---
title: "Data Lineage & Governance"
module: "07"
order: 1
tags:
  - "data-lineage"
  - "governance"
  - "contracts"
  - "staff-level"
status: "ready"
---

# 07 — Data Lineage & Governance

> **Tiempo estimado**: 8 horas | **Nivel**: Staff/Principal
> 
> **Prerrequisitos**: Módulos 05-06 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Rastrear el **origen y transformaciones** de cada feature
2. ✅ Implementar **contratos de datos** entre equipos
3. ✅ Documentar **data lineage** automáticamente
4. ✅ Establecer **políticas de governance** para ML

---

## 📖 Contenido Teórico

### 1. ¿Qué es Data Lineage?

**Data Lineage** rastrea el ciclo de vida de los datos: de dónde vienen, cómo se transforman y dónde terminan.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Fuente    │ --> │   Ingesta   │ --> │  Transform  │ --> │   Feature   │
│   (MySQL)   │     │   (Spark)   │     │  (Pandas)   │     │   Store     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      v                   v                   v                   v
   raw.users        staging.users       features.users      model_input
   
Lineage: raw.users → staging.users → features.users → model_input
```

### 2. Implementación de Lineage Tracking

```python
"""lineage.py — Sistema de tracking de lineage."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4
import json


@dataclass
class LineageNode:
    """Nodo en el grafo de lineage."""
    
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    node_type: str = "dataset"  # dataset, transform, model
    source: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)
    parents: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type,
            "source": self.source,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "parents": self.parents,
        }


class LineageTracker:
    """Rastreador de lineage para pipelines de datos."""
    
    def __init__(self, project_name: str = "default"):
        self.project = project_name
        self.nodes: dict[str, LineageNode] = {}
        self.edges: list[tuple[str, str]] = []
    
    def register_dataset(
        self,
        name: str,
        source: str,
        parents: list[str] = None,
        metadata: dict = None,
    ) -> str:
        """Registra un dataset en el lineage."""
        node = LineageNode(
            name=name,
            node_type="dataset",
            source=source,
            parents=parents or [],
            metadata=metadata or {},
        )
        self.nodes[node.id] = node
        
        # Registrar edges
        for parent_id in node.parents:
            self.edges.append((parent_id, node.id))
        
        return node.id
    
    def register_transform(
        self,
        name: str,
        input_ids: list[str],
        output_name: str,
        transform_code: str = "",
    ) -> str:
        """Registra una transformación."""
        # Nodo de transformación
        transform_node = LineageNode(
            name=name,
            node_type="transform",
            source=transform_code,
            parents=input_ids,
            metadata={"inputs": input_ids},
        )
        self.nodes[transform_node.id] = transform_node
        
        # Nodo de output
        output_node = LineageNode(
            name=output_name,
            node_type="dataset",
            source=f"transform:{name}",
            parents=[transform_node.id],
        )
        self.nodes[output_node.id] = output_node
        
        # Edges
        for input_id in input_ids:
            self.edges.append((input_id, transform_node.id))
        self.edges.append((transform_node.id, output_node.id))
        
        return output_node.id
    
    def get_upstream(self, node_id: str, depth: int = -1) -> list[LineageNode]:
        """Obtiene todos los nodos upstream."""
        if node_id not in self.nodes:
            return []
        
        visited = set()
        result = []
        
        def traverse(nid: str, current_depth: int):
            if nid in visited:
                return
            if depth != -1 and current_depth > depth:
                return
            
            visited.add(nid)
            node = self.nodes.get(nid)
            if node:
                result.append(node)
                for parent in node.parents:
                    traverse(parent, current_depth + 1)
        
        traverse(node_id, 0)
        return result[1:]  # Excluir el nodo inicial
    
    def export_graph(self, output_path: str) -> None:
        """Exporta el grafo de lineage a JSON."""
        graph = {
            "project": self.project,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [{"from": e[0], "to": e[1]} for e in self.edges],
        }
        with open(output_path, 'w') as f:
            json.dump(graph, f, indent=2)
    
    def visualize_mermaid(self) -> str:
        """Genera diagrama Mermaid del lineage."""
        lines = ["graph LR"]
        
        for node in self.nodes.values():
            shape = "([" if node.node_type == "dataset" else "[["
            end_shape = "])" if node.node_type == "dataset" else "]]"
            lines.append(f"    {node.id}{shape}{node.name}{end_shape}")
        
        for src, dst in self.edges:
            lines.append(f"    {src} --> {dst}")
        
        return "\n".join(lines)


# Ejemplo de uso
tracker = LineageTracker("churn_project")

# Registrar datasets fuente
raw_customers = tracker.register_dataset(
    name="raw_customers",
    source="mysql://prod/customers",
    metadata={"rows": 100000, "columns": 15}
)

raw_transactions = tracker.register_dataset(
    name="raw_transactions",
    source="mysql://prod/transactions",
    metadata={"rows": 5000000}
)

# Registrar transformación
features = tracker.register_transform(
    name="create_features",
    input_ids=[raw_customers, raw_transactions],
    output_name="customer_features",
    transform_code="features.py::create_features()"
)

print(tracker.visualize_mermaid())
```

---

### 3. Contratos de Datos

```python
"""contracts.py — Contratos de datos entre equipos."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class DataContract(BaseModel):
    """Contrato formal para un dataset."""
    
    # Identificación
    name: str = Field(..., description="Nombre único del dataset")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    owner: str = Field(..., description="Equipo responsable")
    
    # Schema
    schema_definition: dict = Field(..., description="Schema esperado")
    
    # SLA
    freshness_hours: int = Field(24, description="Máxima antigüedad en horas")
    availability_sla: float = Field(0.99, ge=0, le=1)
    
    # Calidad
    quality_rules: list[dict] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    deprecated: bool = False
    successor: Optional[str] = None
    
    def validate_data(self, df) -> tuple[bool, list[str]]:
        """Valida un DataFrame contra el contrato."""
        errors = []
        
        # Validar schema
        expected_cols = set(self.schema_definition.keys())
        actual_cols = set(df.columns)
        
        missing = expected_cols - actual_cols
        if missing:
            errors.append(f"Columnas faltantes: {missing}")
        
        # Validar tipos
        for col, expected_type in self.schema_definition.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if expected_type not in actual_type:
                    errors.append(f"Tipo incorrecto en {col}: esperado {expected_type}, actual {actual_type}")
        
        # Validar reglas de calidad
        for rule in self.quality_rules:
            if rule["type"] == "not_null":
                col = rule["column"]
                if df[col].isnull().any():
                    errors.append(f"Valores nulos en {col}")
            elif rule["type"] == "unique":
                col = rule["column"]
                if df[col].duplicated().any():
                    errors.append(f"Valores duplicados en {col}")
        
        return len(errors) == 0, errors


# Ejemplo de contrato
customer_contract = DataContract(
    name="customer_features",
    version="1.0.0",
    owner="data-engineering",
    schema_definition={
        "customer_id": "str",
        "age": "int",
        "balance": "float",
        "tenure": "int",
        "is_active": "bool",
    },
    freshness_hours=24,
    quality_rules=[
        {"type": "not_null", "column": "customer_id"},
        {"type": "unique", "column": "customer_id"},
        {"type": "not_null", "column": "age"},
    ],
)
```

---

### 4. Políticas de Governance

```python
"""governance.py — Políticas de governance para ML."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DataClassification(Enum):
    """Clasificación de sensibilidad de datos."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # PII, financiero


class RetentionPolicy(Enum):
    """Políticas de retención."""
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_365 = 365
    YEARS_7 = 365 * 7  # Regulatorio


@dataclass
class GovernancePolicy:
    """Política de governance para un dataset."""
    
    dataset_name: str
    classification: DataClassification
    retention: RetentionPolicy
    
    # Acceso
    allowed_teams: list[str]
    requires_approval: bool = False
    approval_workflow: Optional[str] = None
    
    # Auditoría
    audit_access: bool = True
    log_queries: bool = True
    
    # Cumplimiento
    gdpr_relevant: bool = False
    can_be_exported: bool = True
    anonymization_required: bool = False
    
    def check_access(self, team: str, purpose: str) -> tuple[bool, str]:
        """Verifica si un equipo puede acceder."""
        if team not in self.allowed_teams:
            return False, f"Equipo {team} no autorizado"
        
        if self.requires_approval:
            return False, f"Requiere aprobación via {self.approval_workflow}"
        
        return True, "Acceso permitido"


# Ejemplo de políticas
policies = {
    "customer_pii": GovernancePolicy(
        dataset_name="customer_pii",
        classification=DataClassification.RESTRICTED,
        retention=RetentionPolicy.YEARS_7,
        allowed_teams=["data-science", "compliance"],
        requires_approval=True,
        approval_workflow="jira/DATA-ACCESS",
        gdpr_relevant=True,
        anonymization_required=True,
    ),
    "aggregated_metrics": GovernancePolicy(
        dataset_name="aggregated_metrics",
        classification=DataClassification.INTERNAL,
        retention=RetentionPolicy.DAYS_365,
        allowed_teams=["data-science", "analytics", "product"],
        requires_approval=False,
    ),
}
```

---

## 🔧 Mini-Proyecto: Sistema de Lineage

### Objetivo

1. Implementar `LineageTracker` para tu pipeline
2. Definir `DataContract` para datasets principales
3. Crear políticas de governance
4. Generar diagrama de lineage

### Estructura

```
work/07_data_lineage/
├── src/
│   ├── lineage.py
│   ├── contracts.py
│   └── governance.py
├── contracts/
│   └── customer_features.yaml
├── policies/
│   └── governance.yaml
├── outputs/
│   └── lineage_graph.json
└── tests/
    └── test_lineage.py
```

### Mapa → Repo

| Concepto | Archivo del Repo |
|:---------|:-----------------|
| Feature lineage | `projects/BankChurn/src/bankchurn/features.py` |
| Data validation | `projects/BankChurn/src/bankchurn/data.py` |
| Config contracts | `projects/BankChurn/src/bankchurn/config.py` |

---

## ✅ Validación

```bash
make check-07
```

---

## ➡️ Siguiente Módulo

**[08 — EDA y Calidad de Datos](../08_eda_calidad/index.md)**

---

*Última actualización: 2024-12*
