---
title: "On-call y Gestión de Incidentes"
module: "26"
order: 1
tags:
  - "oncall"
  - "incidents"
  - "runbooks"
  - "staff-level"
status: "ready"
---

# 26 — On-call y Gestión de Incidentes

> **Tiempo estimado**: 8 horas | **Nivel**: Staff/Principal
> 
> **Prerrequisitos**: Módulos 22, 25 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Establecer **rotaciones de on-call** efectivas
2. ✅ Ejecutar **simulacros de incidentes** (game days)
3. ✅ Implementar **escalamiento** estructurado
4. ✅ Escribir **postmortems** accionables

---

## 📖 Contenido Teórico

### 1. Estructura de On-call

```
┌─────────────────────────────────────────────────────────────┐
│                    ON-CALL ESCALATION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  NIVEL 1 (0-15 min)         NIVEL 2 (15-30 min)            │
│  ─────────────────          ─────────────────               │
│  Primary On-call     -->    Secondary On-call               │
│  • Acknowledge alert        • Escalate from L1              │
│  • Initial triage           • Deep investigation            │
│  • Apply runbook            • Cross-team coordination       │
│                                                             │
│  NIVEL 3 (30-60 min)        NIVEL 4 (60+ min)              │
│  ─────────────────          ─────────────────               │
│  Tech Lead / Manager  -->   VP / Incident Commander        │
│  • Major decisions          • Executive communication       │
│  • Resource allocation      • External communication        │
│  • War room coordination    • P0 declaration                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```python
"""oncall.py — Sistema de on-call y escalamiento."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import json


class Severity(Enum):
    """Severidad de incidente."""
    P0 = "P0"  # Outage completo
    P1 = "P1"  # Degradación severa
    P2 = "P2"  # Degradación menor
    P3 = "P3"  # Issue no urgente


@dataclass
class OnCallRotation:
    """Rotación de on-call."""
    
    team: str
    schedule: List[dict]  # [{person, start, end}, ...]
    escalation_contacts: List[str]
    
    def get_current_oncall(self) -> str:
        """Obtiene persona de on-call actual."""
        now = datetime.now()
        for entry in self.schedule:
            start = datetime.fromisoformat(entry["start"])
            end = datetime.fromisoformat(entry["end"])
            if start <= now <= end:
                return entry["person"]
        return self.escalation_contacts[0]  # Fallback
    
    def get_escalation_path(self) -> List[str]:
        """Retorna path de escalamiento."""
        current = self.get_current_oncall()
        return [current] + self.escalation_contacts


@dataclass
class Incident:
    """Incidente en curso."""
    
    id: str
    title: str
    severity: Severity
    status: str = "open"  # open, investigating, mitigating, resolved
    
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    owner: Optional[str] = None
    summary: str = ""
    timeline: List[dict] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    
    def acknowledge(self, person: str) -> None:
        """Marca incidente como acknowledged."""
        self.acknowledged_at = datetime.now()
        self.owner = person
        self.add_timeline_event("acknowledged", f"Acknowledged by {person}")
    
    def add_timeline_event(self, event_type: str, description: str) -> None:
        """Agrega evento al timeline."""
        self.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
        })
    
    def resolve(self, resolution: str) -> None:
        """Resuelve el incidente."""
        self.resolved_at = datetime.now()
        self.status = "resolved"
        self.add_timeline_event("resolved", resolution)
    
    def time_to_acknowledge(self) -> Optional[timedelta]:
        """Calcula tiempo hasta acknowledgement."""
        if self.acknowledged_at:
            return self.acknowledged_at - self.created_at
        return None
    
    def time_to_resolve(self) -> Optional[timedelta]:
        """Calcula tiempo hasta resolución."""
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return None
    
    def to_dict(self) -> dict:
        """Exporta a diccionario."""
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "status": self.status,
            "owner": self.owner,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "tta_minutes": self.time_to_acknowledge().seconds // 60 if self.time_to_acknowledge() else None,
            "ttr_minutes": self.time_to_resolve().seconds // 60 if self.time_to_resolve() else None,
            "timeline": self.timeline,
        }


class IncidentManager:
    """Gestor de incidentes."""
    
    def __init__(self, oncall_rotation: OnCallRotation):
        self.oncall = oncall_rotation
        self.incidents: List[Incident] = []
        
        # SLAs por severidad (minutos)
        self.ack_sla = {
            Severity.P0: 5,
            Severity.P1: 15,
            Severity.P2: 60,
            Severity.P3: 240,
        }
        self.resolution_sla = {
            Severity.P0: 60,
            Severity.P1: 240,
            Severity.P2: 1440,  # 24h
            Severity.P3: 10080,  # 7d
        }
    
    def create_incident(
        self,
        title: str,
        severity: Severity,
        affected_services: List[str] = None,
    ) -> Incident:
        """Crea nuevo incidente."""
        incident = Incident(
            id=f"INC-{len(self.incidents) + 1:04d}",
            title=title,
            severity=severity,
            affected_services=affected_services or [],
        )
        incident.add_timeline_event("created", f"Incident created: {title}")
        self.incidents.append(incident)
        
        # Notificar on-call
        oncall_person = self.oncall.get_current_oncall()
        incident.add_timeline_event("paged", f"Paged {oncall_person}")
        
        return incident
    
    def check_sla_breaches(self) -> List[dict]:
        """Verifica incidentes que están cerca de violar SLA."""
        breaches = []
        now = datetime.now()
        
        for inc in self.incidents:
            if inc.status == "resolved":
                continue
            
            elapsed = (now - inc.created_at).seconds // 60
            
            # Check acknowledgement SLA
            if not inc.acknowledged_at:
                ack_sla = self.ack_sla[inc.severity]
                if elapsed > ack_sla * 0.8:  # 80% del SLA
                    breaches.append({
                        "incident": inc.id,
                        "type": "ack",
                        "sla_minutes": ack_sla,
                        "elapsed_minutes": elapsed,
                        "status": "breached" if elapsed > ack_sla else "at_risk",
                    })
            
            # Check resolution SLA
            res_sla = self.resolution_sla[inc.severity]
            if elapsed > res_sla * 0.8:
                breaches.append({
                    "incident": inc.id,
                    "type": "resolution",
                    "sla_minutes": res_sla,
                    "elapsed_minutes": elapsed,
                    "status": "breached" if elapsed > res_sla else "at_risk",
                })
        
        return breaches
```

---

### 2. Simulacros de Incidentes (Game Days)

```python
"""gameday.py — Simulacros de incidentes."""
from dataclasses import dataclass
from typing import List, Dict, Callable
import random
import time


@dataclass
class GameDayScenario:
    """Escenario para simulacro."""
    
    name: str
    description: str
    severity: str
    inject_actions: List[str]
    expected_response: List[str]
    success_criteria: List[str]
    duration_minutes: int


SCENARIOS = {
    "model_degradation": GameDayScenario(
        name="Model Performance Degradation",
        description="El modelo de predicción muestra accuracy <60% por drift",
        severity="P1",
        inject_actions=[
            "Modificar datos de input para simular drift",
            "Generar alertas de accuracy bajo",
            "Simular incremento en tasa de errores",
        ],
        expected_response=[
            "Acknowledge alerta en <15 min",
            "Identificar causa raíz (drift)",
            "Rollback a versión anterior o desactivar modelo",
            "Comunicar a stakeholders",
        ],
        success_criteria=[
            "TTA < 15 minutos",
            "TTR < 60 minutos",
            "Zero impacto a usuarios finales",
            "Postmortem programado",
        ],
        duration_minutes=60,
    ),
    "api_outage": GameDayScenario(
        name="API de Inferencia Caída",
        description="La API de predicción no responde (5xx errors)",
        severity="P0",
        inject_actions=[
            "Detener container de API",
            "Simular saturación de recursos",
            "Bloquear conexiones a base de datos",
        ],
        expected_response=[
            "Acknowledge alerta en <5 min",
            "Escalar a L2 si no hay progreso",
            "Activar runbook de recovery",
            "Comunicar via status page",
        ],
        success_criteria=[
            "TTA < 5 minutos",
            "TTR < 30 minutos",
            "Failover ejecutado correctamente",
            "Comunicación externa enviada",
        ],
        duration_minutes=45,
    ),
    "data_pipeline_failure": GameDayScenario(
        name="Fallo en Pipeline de Datos",
        description="El pipeline de features falla, datos no se actualizan",
        severity="P2",
        inject_actions=[
            "Introducir error en transformación",
            "Simular timeout en fuente de datos",
            "Corromper archivo de configuración",
        ],
        expected_response=[
            "Detectar vía monitoring",
            "Investigar logs del pipeline",
            "Aplicar fix o revertir cambio",
            "Verificar integridad de datos",
        ],
        success_criteria=[
            "Detectado en <30 min",
            "Fix aplicado en <4 horas",
            "Sin impacto en predicciones",
        ],
        duration_minutes=120,
    ),
}


class GameDayRunner:
    """Ejecutor de simulacros."""
    
    def __init__(self, incident_manager):
        self.incident_manager = incident_manager
        self.results: List[Dict] = []
    
    def run_scenario(self, scenario_name: str) -> dict:
        """Ejecuta un escenario de simulacro."""
        scenario = SCENARIOS.get(scenario_name)
        if not scenario:
            raise ValueError(f"Escenario no encontrado: {scenario_name}")
        
        print(f"\n{'='*60}")
        print(f"GAME DAY: {scenario.name}")
        print(f"{'='*60}")
        print(f"Descripción: {scenario.description}")
        print(f"Severidad: {scenario.severity}")
        print(f"Duración esperada: {scenario.duration_minutes} min")
        print(f"\n📋 Acciones a inyectar:")
        for action in scenario.inject_actions:
            print(f"  - {action}")
        print(f"\n✅ Respuesta esperada:")
        for resp in scenario.expected_response:
            print(f"  - {resp}")
        print(f"\n🎯 Criterios de éxito:")
        for criteria in scenario.success_criteria:
            print(f"  - {criteria}")
        
        # Simular creación de incidente
        input("\n[Press Enter para iniciar simulacro...]")
        
        start_time = time.time()
        
        # Crear incidente
        from .oncall import Severity
        sev_map = {"P0": Severity.P0, "P1": Severity.P1, "P2": Severity.P2, "P3": Severity.P3}
        incident = self.incident_manager.create_incident(
            title=f"[GAMEDAY] {scenario.name}",
            severity=sev_map[scenario.severity],
        )
        
        print(f"\n🚨 Incidente creado: {incident.id}")
        print("Simulacro en progreso... (equipo debe responder)")
        
        # Esperar acknowledgement manual
        input("[Press Enter cuando el equipo haya acknowledged...]")
        incident.acknowledge("gameday-participant")
        tta = time.time() - start_time
        
        # Esperar resolución manual
        input("[Press Enter cuando el equipo haya resuelto...]")
        incident.resolve("Simulacro completado")
        ttr = time.time() - start_time
        
        result = {
            "scenario": scenario_name,
            "incident_id": incident.id,
            "tta_seconds": tta,
            "ttr_seconds": ttr,
            "success": self._evaluate_success(scenario, tta, ttr),
        }
        
        self.results.append(result)
        
        print(f"\n📊 Resultados:")
        print(f"  TTA: {tta/60:.1f} minutos")
        print(f"  TTR: {ttr/60:.1f} minutos")
        print(f"  Éxito: {'✅' if result['success'] else '❌'}")
        
        return result
    
    def _evaluate_success(self, scenario: GameDayScenario, tta: float, ttr: float) -> bool:
        """Evalúa si se cumplieron criterios de éxito."""
        # Simplificado: solo evaluar tiempos
        if scenario.severity == "P0":
            return tta < 300 and ttr < 1800  # 5 min / 30 min
        elif scenario.severity == "P1":
            return tta < 900 and ttr < 3600  # 15 min / 60 min
        else:
            return tta < 3600 and ttr < 14400  # 1 hora / 4 horas
```

---

### 3. Template de Postmortem

```markdown
# Postmortem: [Título del Incidente]

## Resumen Ejecutivo
- **Fecha**: YYYY-MM-DD
- **Severidad**: P[0-3]
- **Duración**: X horas Y minutos
- **Impacto**: [Descripción breve del impacto]
- **Causa raíz**: [Una frase]

## Timeline
| Hora | Evento |
|:-----|:-------|
| HH:MM | Alerta disparada |
| HH:MM | On-call acknowledges |
| HH:MM | Investigación iniciada |
| HH:MM | Causa raíz identificada |
| HH:MM | Mitigación aplicada |
| HH:MM | Incidente resuelto |

## Detección
- **Cómo se detectó**: [Alerta / Reporte de usuario / Otro]
- **Tiempo de detección**: X minutos desde inicio
- **¿Mejorable?**: [Sí/No y cómo]

## Causa Raíz
[Descripción detallada de la causa raíz, usando 5 Whys si es necesario]

### 5 Whys
1. **¿Por qué falló X?** Porque Y
2. **¿Por qué Y?** Porque Z
3. ...

## Impacto
- **Usuarios afectados**: N
- **Requests fallidas**: N
- **Duración del impacto**: X minutos
- **Revenue impactado**: $X (si aplica)

## Mitigación y Resolución
[Pasos específicos tomados para resolver]

1. [Paso 1]
2. [Paso 2]
3. ...

## Lecciones Aprendidas
### Lo que funcionó bien
- [Item 1]
- [Item 2]

### Lo que no funcionó
- [Item 1]
- [Item 2]

### Dónde tuvimos suerte
- [Item 1]

## Action Items
| ID | Acción | Owner | Deadline | Status |
|:---|:-------|:------|:---------|:-------|
| 1 | [Descripción] | @persona | YYYY-MM-DD | TODO |
| 2 | [Descripción] | @persona | YYYY-MM-DD | TODO |

## Métricas SLA
- **TTA (Time to Acknowledge)**: X min (SLA: Y min) ✅/❌
- **TTR (Time to Resolve)**: X min (SLA: Y min) ✅/❌
- **MTTR trending**: [Mejorando/Empeorando/Estable]

## Aprobaciones
- [ ] Revisado por: @tech-lead
- [ ] Aprobado por: @manager
- [ ] Action items asignados
```

---

## 🔧 Mini-Proyecto: Simulacro Completo

### Objetivo

1. Configurar rotación de on-call
2. Ejecutar un game day
3. Escribir postmortem
4. Implementar action items

### Criterios de Éxito

- [ ] Rotación de on-call documentada
- [ ] Game day ejecutado
- [ ] Postmortem escrito
- [ ] ≥1 action item completado

---

## ✅ Validación

```bash
make check-26
```

---

## 🎉 ¡Módulo Final Completado!

Has terminado los módulos de nivel Staff. Ahora tienes conocimientos de:

- ✅ Data Lineage & Governance
- ✅ Seguridad y Testing Adversarial
- ✅ Performance y Optimización de Costos
- ✅ Model Risk Management
- ✅ On-call y Gestión de Incidentes

**Siguiente paso**: Aplica todo en el proyecto integrador.

---

*Última actualización: 2024-12*
