# ADR Quick Reference for ML Inference Debugging

## ADR-001: CPU-Only HPA
- **Problem**: Memory-based HPA never scales down for ML pods
- **Why**: Model loaded in RAM = fixed memory footprint (~300Mi BankChurn, ~550Mi NLPInsight)
- **Formula**: `ceil(replicas × usage/target)` with constant memory never decreases
- **Fix**: Remove memory metric from HPA, use CPU-only scaling (70% threshold)
- **Verification**: Watch HPA scale 3→2→1 after load drops (~8 minutes)

## ADR-005: Compatible Release Pinning
- **Problem**: numpy 2.x silently corrupts joblib-serialized sklearn models
- **Why**: dtype layout changed in numpy 2.0, no error raised, just wrong predictions
- **Fix**: Use `~=` pinning for ALL dependencies (blocks major/minor, allows patches)
- **Check**: `pip list | grep numpy` — must be <2.0

## ADR-010: SHAP KernelExplainer
- **Problem**: SHAP returns all-zero values in production
- **Why**: (1) shap missing from prod requirements, (2) TreeExplainer incompatible with StackingClassifier
- **Fix**: Use `KernelExplainer` with `predict_proba_wrapper` in original 10-feature space
- **Check**: Verify SHAP values sum to non-zero for any prediction

## ADR-014: Single-Worker Pod
- **Problem**: 81% error rate under 100 concurrent users
- **Why**: `uvicorn --workers N` shares CPU budget under K8s, causes thrashing not parallelism
- **Fix**: Single-worker uvicorn (workers=1) + HPA horizontal scaling
- **Check**: Verify `--workers 1` or no --workers flag in Dockerfile CMD

## ADR-015: Async Inference with ThreadPoolExecutor
- **Problem**: Synchronous inference blocks the event loop
- **Why**: sklearn/XGBoost/LightGBM C extensions release GIL during computation
- **Fix**: `asyncio.run_in_executor` + `ThreadPoolExecutor(4)` — real parallelism with shared model memory
- **Why not ProcessPoolExecutor**: N × model memory per process, IPC overhead, fork-after-load risks
- **Result**: ~40 req/s per pod on 1 CPU

## ADR-016: GCP/AWS Performance Parity
- **Problem**: GCP 2-3× slower than AWS under load
- **Why**: e2-medium (shared, AMD EPYC 2.2GHz) vs t3.medium (burst, Intel Xeon 2.5-3.1GHz)
- **Decision**: Documented as FinOps trade-off ($24/mo vs $145/mo), both meet <500ms SLA
