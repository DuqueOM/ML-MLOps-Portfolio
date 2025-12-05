# 🔧 Guía de Mantenimiento — guia_mlops v5

> **Meta-documento**: Esta guía describe cómo mantener **la guía MLOps en sí misma** actualizada y funcional.
> 
> ⚠️ **¿Buscas contenido sobre operaciones de sistemas ML en producción?** Ver:
> - [17_DESPLIEGUE.md → Operaciones y Runbooks](17_DESPLIEGUE.md#-operaciones-y-runbooks)
> - [16_OBSERVABILIDAD.md](16_OBSERVABILIDAD.md) — Monitoreo y alertas
> - [Runbook del Portafolio](../OPERATIONS_PORTFOLIO.md) — Operaciones end-to-end del portafolio

*Última actualización: Diciembre 2025*

---

## 📊 Estado Actual de la Guía

| Componente | Cantidad | Estado |
|:-----------|:--------:|:------:|
| Módulos principales | 23 | ✅ Completos |
| Ejercicios | 42 | ✅ Con soluciones |
| ADRs | 14 | ✅ Actualizados |
| Recursos externos | 50+ videos | ✅ Curados |
| Glosario | 100+ términos | ✅ Expandido |

---

## 📅 Calendario de Mantenimiento

### Mensual
- [ ] Verificar que todos los links funcionan (`./scripts/check_links.sh`)
- [ ] Actualizar versiones de dependencias en `requirements.txt`
- [ ] Ejecutar tests de todos los módulos
- [ ] Verificar que videos de RECURSOS_POR_MODULO.md siguen disponibles

### Trimestral
- [ ] Revisar y actualizar ejemplos de código con mejores prácticas
- [ ] Regenerar `requirements.txt` con versiones actuales
- [ ] Verificar compatibilidad con Python más reciente (actualmente 3.11+)
- [ ] Actualizar templates con mejores prácticas
- [ ] Revisar y actualizar RECURSOS_POR_MODULO.md con nuevos videos/cursos

### Semestral
- [ ] Revisar estructura completa de la guía (23 módulos)
- [ ] Actualizar referencias y recursos externos
- [ ] Incorporar feedback de usuarios
- [ ] Evaluar nuevas herramientas del ecosistema MLOps
- [ ] Actualizar DECISIONES_TECH.md con nuevas herramientas
- [ ] Revisar que el glosario cubre todos los términos usados en módulos

---

## 🔍 Validación de la Guía

### Script de Validación

Ejecutar para verificar la integridad de la guía:

```bash
# Dar permisos de ejecución
chmod +x scripts/validate_guide.sh

# Ejecutar validación
./scripts/validate_guide.sh
```

El script verifica:
1. **Estructura de directorios**: Todos los módulos existen
2. **Archivos requeridos**: mkdocs.yml, requirements.txt, etc.
3. **Links en Markdown**: No hay links rotos
4. **Sintaxis YAML**: Archivos de configuración válidos
5. **Tests por módulo**: Cada módulo tiene tests
6. **Notebooks**: Son JSON válidos

### Ejecutar Tests Completos

```bash
# Activar entorno
source .venv/bin/activate

# Ejecutar todos los tests
make check-all

# O módulo por módulo
make check-01
make check-02
# ...
```

---

## 📦 Actualización de Dependencias

### Verificar Desactualizadas

```bash
pip list --outdated
```

### Proceso de Actualización

1. **Crear branch de actualización**
   ```bash
   git checkout -b chore/update-deps-YYYY-MM
   ```

2. **Actualizar dependencias**
   ```bash
   pip install --upgrade package-name
   ```

3. **Ejecutar tests**
   ```bash
   pytest docs/ -v
   ```

4. **Si pasan, regenerar lockfile**
   ```bash
   pip freeze > requirements.lock
   ```

5. **Commit y PR**
   ```bash
   git add requirements.txt requirements.lock
   git commit -m "chore: update dependencies YYYY-MM"
   ```

### Auditoría de Seguridad

```bash
# Instalar herramientas
pip install pip-audit safety

# Verificar vulnerabilidades
pip-audit
safety check
```

---

## 🐛 Resolución de Problemas

### Tests Fallando

1. Verificar que el entorno está activado
2. Reinstalar dependencias: `pip install -r requirements.txt`
3. Verificar versión de Python: `python --version` (3.10+)
4. Ejecutar test individual para más detalles

### Links Rotos

1. Ejecutar `./scripts/validate_guide.sh`
2. Revisar output para links específicos
3. Actualizar o eliminar links rotos

### MkDocs No Funciona

1. Verificar instalación: `mkdocs --version`
2. Reinstalar: `pip install mkdocs mkdocs-material`
3. Verificar sintaxis de `mkdocs.yml`

---

## 📝 Contribuir a la Guía

### Agregar Nuevo Contenido

1. Crear branch: `git checkout -b feat/new-content`
2. Agregar contenido en el módulo correspondiente
3. Agregar tests si aplica
4. Actualizar `mkdocs.yml` si es necesario
5. Ejecutar validación: `./scripts/validate_guide.sh`
6. Crear PR con descripción clara

### Estructura de un Módulo

```
docs/XX_nombre_modulo/
├── index.md           # Contenido principal
├── tests/
│   └── test_*.py      # Tests del módulo
└── solutions/
    └── *.py           # Soluciones de ejercicios
```

### Convenciones

- Usar **Markdown** estándar
- Incluir **ejemplos de código** ejecutables
- Agregar **ejercicios prácticos** con tests
- Mantener **links relativos** entre módulos

---

## 📊 Métricas de Calidad

### Objetivos

| Métrica | Objetivo | Actual |
|:--------|:---------|:-------|
| Tests pasando | 100% | ✅ |
| Links rotos | 0 | ✅ |
| Módulos completos | 23/23 | ✅ |
| Ejercicios con solución | 42/42 | ✅ |
| ADRs documentados | 14/14 | ✅ |
| Glosario términos | 100+ | ✅ |
| Recursos externos | 50+ | ✅ |

### Monitoreo

Ejecutar semanalmente:

```bash
./scripts/validate_guide.sh > reports/validation_$(date +%Y%m%d).log
```

---

## 📁 Estructura de Archivos de la Guía

```
docs/guia_mlops/
├── 00_INDICE.md              # Índice principal
├── 01-23_*.md                # 23 módulos temáticos
├── EJERCICIOS.md             # 42 ejercicios prácticos
├── EJERCICIOS_SOLUCIONES.md  # Soluciones detalladas
├── RUBRICA_EVALUACION.md     # Sistema de evaluación (100 puntos)
├── RECURSOS_POR_MODULO.md    # 📺 Videos y cursos externos
├── DECISIONES_TECH.md        # 14 ADRs de herramientas
├── 21_GLOSARIO.md            # 100+ términos con ejemplos
├── SIMULACRO_*.md            # Entrevistas técnicas
├── APENDICE_A_SPEECH.md      # Speech de portafolio
├── APENDICE_B_TALKING.md     # Puntos clave
├── SYLLABUS.md               # Programa de 8 semanas
├── PLAN_ESTUDIOS.md          # Cronograma día a día
├── GUIA_AUDIOVISUAL.md       # Crear demos y videos
├── MAINTENANCE_GUIDE.md      # Esta guía
├── templates/                # 13 plantillas reutilizables
└── mkdocs.yml                # Configuración MkDocs
```

---

## 🔗 Recursos Internos

| Archivo | Propósito | Actualización |
|---------|-----------|:-------------:|
| [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) | Videos y cursos externos | Trimestral |
| [DECISIONES_TECH.md](DECISIONES_TECH.md) | ADRs de herramientas | Semestral |
| [21_GLOSARIO.md](21_GLOSARIO.md) | Definiciones de términos | Mensual |
| [RUBRICA_EVALUACION.md](RUBRICA_EVALUACION.md) | Sistema de puntuación | Semestral |

### Recursos Externos

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 👥 Contacto

- **Mantenedor**: DuqueOM
- **Repositorio**: [ML-MLOps-Portfolio](https://github.com/DuqueOM/ML-MLOps-Portfolio)

---

<div align="center">

[← Volver al Índice](00_INDICE.md)

</div>
