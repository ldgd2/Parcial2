# 📋 Quick Reference Card: Testing CU15, CU16, CU17, CU18

## Estructura Básica de un Test (Patrón AAA)

```python
@pytest.mark.unit
def test_nombre_descriptivo(self, mock_db, mock_taller):
    # ARRANGE: Preparar datos
    datos = {"id": 1, "nombre": "Test"}
    
    # ACT: Ejecutar la función
    resultado = service.hacer_algo(datos)
    
    # ASSERT: Validar resultado
    assert resultado is not None
    assert resultado.id == 1
    mock_db.commit.assert_called_once()
```

---

## Fixtures Disponibles

```python
# Autenticación
auth_headers_tecnico
auth_headers_cliente
auth_headers_admin

# WebSockets
mock_socket_manager
async_mock_socket

# Modelos
mock_emergencia
mock_tecnico
mock_tecnico_ocupado
mock_taller
mock_taller_inactivo
mock_cotizacion
mock_estado
mock_asignacion_tecnico

# Datos para crear
cotizacion_data
emergencia_data

# Helpers
assert_close_coordinates
mock_db
mock_db_with_query_chain
```

---

## Casos de Uso por Módulo

### CU15: Auxilio a Tiempo Real

**Qué testear:**
- ✅ Asignar técnico disponible
- ✅ Rechazar si técnico no disponible
- ✅ Calcular ETA (distancia + velocidad)
- ✅ Cambiar estado (EN_RUTA, ATENDIENDO, FINALIZADO)
- ✅ Actualizar ubicación en tiempo real
- ✅ No asignar 2 emergencias al mismo técnico

**Archivo:**
```
backend/app/packages/.../auxilio_tiempo_real/tests/test_auxilio_service.py
```

### CU16: Sincronizar Emergencias Offline

**Qué testear:**
- ✅ Guardar localmente cuando falla conexión
- ✅ Sincronizar al recuperar conexión
- ✅ Resolver conflictos (última modificación gana)
- ✅ Marcar como no sincronizado si falla

**Frontend:**
```
frontend/src/app/services/sync.service.spec.ts
```

**Mobile:**
```
tallermovil/test/services/sync_service_test.dart
```

### CU17: Gestionar Cotizaciones

**Qué testear:**
- ✅ Crear cotización (sin duplicatas)
- ✅ Validar expiración (10 minutos)
- ✅ Cambiar estado
- ✅ Calcular costo total
- ✅ Validar que taller esté ACTIVO

**Archivo:**
```
backend/app/packages/.../cotizaciones/tests/test_cotizacion_service.py
```

### CU18: Seleccionar Taller

**Qué testear:**
- ✅ Listar cotizaciones ordenadas por precio
- ✅ Validar authorization (cliente solo su emergencia)
- ✅ Asignar taller a emergencia
- ✅ Rechazar otras cotizaciones automáticamente
- ✅ Notificar a talleres

**Archivo:**
```
backend/app/packages/.../cotizaciones/tests/test_cotizacion_service.py
```

---

## Comandos Útiles

```bash
cd backend

# Ver todos los tests
pytest --collect-only

# Ejecutar todos
pytest -v

# Un archivo específico
pytest app/.../test_cotizacion_service.py -v

# Un test específico
pytest app/.../test_cotizacion_service.py::TestClass::test_nombre -v

# Solo unitarios
pytest -m unit -v

# Solo integración
pytest -m integration -v

# Con cobertura
pytest --cov=app -v

# Cobertura HTML
pytest --cov=app --cov-report=html

# Tests lentos
pytest --durations=10

# Parar en primer error
pytest -x

# Ver print statements
pytest -s

# Abrir debugger en fallo
pytest --pdb

# En paralelo (instalar pytest-xdist)
pytest -n auto

# Mode watch
pytest-watch app/packages/.../tests/
```

---

## Mocking Comúnes

```python
# Mock simple
mock_db = Mock()
mock_db.add = Mock()
mock_db.commit = Mock()

# Mock con side_effect
mock_db.query.return_value.filter.return_value.first.side_effect = [
    mock_tecnico,    # Primera llamada
    mock_emergencia  # Segunda llamada
]

# Mock async
async_mock = AsyncMock()
await async_mock()

# Mock de funciones
@patch('app.core.socket_manager.manager')
def test_algo(self, mock_socket):
    mock_socket.broadcast = AsyncMock()

# Validar llamadas
mock_db.commit.assert_called_once()
mock_db.add.assert_called_with(algo)
mock_socket.broadcast.assert_called()
```

---

## Assertions Comúnes

```python
# Igualdad
assert resultado == esperado
assert resultado.id == 1

# Nullability
assert resultado is not None
assert resultado is None

# Excepciones
with pytest.raises(HTTPException) as exc:
    service.hacer_algo()
assert exc.value.status_code == 400

# Listas
assert len(lista) == 3
assert 1 in lista
assert lista[0] == algo

# Booleans
assert condicion
assert not condicion

# Mock calls
mock.assert_called()
mock.assert_called_once()
mock.assert_called_with(arg1, arg2)
mock.assert_not_called()
mock.call_count == 2
```

---

## Decoradores Útiles

```python
@pytest.mark.unit              # Test unitario
@pytest.mark.integration       # Test de integración
@pytest.mark.asyncio           # Test async
@pytest.mark.slow              # Test lento
@pytest.mark.skip              # Saltar test
@pytest.mark.skipif(...)       # Saltar condicionalmente
@pytest.mark.xfail             # Fallo esperado
@pytest.mark.parametrize(...)  # Tests parametrizados
```

---

## Estructura de Carpetas

```
backend/
├── pytest.ini
├── HOW_TO_RUN_TESTS.md
├── tests/
│   └── conftest.py
└── app/packages/
    └── gestion_emergencias_solicitudes/
        └── modules/
            ├── auxilio_tiempo_real/
            │   └── tests/
            │       ├── __init__.py
            │       └── test_auxilio_service.py
            └── cotizaciones/
                └── tests/
                    ├── __init__.py
                    └── test_cotizacion_service.py
```

---

## Checklist para Nueva Prueba

- [ ] Archivo en `tests/` dentro del módulo
- [ ] Nombre: `test_*.py`
- [ ] Clase: `Test*` (e.g., `TestCotizacionService`)
- [ ] Método: `test_*` (e.g., `test_crear_cotizacion_exitosa`)
- [ ] Patrón AAA (Arrange, Act, Assert)
- [ ] Nombre descriptivo que explique qué se testea
- [ ] Usa fixtures del `conftest.py`
- [ ] Está marcado con `@pytest.mark.unit` o `@pytest.mark.integration`
- [ ] Valida excepciones con `pytest.raises()`
- [ ] Valida mock calls

---

## Errores Comúnes

```
❌ "conftest.py not found"
✅ Está en backend/tests/ NO en backend/

❌ "fixture 'mock_db' not found"
✅ conftest.py debe estar en backend/tests/

❌ "No module named 'app'"
✅ Ejecutar desde backend/ y tener __init__.py en cada carpeta

❌ "E: object has no attribute 'commit'"
✅ Usar Mock(spec=Session) para que tenga los métodos correctos

❌ Mock no es async
✅ Usar AsyncMock() en lugar de Mock()

❌ "TypeError: 'coroutine' object is not awaitable"
✅ Falta @pytest.mark.asyncio en el test
```

---

## Plantilla Rápida

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestMiServicio:
    """Tests para mi servicio"""
    
    @pytest.mark.unit
    def test_caso_exitoso(self, mock_db, mock_taller):
        # ARRANGE
        datos = mock_taller
        
        # ACT
        resultado = hacer_algo(datos)
        
        # ASSERT
        assert resultado is not None
    
    @pytest.mark.unit
    def test_caso_error(self, mock_db):
        # ARRANGE, ACT, ASSERT
        with pytest.raises(Exception):
            hacer_algo_que_falla()
```

---

## Links Útiles

- Guía Completa: `GUIA_PRUEBAS_UNITARIAS_CU15_CU18.md`
- How to Run: `HOW_TO_RUN_TESTS.md`
- [Pytest Docs](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-events/)
- [Mock Docs](https://docs.python.org/3/library/unittest.mock.html)

---

## Imprime esto y tendrás todo a mano 🎯
