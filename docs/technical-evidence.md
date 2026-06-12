# Technical Evidence

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Reviewer evidence</span>

# Technical evidence without the wall of links

This page is the short version. It is designed for a reviewer who wants to know
what was actually built without being dropped into every ADR, API reference and
deployment note at once.

Use it as a map: start with the summary, choose one review path, and open the
deep dive only if you want the full technical archive.

<div class="portfolio-actions" markdown="1">
[Read incident writeup](projects/bankchurn-debugging.md){ .portfolio-button .portfolio-button--primary }
[Open deep dive index](technical-deep-dive.md){ .portfolio-button }
[Check current status](DEPLOYMENT_EVIDENCE.md){ .portfolio-button }
</div>
</div>

## Visual Evidence Shortcuts

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving path</small>
<h3>Live ML predictions</h3>
<img class="portfolio-evidence-image" src="../media/gifs/ml-predictions.gif" alt="Animated walkthrough of ML prediction APIs">
<p>FastAPI prediction paths for the portfolio services, shown as a short visual
review instead of another long code block.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Observability path</small>
<h3>Monitoring under load</h3>
<img class="portfolio-evidence-image" src="../media/gifs/monitoring-observability.gif" alt="Animated walkthrough of monitoring and observability evidence">
<p>Grafana, Prometheus, Locust and MLflow evidence grouped for reviewers who
want runtime behavior, not only architecture claims.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cloud path</small>
<h3>GKE and EKS parity</h3>
<img class="portfolio-evidence-image" src="../media/gifs/multicloud-parity.gif" alt="Animated walkthrough of GKE and EKS multi-cloud evidence">
<p>Side-by-side cloud evidence showing that the portfolio was exercised across
Google Cloud and AWS Kubernetes environments.</p>
</div>
</div>

## Green Checks And Runtime Evidence

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>CI proof</small>
<h3>GitHub Actions completed</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/cicd/46-workflow-completado.png" alt="GitHub Actions workflow completed successfully">
<p>Visible green checks reduce the time a technical reviewer spends wondering
whether the 395+ tests are only a claim.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Smoke proof</small>
<h3>API health checks passed</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/terminal/23-health-checks-apis.png" alt="Terminal showing API health checks passing">
<p>Health-check screenshots show that the APIs were exercised as running
services, not only described in documentation.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Model lifecycle</small>
<h3>MLflow experiment tracking</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/monitoring/39-mlflow-experiments.png" alt="MLflow experiments screenshot">
<p>MLflow evidence makes model tracking tangible for reviewers who want to see
experiment and model registry habits.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Observability</small>
<h3>Grafana and load testing</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/monitoring/38c-load-test-results.png" alt="Load test results screenshot">
<p>The load-test evidence connects observability claims to measured runtime
behavior.</p>
</div>
</div>

## Key Engineering Decisions

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving</small>
<h3>One worker per pod plus executor</h3>
<p>Kubernetes handles horizontal scaling; the API avoids
<code>uvicorn --workers N</code> inside one pod and keeps the event loop free by
offloading CPU-bound inference work to <code>asyncio.run_in_executor()</code>
and <code>ThreadPoolExecutor</code>.</p>

[ADR-014](decisions/014-single-worker-pod-ml-inference.md){ .portfolio-button }
[ADR-015](decisions/015-async-inference-threadpool.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>Cost control</small>
<h3>Cloud evidence, not always-on waste</h3>
<p>The portfolio preserves deployment proof while pausing live clusters when
the monthly cost is not justified for a public showcase.</p>

[Portfolio status](DEPLOYMENT_EVIDENCE.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>Template extraction</small>
<h3>Lessons became guardrails</h3>
<p>The reusable template turns repeated failure modes into documented defaults,
rules and reviewable workflows.</p>

[Production template](template.md){ .portfolio-button }
</div>
</div>

<style>
#pf-lightbox {
  display: none;
  position: fixed;
  z-index: 9999;
  inset: 0;
  background: rgba(0,0,0,0.85);
  justify-content: center;
  align-items: center;
  cursor: zoom-out;
  padding: 2rem;
}
#pf-lightbox.active { display: flex; }
#pf-lightbox img {
  max-width: 95vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
#pf-lightbox-close {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  color: #fff;
  font-size: 2rem;
  line-height: 1;
  cursor: pointer;
  opacity: 0.8;
}
#pf-lightbox-close:hover { opacity: 1; }
.portfolio-evidence-image { cursor: zoom-in; transition: opacity 0.2s; }
.portfolio-evidence-image:hover { opacity: 0.85; }
</style>

<div id="pf-lightbox" onclick="this.classList.remove('active')">
  <span id="pf-lightbox-close">&times;</span>
  <img id="pf-lightbox-img" src="" alt="">
</div>

<script>
(function() {
  const lb = document.getElementById('pf-lightbox');
  const lbImg = document.getElementById('pf-lightbox-img');
  document.querySelectorAll('.portfolio-evidence-image').forEach(function(img) {
    img.addEventListener('click', function(e) {
      e.preventDefault();
      lbImg.src = img.src;
      lbImg.alt = img.alt;
      lb.classList.add('active');
    });
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') lb.classList.remove('active');
  });
})();
</script>

</div>
