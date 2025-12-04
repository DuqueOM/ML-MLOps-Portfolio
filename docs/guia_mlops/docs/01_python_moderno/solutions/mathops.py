"""Operaciones matemáticas con type hints — Solución Módulo 01."""

import math
from typing import Sequence


def add(a: float, b: float) -> float:
    """Suma dos números.

    Args:
        a: Primer número
        b: Segundo número

    Returns:
        La suma de a y b
    """
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiplica dos números.

    Args:
        a: Primer número
        b: Segundo número

    Returns:
        El producto de a y b
    """
    return a * b


def mean(values: Sequence[float]) -> float:
    """Calcula la media aritmética de una secuencia.

    Args:
        values: Secuencia de valores numéricos

    Returns:
        La media de los valores

    Raises:
        ValueError: Si la secuencia está vacía
    """
    if not values:
        raise ValueError("La secuencia no puede estar vacía")
    return sum(values) / len(values)


def std(values: Sequence[float]) -> float:
    """Calcula la desviación estándar muestral.

    Usa la fórmula con n-1 (desviación estándar muestral).

    Args:
        values: Secuencia de valores numéricos

    Returns:
        La desviación estándar de los valores

    Raises:
        ValueError: Si hay menos de 2 valores
    """
    if len(values) < 2:
        raise ValueError("Se necesitan al menos 2 valores para calcular std")

    avg = mean(values)
    variance = sum((x - avg) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def normalize(values: Sequence[float]) -> list[float]:
    """Normaliza valores al rango [0, 1] usando min-max scaling.

    Args:
        values: Secuencia de valores numéricos

    Returns:
        Lista de valores normalizados entre 0 y 1

    Note:
        Si todos los valores son iguales, retorna 0.5 para cada uno
    """
    if not values:
        return []

    min_val = min(values)
    max_val = max(values)

    # Caso especial: todos los valores son iguales
    if max_val == min_val:
        return [0.5] * len(values)

    return [(x - min_val) / (max_val - min_val) for x in values]
