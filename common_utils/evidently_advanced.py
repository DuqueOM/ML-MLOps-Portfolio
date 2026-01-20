"""
Advanced Evidently Integration for ML Monitoring.

Provides enhanced drift detection, model performance monitoring,
and automated alerting capabilities.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

try:
    from evidently import ColumnMapping
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset
    from evidently.metrics import DatasetDriftMetric, DatasetMissingValuesMetric
    from evidently.report import Report
    from evidently.test_preset import DataDriftTestPreset, DataQualityTestPreset
    from evidently.test_suite import TestSuite

    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False
    Report = None  # type: ignore
    TestSuite = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class DriftAlert:
    """Drift alert configuration and result."""

    metric_name: str
    threshold: float
    current_value: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: str


@dataclass
class MonitoringResult:
    """Complete monitoring result with drift, quality, and alerts."""

    dataset_drift: bool
    drift_share: float
    drifted_features: List[str]
    quality_issues: Dict[str, Any]
    alerts: List[DriftAlert]
    report_path: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None


class EvidentlyMonitor:
    """Advanced Evidently monitoring with alerting."""

    def __init__(
        self,
        drift_threshold: float = 0.5,
        missing_threshold: float = 0.1,
        alert_thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize Evidently monitor.

        Parameters
        ----------
        drift_threshold : float
            Threshold for dataset drift (0-1)
        missing_threshold : float
            Threshold for missing values (0-1)
        alert_thresholds : dict, optional
            Custom thresholds for alerts
        """
        if not EVIDENTLY_AVAILABLE:
            raise ImportError("Evidently is not installed. Install with: pip install evidently")

        self.drift_threshold = drift_threshold
        self.missing_threshold = missing_threshold
        self.alert_thresholds = alert_thresholds or {
            "drift_share": 0.3,
            "missing_values": 0.05,
            "target_drift": 0.1,
        }

    def generate_comprehensive_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        target_column: Optional[str] = None,
        numerical_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        output_path: Optional[Path] = None,
    ) -> MonitoringResult:
        """
        Generate comprehensive monitoring report with drift, quality, and alerts.

        Parameters
        ----------
        reference_data : pd.DataFrame
            Reference/training dataset
        current_data : pd.DataFrame
            Current/production dataset
        target_column : str, optional
            Target column name
        numerical_features : list, optional
            List of numerical feature names
        categorical_features : list, optional
            List of categorical feature names
        output_path : Path, optional
            Path to save HTML report

        Returns
        -------
        MonitoringResult
            Complete monitoring result with alerts
        """
        logger.info("Generating comprehensive Evidently report...")

        # Setup column mapping
        column_mapping = ColumnMapping()
        if target_column:
            column_mapping.target = target_column
        if numerical_features:
            column_mapping.numerical_features = numerical_features
        if categorical_features:
            column_mapping.categorical_features = categorical_features

        # Create report with multiple presets
        report = Report(
            metrics=[
                DataDriftPreset(),
                DataQualityPreset(),
                TargetDriftPreset() if target_column else DatasetDriftMetric(),
                DatasetMissingValuesMetric(),
            ]
        )

        # Run report
        report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=column_mapping,
        )

        # Extract metrics
        result_dict = report.as_dict()
        metrics = result_dict.get("metrics", [])

        # Parse drift metrics
        dataset_drift = False
        drift_share = 0.0
        drifted_features = []

        for metric in metrics:
            if metric.get("metric") == "DatasetDriftMetric":
                result = metric.get("result", {})
                dataset_drift = result.get("dataset_drift", False)
                drift_share = result.get("drift_share", 0.0)
                drift_by_columns = result.get("drift_by_columns", {})
                drifted_features = [col for col, info in drift_by_columns.items() if info.get("drift_detected", False)]

        # Parse quality metrics
        quality_issues = {}
        for metric in metrics:
            if metric.get("metric") == "DatasetMissingValuesMetric":
                result = metric.get("result", {})
                quality_issues["missing_values"] = result.get("current", {}).get("share_of_missing_values", 0.0)

        # Generate alerts
        alerts = self._generate_alerts(dataset_drift, drift_share, drifted_features, quality_issues)

        # Save HTML report if path provided
        report_path_str = None
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report.save_html(str(output_path))
            report_path_str = str(output_path)
            logger.info(f"Report saved to {output_path}")

        return MonitoringResult(
            dataset_drift=dataset_drift,
            drift_share=drift_share,
            drifted_features=drifted_features,
            quality_issues=quality_issues,
            alerts=alerts,
            report_path=report_path_str,
        )

    def run_test_suite(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        target_column: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Run Evidently test suite for automated validation.

        Parameters
        ----------
        reference_data : pd.DataFrame
            Reference dataset
        current_data : pd.DataFrame
            Current dataset
        target_column : str, optional
            Target column name
        output_path : Path, optional
            Path to save test results

        Returns
        -------
        dict
            Test results with pass/fail status
        """
        logger.info("Running Evidently test suite...")

        column_mapping = ColumnMapping()
        if target_column:
            column_mapping.target = target_column

        # Create test suite
        test_suite = TestSuite(tests=[DataDriftTestPreset(), DataQualityTestPreset()])

        # Run tests
        test_suite.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=column_mapping,
        )

        # Extract results
        result_dict = test_suite.as_dict()
        tests = result_dict.get("tests", [])

        test_results = {
            "total_tests": len(tests),
            "passed": sum(1 for t in tests if t.get("status") == "SUCCESS"),
            "failed": sum(1 for t in tests if t.get("status") == "FAIL"),
            "tests": tests,
        }

        # Save HTML if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            test_suite.save_html(str(output_path))
            logger.info(f"Test suite saved to {output_path}")

        return test_results

    def _generate_alerts(
        self,
        dataset_drift: bool,
        drift_share: float,
        drifted_features: List[str],
        quality_issues: Dict[str, Any],
    ) -> List[DriftAlert]:
        """Generate alerts based on thresholds."""
        alerts = []
        timestamp = datetime.now().isoformat()

        # Dataset drift alert
        if dataset_drift:
            severity = self._calculate_severity(drift_share, self.alert_thresholds["drift_share"])
            feature_list = ", ".join(drifted_features[:5])
            message = f"Dataset drift detected! {len(drifted_features)} features drifted: {feature_list}"
            alerts.append(
                DriftAlert(
                    metric_name="dataset_drift",
                    threshold=self.drift_threshold,
                    current_value=drift_share,
                    severity=severity,
                    message=message,
                    timestamp=timestamp,
                )
            )

        # Missing values alert
        missing_share = quality_issues.get("missing_values", 0.0)
        if missing_share > self.alert_thresholds["missing_values"]:
            severity = self._calculate_severity(missing_share, self.alert_thresholds["missing_values"])
            alerts.append(
                DriftAlert(
                    metric_name="missing_values",
                    threshold=self.alert_thresholds["missing_values"],
                    current_value=missing_share,
                    severity=severity,
                    message=f"High missing values detected: {missing_share:.2%}",
                    timestamp=timestamp,
                )
            )

        return alerts

    def _calculate_severity(self, value: float, threshold: float) -> str:
        """Calculate alert severity based on value and threshold."""
        ratio = value / threshold if threshold > 0 else 0
        if ratio < 1.0:
            return "low"
        elif ratio < 1.5:
            return "medium"
        elif ratio < 2.0:
            return "high"
        else:
            return "critical"

    def save_alerts(self, alerts: List[DriftAlert], output_path: Path) -> None:
        """Save alerts to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        alerts_dict = [
            {
                "metric_name": alert.metric_name,
                "threshold": alert.threshold,
                "current_value": alert.current_value,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp,
            }
            for alert in alerts
        ]
        with open(output_path, "w") as f:
            json.dump(alerts_dict, f, indent=2)
        logger.info(f"Alerts saved to {output_path}")


def create_monitoring_report(
    reference_csv: str,
    current_csv: str,
    target_column: Optional[str] = None,
    numerical_features: Optional[List[str]] = None,
    categorical_features: Optional[List[str]] = None,
    output_dir: str = "artifacts/monitoring",
) -> MonitoringResult:
    """
    Convenience function to create monitoring report from CSV files.

    Parameters
    ----------
    reference_csv : str
        Path to reference CSV
    current_csv : str
        Path to current CSV
    target_column : str, optional
        Target column name
    numerical_features : list, optional
        Numerical features
    categorical_features : list, optional
        Categorical features
    output_dir : str
        Output directory for reports

    Returns
    -------
    MonitoringResult
        Complete monitoring result
    """
    ref_data = pd.read_csv(reference_csv)
    cur_data = pd.read_csv(current_csv)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    monitor = EvidentlyMonitor()
    result = monitor.generate_comprehensive_report(
        reference_data=ref_data,
        current_data=cur_data,
        target_column=target_column,
        numerical_features=numerical_features,
        categorical_features=categorical_features,
        output_path=output_path / "monitoring_report.html",
    )

    # Save alerts
    if result.alerts:
        monitor.save_alerts(result.alerts, output_path / "alerts.json")

    return result
