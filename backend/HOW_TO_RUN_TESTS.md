# 🚀 Cómo Ejecutar las Pruebas Unitarias

## 📋 Resumen Rápido

Has recibido una guía completa con:

1. **GUIA_PRUEBAS_UNITARIAS_CU15_CU18.md** ← LEE ESTO PRIMERO (teoría + ejemplos)
2. **backend/tests/conftest.py** ← Fixtures reutilizables
3. **backend/pytest.ini** ← Configuración de pytest
4. **backend/app/.../tests/** ← Tests listos para usar
5. **backend/run_tests.sh** ← Script conveniente

---

## 🔥 Quick Start

### 1. Instalar dependencias

```bash
cd backend

# Instalar pytest y plugins necesarios
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

### 2. Ejecutar todos los tests

**Opción A: Usando script**
```bash
./run_tests.sh all
```

**Opción B: Directo con pytest**
```bash
pytest -v
```

### 3. Ejecutar tests de un CU específico

```bash
# CU15: Gestión de Auxilio a Tiempo Real
./run_tests.sh cu15

# CU17 + CU18: Cotizaciones
./run_tests.sh cu17

# Solo unitarios (rápido)
./run_tests.sh unit

# Con reporte de cobertura
./run_tests.sh coverage
```

---

## 📂 Estructura de Carpetas

```
backend/
├── pytest.ini                          ← Configuración
├── run_tests.sh                        ← Script de ejecución
├── tests/
│   └── conftest.py                    ← Fixtures globales
└── app/packages/
    └── gestion_emergencias_solicitudes/
        └── modules/
            ├── auxilio_tiempo_real/
            │   └── tests/
            │       └── test_auxilio_service.py
            └── cotizaciones/
                └── tests/
                    └── test_cotizacion_service.py
```

---

## 💡 Primeros Pasos

### Paso 1: Entender la estructura

Lee estos archivos en este orden:

1. [GUIA_PRUEBAS_UNITARIAS_CU15_CU18.md](../GUIA_PRUEBAS_UNITARIAS_CU15_CU18.md)
   - Entiende qué son pruebas unitarias
   - Ve los ejemplos de código
   - Aprende el patrón AAA (Arrange, Act, Assert)

2. [conftest.py](./tests/conftest.py)
   - Mocks y fixtures que puedes reutilizar
   - Entiende cómo funcionan los fixtures

3. Los archivos `test_*.py` en cada módulo
   - Mira cómo se estructuran los tests
   - Copia el patrón

### Paso 2: Ejecutar tests existentes

```bash
cd backend

# Ver todos los tests sin ejecutar
pytest --collect-only

# Ejecutar y ver resultados
pytest -v

# Ejecutar un test específico
pytest app/packages/gestion_emergencias_solicitudes/modules/cotizaciones/tests/test_cotizacion_service.py::TestCotizacionServiceCreation::test_crear_cotizacion_exitosa -v
```

### Paso 3: Crear tu propio test

En el archivo `test_cotizacion_service.py`:

```python
@pytest.mark.unit
def test_mi_nuevo_test(self, mock_db, mock_taller):
    # ARRANGE
    datos = {"algo": "valor"}
    
    # ACT
    resultado = service.hacer_algo(datos)
    
    # ASSERT
    assert resultado is not None
```

Luego ejecutar:

```bash
pytest app/packages/.../test_cotizacion_service.py::TestMiClase::test_mi_nuevo_test -v
```

---

## 🎯 Comandos Útiles

```bash
# Ver todos los tests disponibles
pytest --collect-only

# Ejecutar con salida completa (verbose)
pytest -v

# Ejecutar un archivo específico
pytest backend/app/packages/gestion_emergencias_solicitudes/modules/cotizaciones/tests/test_cotizacion_service.py -v

# Ejecutar un test específico
pytest backend/app/packages/gestion_emergencias_solicitudes/modules/cotizaciones/tests/test_cotizacion_service.py::TestCotizacionServiceCreation::test_crear_cotizacion_exitosa -v

# Ejecutar solo tests rápidos (sin "slow")
pytest -m "not slow" -v

# Ejecutar con traceback corto
pytest --tb=short -v

# Ejecutar con traceback largo
pytest --tb=long -v

# Ejecutar con output más limpio (sin detalles)
pytest --tb=line -v

# Ver cobertura de código
pytest --cov=app -v

# Ver cobertura en HTML
pytest --cov=app --cov-report=html
# Luego abre: htmlcov/index.html

# Mostrar las 10 pruebas más lentas
pytest --durations=10

# Ejecutar en paralelo (instalar pytest-xdist)
pytest -n auto

# Parar en el primer error
pytest -x

# Abrir debugger en primer fallo
pytest --pdb

# Ejecutar solo tests que fallaron la última vez
pytest --lf

# Ejecutar tests hasta que falle uno
pytest -x

# Mostrar print() durante ejecución
pytest -s

# Usar un archivo de config diferente
pytest -c custom_pytest.ini
```

---

## 🐛 Troubleshooting

### Error: "No module named 'pytest'"

**Solución:** Instalar pytest

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### Error: "Cannot import app modules"

**Solución:** Asegúrate que estás en la carpeta `backend` y que el venv está activado

```bash
cd backend
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

python -c "import app; print(app)"
```

### Los tests no encuentran fixtures

**Solución:** El `conftest.py` debe estar en `backend/tests/`

```bash
# Verificar que existe
ls -la backend/tests/conftest.py

# Si no existe, crear:
touch backend/tests/conftest.py
```

### TypeError: "mock_db" fixture not found

**Solución:** Asegúrate que `conftest.py` esté en `backend/tests/` NO en `backend/tests/modules/...`

Los fixtures deben estar en el nivel más alto.

---

## 📊 Reporte de Cobertura

Después de ejecutar:

```bash
pytest --cov=app --cov-report=html
```

Se genera `htmlcov/index.html`. Abre para ver:

- % de código cubierto por tests
- Qué líneas NO están siendo testeadas
- Sugerencias de qué testear

---

## 🏃 Modo Watch (Auto-rerun)

Para que los tests se ejecuten automáticamente al guardar archivos:

```bash
# Instalar pytest-watch
pip install pytest-watch

# Ejecutar en modo watch
./run_tests.sh watch
```

---

## 🔄 Integración CI/CD

Si usas GitHub Actions, GitLab CI, etc., añade en tu pipeline:

```yaml
- name: Run Tests
  run: |
    cd backend
    pip install -r requirements.txt pytest pytest-asyncio pytest-cov pytest-mock
    pytest --cov=app --cov-report=xml
```

---

## 📚 Recursos

- [Pytest Docs](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-events/)
- [Unittest.mock Docs](https://docs.python.org/3/library/unittest.mock.html)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)

---

## ❓ Preguntas Frecuentes

**P: ¿Cómo hago un test async?**

R: Usa `@pytest.mark.asyncio` y `async def`:

```python
@pytest.mark.asyncio
async def test_algo_async(self, mock_db):
    resultado = await service.hacer_algo()
    assert resultado
```

**P: ¿Cómo hago mocks de funciones externas?**

R: Usa `@patch`:

```python
@patch('app.core.socket_manager.manager')
def test_con_socket(self, mock_socket, mock_db):
    mock_socket.broadcast = Mock()
    # ...
```

**P: ¿Cómo hago que un test falle a propósito?**

R: Usa `pytest.fail()` o simplemente `assert False`:

```python
pytest.fail("Razón por la que falla")
# o
assert False, "Razón"
```

**P: ¿Puedo debuggear un test?**

R: Sí, usa `--pdb`:

```bash
pytest test_archivo.py --pdb
```

O añade `breakpoint()` en el test:

```python
def test_algo(self):
    breakpoint()  # Se abre el debugger aquí
    resultado = hacer_algo()
```

---

## ✅ Checklist antes de hacer commit

- [ ] Ejecuté `pytest -v` y todos pasan
- [ ] Ejecuté `pytest --cov=app` y la cobertura es > 70%
- [ ] Los tests que agregué siguen el patrón AAA
- [ ] No hay `print()` o `breakpoint()` olvidados
- [ ] Los nombres de los tests son descriptivos

---

## 🎉 ¡Listo!

Ahora tienes:

✅ Entendimiento de cómo testear CU15, CU16, CU17, CU18
✅ Ejemplos de código listos para usar
✅ Fixtures reutilizables
✅ Script para ejecutar fácilmente
✅ Guía completa de referencia

**Siguiente paso:** Lee [GUIA_PRUEBAS_UNITARIAS_CU15_CU18.md](../GUIA_PRUEBAS_UNITARIAS_CU15_CU18.md) para profundizar.
