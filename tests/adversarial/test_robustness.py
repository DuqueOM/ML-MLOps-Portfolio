"""Adversarial and robustness tests for all 3 ML services.

Tests edge cases, malformed inputs, boundary conditions, and adversarial
payloads that could cause unexpected behavior in production.

Uses self-contained Pydantic schemas that mirror the actual API schemas
to avoid cross-project import issues.
"""

from __future__ import annotations

import math
from typing import Optional

import pytest
from pydantic import BaseModel, Field, field_validator

# ===================================================================
# Mirror schemas — these replicate the Pydantic validation rules from
# each project's fastapi_app.py so we can test input guards in isolation.
# ===================================================================


class CustomerData(BaseModel):
    """Mirror of BankChurn-Predictor/app/fastapi_app.py::CustomerData"""

    CreditScore: int = Field(..., ge=300, le=850)
    Geography: str
    Gender: str
    Age: int = Field(..., ge=0, le=120)
    Tenure: int = Field(..., ge=0, le=50)
    Balance: float = Field(..., ge=0)
    NumOfProducts: int = Field(..., ge=0, le=10)
    HasCrCard: int = Field(..., ge=0, le=1)
    IsActiveMember: int = Field(..., ge=0, le=1)
    EstimatedSalary: float = Field(..., ge=0)

    @field_validator("Balance", "EstimatedSalary", mode="before")
    @classmethod
    def reject_nan_inf(cls, v):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            raise ValueError("NaN and Inf are not allowed")
        return v


class VehicleFeatures(BaseModel):
    """Mirror of CarVision-Market-Intelligence/app/fastapi_app.py::VehicleFeatures"""

    model_year: int = Field(..., ge=1990, le=2030)
    model: str = Field(...)
    condition: Optional[str] = "good"
    cylinders: Optional[float] = 4
    fuel: Optional[str] = "gas"
    odometer: Optional[float] = Field(default=0, ge=0)
    transmission: Optional[str] = "automatic"
    drive: Optional[str] = "fwd"
    type: Optional[str] = "sedan"
    paint_color: Optional[str] = "white"


class TextInput(BaseModel):
    """Mirror of NLPInsight-Analyzer/app/fastapi_app.py::TextInput"""

    text: str = Field(..., min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


# ---------------------------------------------------------------------------
# BankChurn adversarial payloads
# ---------------------------------------------------------------------------

BANKCHURN_VALID = {
    "CreditScore": 650,
    "Geography": "France",
    "Gender": "Female",
    "Age": 40,
    "Tenure": 5,
    "Balance": 60000.0,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 50000.0,
}


class TestBankChurnRobustness:
    """Edge-case and adversarial inputs for BankChurn API schema."""

    def test_valid_payload_accepted(self):
        obj = CustomerData(**BANKCHURN_VALID)
        assert obj.CreditScore == 650

    def test_missing_required_field(self):
        payload = {k: v for k, v in BANKCHURN_VALID.items() if k != "CreditScore"}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_negative_age(self):
        payload = {**BANKCHURN_VALID, "Age": -5}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_extreme_credit_score(self):
        payload = {**BANKCHURN_VALID, "CreditScore": 999999}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_credit_score_below_min(self):
        payload = {**BANKCHURN_VALID, "CreditScore": 100}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_string_in_numeric_field(self):
        payload = {**BANKCHURN_VALID, "Balance": "not_a_number"}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_nan_value_rejected(self):
        payload = {**BANKCHURN_VALID, "Balance": float("nan")}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_infinity_value_rejected(self):
        payload = {**BANKCHURN_VALID, "EstimatedSalary": float("inf")}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_negative_infinity_rejected(self):
        payload = {**BANKCHURN_VALID, "Balance": float("-inf")}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_sql_injection_in_string_field(self):
        payload = {**BANKCHURN_VALID, "Geography": "'; DROP TABLE users; --"}
        obj = CustomerData(**payload)
        assert isinstance(obj.Geography, str)

    def test_xss_payload_in_string_field(self):
        payload = {**BANKCHURN_VALID, "Geography": "<script>alert('xss')</script>"}
        obj = CustomerData(**payload)
        assert isinstance(obj.Geography, str)

    def test_zero_values_boundary(self):
        payload = {
            **BANKCHURN_VALID,
            "CreditScore": 300,
            "Age": 0,
            "Tenure": 0,
            "Balance": 0,
            "NumOfProducts": 0,
            "HasCrCard": 0,
            "IsActiveMember": 0,
            "EstimatedSalary": 0,
        }
        obj = CustomerData(**payload)
        assert obj.Age == 0

    def test_max_values_boundary(self):
        payload = {
            **BANKCHURN_VALID,
            "CreditScore": 850,
            "Age": 120,
            "Tenure": 50,
            "NumOfProducts": 10,
            "HasCrCard": 1,
            "IsActiveMember": 1,
        }
        obj = CustomerData(**payload)
        assert obj.CreditScore == 850

    def test_unicode_in_string_field(self):
        payload = {**BANKCHURN_VALID, "Geography": "日本語テスト"}
        obj = CustomerData(**payload)
        assert isinstance(obj.Geography, str)

    def test_very_long_string(self):
        payload = {**BANKCHURN_VALID, "Geography": "A" * 100000}
        # Pydantic accepts any string length; API may truncate
        obj = CustomerData(**payload)
        assert len(obj.Geography) == 100000

    def test_negative_balance_rejected(self):
        payload = {**BANKCHURN_VALID, "Balance": -1000}
        with pytest.raises(Exception):
            CustomerData(**payload)

    def test_has_crcard_out_of_range(self):
        payload = {**BANKCHURN_VALID, "HasCrCard": 2}
        with pytest.raises(Exception):
            CustomerData(**payload)


# ---------------------------------------------------------------------------
# CarVision adversarial payloads
# ---------------------------------------------------------------------------

CARVISION_VALID = {
    "model_year": 2020,
    "model": "camry",
    "condition": "good",
    "cylinders": 4,
    "fuel": "gas",
    "odometer": 50000.0,
    "transmission": "automatic",
    "drive": "fwd",
    "type": "sedan",
    "paint_color": "white",
}


class TestCarVisionRobustness:
    """Edge-case and adversarial inputs for CarVision API schema."""

    def test_valid_payload_accepted(self):
        obj = VehicleFeatures(**CARVISION_VALID)
        assert obj.model_year == 2020

    def test_future_model_year_rejected(self):
        payload = {**CARVISION_VALID, "model_year": 2099}
        with pytest.raises(Exception):
            VehicleFeatures(**payload)

    def test_ancient_model_year_rejected(self):
        payload = {**CARVISION_VALID, "model_year": 1800}
        with pytest.raises(Exception):
            VehicleFeatures(**payload)

    def test_negative_odometer_rejected(self):
        payload = {**CARVISION_VALID, "odometer": -100}
        with pytest.raises(Exception):
            VehicleFeatures(**payload)

    def test_extreme_odometer_accepted(self):
        payload = {**CARVISION_VALID, "odometer": 99999999}
        obj = VehicleFeatures(**payload)
        assert obj.odometer == 99999999

    def test_boundary_model_year_min(self):
        payload = {**CARVISION_VALID, "model_year": 1990}
        obj = VehicleFeatures(**payload)
        assert obj.model_year == 1990

    def test_boundary_model_year_max(self):
        payload = {**CARVISION_VALID, "model_year": 2030}
        obj = VehicleFeatures(**payload)
        assert obj.model_year == 2030

    def test_string_in_numeric_field_rejected(self):
        payload = {**CARVISION_VALID, "model_year": "not_a_year"}
        with pytest.raises(Exception):
            VehicleFeatures(**payload)

    def test_sql_injection_model_field(self):
        payload = {**CARVISION_VALID, "model": "'; DROP TABLE cars; --"}
        obj = VehicleFeatures(**payload)
        assert isinstance(obj.model, str)

    def test_zero_odometer(self):
        payload = {**CARVISION_VALID, "odometer": 0}
        obj = VehicleFeatures(**payload)
        assert obj.odometer == 0

    def test_missing_optional_fields(self):
        payload = {"model_year": 2020, "model": "camry"}
        obj = VehicleFeatures(**payload)
        assert obj.condition == "good"
        assert obj.cylinders == 4


# ---------------------------------------------------------------------------
# NLPInsight adversarial payloads
# ---------------------------------------------------------------------------


class TestNLPInsightRobustness:
    """Edge-case and adversarial inputs for NLPInsight API schema."""

    def test_valid_text_accepted(self):
        obj = TextInput(text="The company reported strong earnings growth.")
        assert "earnings" in obj.text

    def test_empty_text_rejected(self):
        with pytest.raises(Exception):
            TextInput(text="")

    def test_whitespace_only_rejected(self):
        with pytest.raises(Exception):
            TextInput(text="   \t\n   ")

    def test_very_long_text_rejected(self):
        long_text = "word " * 1001  # ~5005 chars
        with pytest.raises(Exception):
            TextInput(text=long_text)

    def test_text_at_max_boundary(self):
        text = "a" * 5000
        obj = TextInput(text=text)
        assert len(obj.text) == 5000

    def test_text_at_min_boundary(self):
        obj = TextInput(text="a")
        assert obj.text == "a"

    def test_unicode_text(self):
        obj = TextInput(text="企業の収益は増加した。市場は好調だ。")
        assert isinstance(obj.text, str)

    def test_emoji_text(self):
        obj = TextInput(text="Stock is going up! 🚀📈 Great earnings!")
        assert "🚀" in obj.text

    def test_html_injection_stored_safely(self):
        obj = TextInput(text="<script>alert('xss')</script> Market is up")
        assert "<script>" in obj.text

    def test_special_characters(self):
        obj = TextInput(text="Revenue $1.2B (+15%) vs. estimate of $1.1B; P/E = 25.3x")
        assert "$1.2B" in obj.text

    def test_null_bytes(self):
        try:
            TextInput(text="Market is up\x00hidden text")
        except Exception:
            pass  # Rejection of null bytes is acceptable

    def test_repeated_single_char(self):
        obj = TextInput(text="a" * 100)
        assert len(obj.text) == 100

    def test_mixed_languages(self):
        obj = TextInput(text="The Aktienmarkt показал strong рост in Q4 2025")
        assert isinstance(obj.text, str)

    def test_newlines_preserved(self):
        obj = TextInput(text="Line one.\nLine two.\nLine three.")
        assert "\n" in obj.text

    def test_tabs_preserved(self):
        obj = TextInput(text="Col1\tCol2\tCol3")
        assert "\t" in obj.text
