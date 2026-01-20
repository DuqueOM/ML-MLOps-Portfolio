#!/usr/bin/env python3
"""
MLflow Model Registry automation script.

Automates:
- Model registration
- Version promotion (Staging -> Production)
- Model archival
- Metadata management
"""

import argparse
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import mlflow
    from mlflow.tracking import MlflowClient

    MLFLOW_AVAILABLE = True
except ImportError:
    logger.error("MLflow not available. Install with: pip install mlflow")
    MLFLOW_AVAILABLE = False


class MLflowRegistryManager:
    """Manage MLflow Model Registry operations."""

    def __init__(self, tracking_uri: str = "file:./mlruns"):
        """Initialize registry manager."""
        if not MLFLOW_AVAILABLE:
            raise ImportError("MLflow is required")

        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
        logger.info(f"MLflow tracking URI: {tracking_uri}")

    def register_model(self, run_id: str, model_name: str, artifact_path: str = "model") -> str:
        """Register model from run.

        Parameters
        ----------
        run_id : str
            MLflow run ID
        model_name : str
            Name for registered model
        artifact_path : str
            Path to model artifact in run

        Returns
        -------
        str
            Model version
        """
        model_uri = f"runs:/{run_id}/{artifact_path}"

        try:
            result = mlflow.register_model(model_uri, model_name)
            version = result.version
            logger.info(f"✅ Registered {model_name} version {version}")
            return version
        except Exception as e:
            logger.error(f"❌ Registration failed: {e}")
            raise

    def promote_to_staging(self, model_name: str, version: str):
        """Promote model version to Staging."""
        try:
            self.client.transition_model_version_stage(name=model_name, version=version, stage="Staging")
            logger.info(f"✅ Promoted {model_name} v{version} to Staging")
        except Exception as e:
            logger.error(f"❌ Promotion to Staging failed: {e}")
            raise

    def promote_to_production(self, model_name: str, version: str):
        """Promote model version to Production."""
        try:
            # Archive current production models
            self._archive_production_models(model_name)

            # Promote to production
            self.client.transition_model_version_stage(name=model_name, version=version, stage="Production")
            logger.info(f"✅ Promoted {model_name} v{version} to Production")
        except Exception as e:
            logger.error(f"❌ Promotion to Production failed: {e}")
            raise

    def _archive_production_models(self, model_name: str):
        """Archive current production models."""
        try:
            versions = self.client.search_model_versions(f"name='{model_name}'")
            for mv in versions:
                if mv.current_stage == "Production":
                    self.client.transition_model_version_stage(name=model_name, version=mv.version, stage="Archived")
                    logger.info(f"📦 Archived {model_name} v{mv.version}")
        except Exception as e:
            logger.warning(f"⚠️  Archive warning: {e}")

    def get_latest_version(self, model_name: str, stage: Optional[str] = None) -> Optional[str]:
        """Get latest model version.

        Parameters
        ----------
        model_name : str
            Model name
        stage : str, optional
            Stage filter (Staging, Production, etc.)

        Returns
        -------
        str or None
            Latest version number
        """
        try:
            if stage:
                versions = self.client.get_latest_versions(model_name, stages=[stage])
            else:
                versions = self.client.search_model_versions(f"name='{model_name}'")

            if versions:
                latest = max(versions, key=lambda v: int(v.version))
                return latest.version
            return None
        except Exception as e:
            logger.error(f"❌ Error getting latest version: {e}")
            return None

    def add_model_metadata(self, model_name: str, version: str, metadata: dict):
        """Add metadata tags to model version."""
        try:
            for key, value in metadata.items():
                self.client.set_model_version_tag(model_name, version, key, str(value))
            logger.info(f"✅ Added metadata to {model_name} v{version}")
        except Exception as e:
            logger.error(f"❌ Metadata update failed: {e}")
            raise


def main():
    """CLI for MLflow registry automation."""
    parser = argparse.ArgumentParser(description="MLflow Model Registry Automation")
    parser.add_argument("--tracking-uri", default="file:./mlruns", help="MLflow tracking URI")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Register command
    register_parser = subparsers.add_parser("register", help="Register model from run")
    register_parser.add_argument("--run-id", required=True, help="MLflow run ID")
    register_parser.add_argument("--name", required=True, help="Model name")
    register_parser.add_argument("--artifact-path", default="model", help="Artifact path")

    # Promote command
    promote_parser = subparsers.add_parser("promote", help="Promote model version")
    promote_parser.add_argument("--name", required=True, help="Model name")
    promote_parser.add_argument("--version", required=True, help="Model version")
    promote_parser.add_argument("--stage", required=True, choices=["Staging", "Production"])

    # Latest command
    latest_parser = subparsers.add_parser("latest", help="Get latest version")
    latest_parser.add_argument("--name", required=True, help="Model name")
    latest_parser.add_argument("--stage", help="Stage filter")

    args = parser.parse_args()

    if not MLFLOW_AVAILABLE:
        logger.error("MLflow not available")
        return 1

    try:
        manager = MLflowRegistryManager(args.tracking_uri)

        if args.command == "register":
            version = manager.register_model(args.run_id, args.name, args.artifact_path)
            print(f"Registered version: {version}")

        elif args.command == "promote":
            if args.stage == "Staging":
                manager.promote_to_staging(args.name, args.version)
            elif args.stage == "Production":
                manager.promote_to_production(args.name, args.version)

        elif args.command == "latest":
            version = manager.get_latest_version(args.name, args.stage)
            if version:
                print(f"Latest version: {version}")
            else:
                print("No versions found")

        else:
            parser.print_help()
            return 1

        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
