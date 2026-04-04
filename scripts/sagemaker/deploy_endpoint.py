#!/usr/bin/env python3
"""
Deploy, test, and manage BankChurn SageMaker Endpoint.

Usage:
    python scripts/sagemaker/deploy_endpoint.py          # Deploy + test
    python scripts/sagemaker/deploy_endpoint.py test      # Test existing endpoint
    python scripts/sagemaker/deploy_endpoint.py delete    # Delete endpoint (stop charges)
    python scripts/sagemaker/deploy_endpoint.py package   # Package model.tar.gz only
    python scripts/sagemaker/deploy_endpoint.py status    # Check endpoint status

Prerequisites:
    pip install sagemaker boto3
    export AWS_PROFILE=ml-portfolio
    # IAM role with SageMaker permissions (see setup-role.sh)

Cost warning:
    ml.t2.medium costs ~$0.065/hr (~$1.56/day).
    ALWAYS delete the endpoint after demos.
"""

import json
import os
import sys
import tarfile
import tempfile
from pathlib import Path

import boto3

ENDPOINT_NAME = "bankchurn-endpoint"
MODEL_NAME = "bankchurn-model"
INSTANCE_TYPE = "ml.t2.medium"
S3_BUCKET = "ml-portfolio-ml-models-production"
S3_PREFIX = "sagemaker/bankchurn"
AWS_PROFILE = os.environ.get("AWS_PROFILE", "ml-portfolio")
REGION = os.environ.get("AWS_REGION", "us-east-1")
FRAMEWORK_VERSION = "1.2-1"

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_session():
    """Create boto3 session with configured profile."""
    return boto3.Session(profile_name=AWS_PROFILE, region_name=REGION)


def get_sagemaker_role(session):
    """Retrieve SageMaker execution role ARN."""
    iam = session.client("iam")
    try:
        role = iam.get_role(RoleName="SageMakerExecutionRole")
        return role["Role"]["Arn"]
    except iam.exceptions.NoSuchEntityException:
        print("❌ SageMaker execution role not found.")
        print("   Run: bash scripts/sagemaker/setup-role.sh")
        sys.exit(1)


def package_model():
    """Package model.joblib + inference.py into model.tar.gz."""
    model_path = PROJECT_ROOT / "BankChurn-Predictor" / "models" / "model.joblib"
    inference_path = PROJECT_ROOT / "scripts" / "sagemaker" / "inference.py"

    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        sys.exit(1)

    output_path = Path(tempfile.mkdtemp()) / "model.tar.gz"

    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(model_path, arcname="model.joblib")
        tar.add(inference_path, arcname="inference.py")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"📦 Packaged model.tar.gz ({size_mb:.1f} MB): {output_path}")
    return output_path


def upload_to_s3(session, local_path):
    """Upload model.tar.gz to S3."""
    s3 = session.client("s3")
    s3_key = f"{S3_PREFIX}/model.tar.gz"

    print(f"⬆️  Uploading to s3://{S3_BUCKET}/{s3_key} ...")
    s3.upload_file(str(local_path), S3_BUCKET, s3_key)
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
    print(f"✅ Uploaded: {s3_uri}")
    return s3_uri


def deploy(session, s3_uri, role_arn):
    """Create SageMaker model + endpoint config + endpoint."""
    sm = session.client("sagemaker")

    # Get the sklearn container image URI
    account_map = {
        "us-east-1": "683313688378",
        "us-west-2": "246618743249",
        "eu-west-1": "141502667606",
    }
    account = account_map.get(REGION, "683313688378")
    image_uri = f"{account}.dkr.ecr.{REGION}.amazonaws.com/" f"sagemaker-scikit-learn:{FRAMEWORK_VERSION}"

    # Clean up existing resources if any
    _cleanup_existing(sm)

    # Create model
    print(f"🔧 Creating model: {MODEL_NAME}")
    sm.create_model(
        ModelName=MODEL_NAME,
        PrimaryContainer={
            "Image": image_uri,
            "ModelDataUrl": s3_uri,
            "Environment": {
                "SAGEMAKER_PROGRAM": "inference.py",
                "SAGEMAKER_SUBMIT_DIRECTORY": s3_uri,
            },
        },
        ExecutionRoleArn=role_arn,
    )

    # Create endpoint config
    config_name = f"{ENDPOINT_NAME}-config"
    print(f"⚙️  Creating endpoint config: {config_name}")
    sm.create_endpoint_config(
        EndpointConfigName=config_name,
        ProductionVariants=[
            {
                "VariantName": "primary",
                "ModelName": MODEL_NAME,
                "InstanceType": INSTANCE_TYPE,
                "InitialInstanceCount": 1,
                "InitialVariantWeight": 1.0,
            }
        ],
    )

    # Create endpoint
    print(f"🚀 Creating endpoint: {ENDPOINT_NAME} (this takes ~5 minutes)...")
    sm.create_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=config_name,
    )

    # Wait for endpoint
    print("⏳ Waiting for endpoint to be InService...")
    waiter = sm.get_waiter("endpoint_in_service")
    waiter.wait(
        EndpointName=ENDPOINT_NAME,
        WaiterConfig={"Delay": 30, "MaxAttempts": 30},
    )
    print(f"✅ Endpoint {ENDPOINT_NAME} is InService!")


def _cleanup_existing(sm):
    """Delete existing endpoint/config/model if they exist."""
    try:
        sm.describe_endpoint(EndpointName=ENDPOINT_NAME)
        print(f"🗑️  Deleting existing endpoint: {ENDPOINT_NAME}")
        sm.delete_endpoint(EndpointName=ENDPOINT_NAME)
        _wait_for_deletion(sm)
    except sm.exceptions.ClientError:
        pass

    config_name = f"{ENDPOINT_NAME}-config"
    try:
        sm.delete_endpoint_config(EndpointConfigName=config_name)
    except sm.exceptions.ClientError:
        pass

    try:
        sm.delete_model(ModelName=MODEL_NAME)
    except sm.exceptions.ClientError:
        pass


def _wait_for_deletion(sm):
    """Wait for endpoint to be fully deleted."""
    import time

    for _ in range(60):
        try:
            status = sm.describe_endpoint(EndpointName=ENDPOINT_NAME)
            state = status["EndpointStatus"]
            if state == "Deleting":
                time.sleep(10)
                continue
        except sm.exceptions.ClientError:
            return
    print("⚠️  Endpoint deletion timed out, proceeding anyway...")


def test_endpoint(session):
    """Invoke endpoint with a test payload."""
    runtime = session.client("sagemaker-runtime")

    payload = json.dumps(
        {
            "CreditScore": 650,
            "Geography": "France",
            "Gender": "Male",
            "Age": 42,
            "Tenure": 2,
            "Balance": 10000,
            "NumOfProducts": 1,
            "HasCrCard": 1,
            "IsActiveMember": 0,
            "EstimatedSalary": 45000,
        }
    )

    print(f"\n🧪 Testing endpoint: {ENDPOINT_NAME}")
    print(f"   Payload: {payload}")

    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=payload,
    )

    result = json.loads(response["Body"].read().decode())
    print(f"   Response: {json.dumps(result, indent=2)}")

    assert "churn_probability" in result, "Missing churn_probability in response"
    assert "prediction" in result, "Missing prediction in response"
    assert 0 <= result["churn_probability"] <= 1, "churn_probability out of range"

    print("✅ Endpoint test PASSED")
    return result


def check_status(session):
    """Check current endpoint status."""
    sm = session.client("sagemaker")
    try:
        response = sm.describe_endpoint(EndpointName=ENDPOINT_NAME)
        status = response["EndpointStatus"]
        print(f"📊 Endpoint: {ENDPOINT_NAME}")
        print(f"   Status: {status}")
        print(f"   Instance: {INSTANCE_TYPE}")
        if status == "InService":
            print("   💰 Cost: ~$0.065/hr — delete when done!")
        return status
    except sm.exceptions.ClientError:
        print(f"📊 Endpoint {ENDPOINT_NAME} does not exist.")
        return None


def delete_endpoint(session):
    """Delete endpoint, config, and model to stop charges."""
    sm = session.client("sagemaker")

    print(f"🗑️  Deleting SageMaker resources for {ENDPOINT_NAME}...")

    try:
        sm.delete_endpoint(EndpointName=ENDPOINT_NAME)
        print(f"   ✅ Endpoint deleted: {ENDPOINT_NAME}")
    except sm.exceptions.ClientError as e:
        print(f"   ⚠️  Endpoint: {e}")

    config_name = f"{ENDPOINT_NAME}-config"
    try:
        sm.delete_endpoint_config(EndpointConfigName=config_name)
        print(f"   ✅ Config deleted: {config_name}")
    except sm.exceptions.ClientError as e:
        print(f"   ⚠️  Config: {e}")

    try:
        sm.delete_model(ModelName=MODEL_NAME)
        print(f"   ✅ Model deleted: {MODEL_NAME}")
    except sm.exceptions.ClientError as e:
        print(f"   ⚠️  Model: {e}")

    print("✅ All SageMaker resources deleted — no more charges.")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "deploy"
    session = get_session()

    if action == "package":
        package_model()

    elif action == "test":
        test_endpoint(session)

    elif action == "delete":
        delete_endpoint(session)

    elif action == "status":
        check_status(session)

    elif action == "deploy":
        role_arn = get_sagemaker_role(session)
        tar_path = package_model()
        s3_uri = upload_to_s3(session, tar_path)
        deploy(session, s3_uri, role_arn)
        test_endpoint(session)
        print("\n⚠️  REMINDER: Delete endpoint when done:")
        print("   python scripts/sagemaker/deploy_endpoint.py delete")

    else:
        print(f"Unknown action: {action}")
        print("Usage: deploy | test | delete | package | status")
        sys.exit(1)


if __name__ == "__main__":
    main()
