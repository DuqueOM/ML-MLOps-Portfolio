"""Tests para mathops — Módulo 01."""

import importlib.util
from pathlib import Path

import pytest

# Agregar path para importar desde solutions

MATHOPS_PATH = Path(__file__).parent.parent / "solutions" / "mathops.py"
_spec = importlib.util.spec_from_file_location("mathops", MATHOPS_PATH)
_mathops = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader is not None
_spec.loader.exec_module(_mathops)

add = _mathops.add
mean = _mathops.mean
multiply = _mathops.multiply
normalize = _mathops.normalize
std = _mathops.std


class TestAdd:
    """Tests para la función add."""

    def test_add_positive_integers(self):
        assert add(2, 3) == 5

    def test_add_negative_integers(self):
        assert add(-1, -2) == -3

    def test_add_mixed_signs(self):
        assert add(-1, 1) == 0

    def test_add_floats(self):
        assert add(1.5, 2.5) == 4.0

    def test_add_zero(self):
        assert add(0, 5) == 5
        assert add(5, 0) == 5


class TestMultiply:
    """Tests para la función multiply."""

    def test_multiply_positive(self):
        assert multiply(2, 3) == 6

    def test_multiply_by_zero(self):
        assert multiply(5, 0) == 0

    def test_multiply_negative(self):
        assert multiply(-2, 3) == -6

    def test_multiply_floats(self):
        assert multiply(1.5, 2) == 3.0


class TestMean:
    """Tests para la función mean."""

    def test_mean_simple(self):
        assert mean([1, 2, 3]) == 2.0

    def test_mean_single_value(self):
        assert mean([5]) == 5.0

    def test_mean_floats(self):
        assert mean([1.0, 2.0, 3.0]) == 2.0

    def test_mean_empty_raises(self):
        with pytest.raises(ValueError, match="vacía"):
            mean([])


class TestStd:
    """Tests para la función std."""

    def test_std_simple(self):
        result = std([2, 4, 4, 4, 5, 5, 7, 9])
        assert abs(result - 2.138) < 0.01

    def test_std_two_values(self):
        result = std([1, 3])
        assert abs(result - 1.414) < 0.01

    def test_std_single_raises(self):
        with pytest.raises(ValueError, match="al menos 2"):
            std([1])

    def test_std_empty_raises(self):
        with pytest.raises(ValueError):
            std([])


class TestNormalize:
    """Tests para la función normalize."""

    def test_normalize_simple(self):
        result = normalize([0, 5, 10])
        assert result == [0.0, 0.5, 1.0]

    def test_normalize_empty(self):
        assert normalize([]) == []

    def test_normalize_same_values(self):
        result = normalize([5, 5, 5])
        assert result == [0.5, 0.5, 0.5]

    def test_normalize_negative_values(self):
        result = normalize([-10, 0, 10])
        assert result == [0.0, 0.5, 1.0]

    def test_normalize_preserves_order(self):
        result = normalize([1, 2, 3, 4, 5])
        assert result == sorted(result)
