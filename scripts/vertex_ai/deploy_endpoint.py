#!/usr/bin/env python3
"""
Deploy, test, and manage BankChurn Vertex AI Endpoint (GCP).

Usage:
    python scripts/vertex_ai/deploy_endpoint.py            # Deploy + test
    python scripts/vertex_ai/deploy_endpoint.py test        # Test existing endpoint
    python scripts/vertex_ai/deploy_endpoint.py delete      # Delete endpoint (stop charges)
    python scripts/vertex_ai/deploy_endpoint.py upload      # Upload model to GCS only
    python scripts/vertex_ai/deploy_endpoint.py status      # Check endpoint status

Prerequisites:
    pip install google-cloud-aiplatform
    gcloud auth application-default login
    export GCP_PROJECT=ml-portfolio-duque-om-202602
    export GCP_REGION=us-central1

Cost warning:
    n1-standard-2 costs ~$0.095/hr (~$2.28/day).
    ALWAYS delete the endpoint after demos.

References:
    https://cloud.google.com/vertex-ai/docs/predictions/deploy-model-api
    https://cloud.google.com/vertex-ai/docs/predictions/custom-prediction-routines
"""

import json
import os
import sys
from pathlib import Path

ENDPOINT_DISPLAY_NAME = "bankchurn-endpoint"
MODEL_DISPLAY_NAME = "bankchurn-model"
MACHINE_TYPE = "n1-standard-2"
GCS_BUCKET = "ml-portfolio-duque-om-202602-ml-models-production"
GCS_PREFIX = "vertex-ai/bankchurn"
GCP_PROJECT = os.environ.get("GCP_PROJECT", "ml-portfolio-duque-om-202602")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Vertex AI sklearn serving container
SKLEARN_CONTAINER = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"


def init_vertex_ai():
    """Initialize Vertex AI SDK."""
    from google.cloud import aiplatform

    aiplatform.init(project=GCP_PROJECT, location=GCP_REGION)
    return aiplatform


def upload_model_to_gcs():
    """Upload model.joblib to GCS for Vertex AI."""
    from google.cloud import storage

    model_path = PROJECT_ROOT / "BankChurn-Predictor" / "models" / "model.joblib"
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        sys.exit(1)

    client = storage.Client(project=GCP_PROJECT)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(f"{GCS_PREFIX}/model.joblib")
    blob.upload_from_filename(str(model_path))

    gcs_uri = f"gs://{GCS_BUCKET}/{GCS_PREFIX}"
    print(f"✅ Model uploaded to {gcs_uri}/model.joblib")
    return gcs_uri


def deploy(aiplatform, gcs_model_uri):
    """Upload model to Vertex AI Model Registry and deploy to endpoint."""

    # Upload model to Vertex AI
    print(f"📦 Uploading model to Vertex AI Registry: {MODEL_DISPLAY_NAME}")
    model = aiplatform.Model.upload(
        display_name=MODEL_DISPLAY_NAME,
        artifact_uri=gcs_model_uri,
        serving_container_image_uri=SKLEARN_CONTAINER,
        serving_container_health_route="/v1/models/default",
        serving_container_predict_route="/v1/models/default:predict",
    )
    print(f"✅ Model registered: {model.resource_name}")

    # Create endpoint
    print(f"🔧 Creating endpoint: {ENDPOINT_DISPLAY_NAME}")
    endpoint = aiplatform.Endpoint.create(
        display_name=ENDPOINT_DISPLAY_NAME,
    )
    print(f"✅ Endpoint created: {endpoint.resource_name}")

    # Deploy model to endpoint
    print("🚀 Deploying model to endpoint (this takes ~5-10 minutes)...")
    model.deploy(
        endpoint=endpoint,
        machine_type=MACHINE_TYPE,
        min_replica_count=1,
        max_replica_count=1,
        traffic_percentage=100,
        deploy_request_timeout=600,
    )
    print(f"✅ Model deployed to endpoint: {endpoint.resource_name}")
    return endpoint


def test_endpoint(aiplatform):
    """Test existing endpoint with a sample prediction."""
    endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"',
    )
    if not endpoints:
        print(f"❌ Endpoint '{ENDPOINT_DISPLAY_NAME}' not found.")
        sys.exit(1)

    endpoint = endpoints[0]
    print(f"\n🧪 Testing endpoint: {endpoint.display_name}")

    test_instance = {
        "CreditScore": 650,
        "Geography": "France",
        "Gender": "Male",
        "Age": 42,
        "Tenure": 2,
        "Balance": 10000.0,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 0,
        "EstimatedSalary": 45000.0,
    }

    print(f"   Payload: {json.dumps(test_instance)}")
    prediction = endpoint.predict(instances=[test_instance])

    print(f"   Response: {prediction.predictions}")
    print("✅ Endpoint test PASSED")
    return prediction


def check_status(aiplatform):
    """Check current endpoint status."""
    endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"',
    )
    if not endpoints:
        print(f"📊 Endpoint '{ENDPOINT_DISPLAY_NAME}' does not exist.")
        return None

    endpoint = endpoints[0]
    print(f"📊 Endpoint: {endpoint.display_name}")
    print(f"   Resource: {endpoint.resource_name}")
    print(f"   Deployed models: {len(endpoint.gca_resource.deployed_models)}")
    for dm in endpoint.gca_resource.deployed_models:
        print(f"   - Model: {dm.model}")
        print(f"     Machine: {dm.dedicated_resources.machine_spec.machine_type}")
        print(f"     Replicas: {dm.dedicated_resources.min_replica_count}")
    print("   💰 Cost: ~$0.095/hr — delete when done!")
    return endpoint


def delete_endpoint(aiplatform):
    """Delete endpoint and model to stop charges."""
    print("🗑️  Deleting Vertex AI resources...")

    # Delete endpoints
    endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"',
    )
    for endpoint in endpoints:
        print(f"   Undeploying models from: {endpoint.display_name}")
        endpoint.undeploy_all()
        endpoint.delete()
        print(f"   ✅ Endpoint deleted: {endpoint.display_name}")

    # Delete models
    models = aiplatform.Model.list(
        filter=f'display_name="{MODEL_DISPLAY_NAME}"',
    )
    for model in models:
        model.delete()
        print(f"   ✅ Model deleted: {model.display_name}")

    print("✅ All Vertex AI resources deleted — no more charges.")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "deploy"

    if action == "upload":
        upload_model_to_gcs()

    elif action == "test":
        aip = init_vertex_ai()
        test_endpoint(aip)

    elif action == "delete":
        aip = init_vertex_ai()
        delete_endpoint(aip)

    elif action == "status":
        aip = init_vertex_ai()
        check_status(aip)

    elif action == "deploy":
        aip = init_vertex_ai()
        gcs_uri = upload_model_to_gcs()
        deploy(aip, gcs_uri)
        test_endpoint(aip)
        print("\n⚠️  REMINDER: Delete endpoint when done:")
        print("   python scripts/vertex_ai/deploy_endpoint.py delete")

    else:
        print(f"Unknown action: {action}")
        print("Usage: deploy | test | delete | upload | status")
        sys.exit(1)


if __name__ == "__main__":
    main()
