# BankChurn Debugging Deep Dive

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<canvas data-neural-field="editorial" aria-hidden="true"></canvas>
<span class="portfolio-eyebrow">Failure story and engineering judgment</span>

# From 81% API errors to a reliable inference path

This is the strongest debugging story in the portfolio because it shows the
habit I want to bring into an entry-level / junior MLOps team: measure the failure, isolate the
cause, make the smallest meaningful fix, and turn the lesson into reusable
engineering guidance.

<div class="portfolio-actions" markdown="1">
[Back to BankChurn](bankchurn.md){ .portfolio-button .portfolio-button--primary }
[Load test evidence](../load-test-results.md){ .portfolio-button }
[ADR-015](../decisions/015-async-inference-threadpool.md){ .portfolio-button }
</div>
</div>

## Incident Summary

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Symptom</small>
<h3>81% failures under load</h3>
<p>A Locust stress test exposed a high API error rate. From the outside, it
looked like a simple scaling or CPU allocation problem.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Root cause</small>
<h3>Blocked event loop + worker contention</h3>
<p><code>uvicorn --workers N</code> inside one Kubernetes pod shared a single
CPU budget, while synchronous ML inference blocked FastAPI's async serving path
under concurrency.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Fix</small>
<h3>ThreadPoolExecutor</h3>
<p>The API moved to one worker per pod and the CPU-bound prediction work was
placed behind <code>asyncio.run_in_executor()</code> with
<code>ThreadPoolExecutor</code>.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Outcome</small>
<h3>Errors removed in validation</h3>
<p>The revised serving pattern was validated with load testing and became a
documented rule for future services.</p>
</div>
</div>

## What I Saw First

The first signal was not a model metric. It was an operating symptom: the API
failed when concurrent users hit the prediction endpoint. That matters because
production ML failures often appear outside the model itself. A model can have a
good AUC and still fail as a service if the serving path is wrong.

The initial question was: **is this a resource problem, a Kubernetes scaling
problem, or an application execution problem?**

## Hypotheses I Had To Separate

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Hypothesis 1</small>
<h3>Add more workers</h3>
<p>This looked tempting, but multiple Uvicorn workers inside one Kubernetes pod
share the same pod CPU budget. That can create contention instead of useful
parallelism.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Hypothesis 2</small>
<h3>Scale with memory</h3>
<p>ML pods have a fixed model memory footprint. Memory stayed high even when
traffic dropped, so memory-based HPA would not scale down cleanly.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Hypothesis 3</small>
<h3>Unblock the event loop</h3>
<p>The evidence pointed to the synchronous prediction call blocking the async
server. That explained why adding resources alone was the wrong first fix.</p>
</div>
</div>

## The Root Cause

The BankChurn model uses a scikit-learn style pipeline and ensemble inference
path. The prediction call is CPU-bound and synchronous. When that call runs
directly inside an async FastAPI endpoint, it blocks the event loop. Under load,
the service spends too much time waiting on inference work and cannot keep
serving new connections reliably. Using <code>uvicorn --workers N</code> inside
the same Kubernetes pod did not solve the issue because the workers still shared
one pod CPU budget and made the HPA signal harder to reason about.

The key lesson was that **async API code does not automatically make CPU-bound
ML inference concurrent**. The serving pattern must intentionally separate
request handling from model computation.

## The Fix

The fix was to keep a single Uvicorn worker per pod and move prediction work
into a thread pool:

```python
loop = asyncio.get_running_loop()
prediction = await loop.run_in_executor(
    app.state.inference_executor,
    predictor.predict,
    request_payload,
)
```

This works for this stack because scikit-learn, XGBoost and LightGBM execute
heavy numerical work in compiled extensions that can release the GIL. The thread
pool lets the event loop keep accepting and coordinating requests while the
model computation runs off the main async path.

## How I Verified It

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Before</small>
<h3>Stress test failure</h3>
<p>The API reached an 81% failure rate under the target load scenario.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>After</small>
<h3>Load test recovery</h3>
<p>The revised serving path removed the observed failure pattern in validation
and preserved a simpler Kubernetes scaling model.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Documentation</small>
<h3>ADR-backed lesson</h3>
<p>The result became part of the portfolio's architecture decisions and later
informed the reusable MLOps template.</p>
</div>
</div>

<div class="portfolio-before-after-chart" markdown="1">
<div class="portfolio-bar-row" markdown="1">
<span>Before: API error rate</span>
<div class="portfolio-bar-track">
<div class="portfolio-bar portfolio-bar--danger" style="width: 81%;">81%</div>
</div>
</div>

<div class="portfolio-bar-row" markdown="1">
<span>After: API error rate</span>
<div class="portfolio-bar-track">
<div class="portfolio-bar portfolio-bar--success" style="width: 2%;">0%</div>
</div>
</div>

<div class="portfolio-bar-row" markdown="1">
<span>CPU request after fix</span>
<div class="portfolio-bar-track">
<div class="portfolio-bar portfolio-bar--neutral" style="width: 50%;">~50% lower</div>
</div>
</div>
</div>

## What This Became In The Template

The important outcome was not only that BankChurn worked. The lesson became a
reusable rule: avoid `uvicorn --workers N` as the default Kubernetes answer for
ML inference, keep one worker per pod, use HPA for horizontal scaling, and move
CPU-bound prediction work away from the async event loop.

That is the difference between a one-time fix and an operating habit. The
portfolio bug became a template guardrail.

## What I Would Improve Next

If I were evolving this service on a real team, I would add distributed tracing
around the prediction path, capture request-level timing by stage, and run a
short scheduled traffic window to keep fresh Grafana/Prometheus evidence. I
would also compare thread pool sizing under different model types instead of
treating one executor configuration as universal.

## Related Evidence

- [Load test results](../load-test-results.md)
- [ADR-014: Single-worker pod ML inference](../decisions/014-single-worker-pod-ml-inference.md)
- [ADR-015: Async inference thread pool](../decisions/015-async-inference-threadpool.md)
- [BankChurn project page](bankchurn.md)
- [Technical evidence overview](../technical-evidence.md)

</div>
