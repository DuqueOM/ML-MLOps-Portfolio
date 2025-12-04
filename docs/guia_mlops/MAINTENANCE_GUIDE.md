# 🔧 Guía de Mantenimiento — guia_mlops v2

> Esta guía describe cómo mantener la guía MLOps actualizada y funcional.

---

## 📅 Calendario de Mantenimiento

### Mensual
- [ ] Verificar que todos los links funcionan
- [ ] Actualizar versiones de dependencias en `requirements.txt`
- [ ] Ejecutar tests de todos los módulos

### Trimestral
- [ ] Revisar y actualizar ejemplos de código
- [ ] Regenerar `requirements.txt` con versiones actuales
- [ ] Verificar compatibilidad con Python más reciente
- [ ] Actualizar templates con mejores prácticas

### Semestral
- [ ] Revisar estructura completa de la guía
- [ ] Actualizar referencias y recursos externos
- [ ] Incorporar feedback de usuarios
- [ ] Evaluar nuevas herramientas del ecosistema MLOps

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
| Tests pasando | 100% | - |
| Links rotos | 0 | - |
| Coverage de docs | 100% módulos | 12/12 |
| Validación YAML | 100% | - |

### Monitoreo

Ejecutar semanalmente:

```bash
./scripts/validate_guide.sh > reports/validation_$(date +%Y%m%d).log
```

---

## 🔗 Recursos

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 👥 Contacto

- **Mantenedor**: DuqueOM
- **Repositorio**: [ML-MLOps-Portfolio](https://github.com/DuqueOM/ML-MLOps-Portfolio)

---

*Última actualización: 2024-12*
