"""
Test de Ejemplo "Hello World"
Ubicación: backend/tests/test_hello_world.py

Este archivo demuestra:
- ✅ Cómo se escribe un test básico
- ✅ Cómo usar fixtures
- ✅ Cómo usar mocks
- ✅ Cómo correr un test

Ejecutar:
    pytest tests/test_hello_world.py -v
    pytest tests/test_hello_world.py::TestHelloWorld::test_suma_simple -v
"""

import pytest
from unittest.mock import Mock


class TestHelloWorld:
    """Tests básicos para demostrar cómo se escribe un test"""
    
    # ─────────────────────────────────────────────────────────────────
    # NIVEL 1: Test más simple posible
    # ─────────────────────────────────────────────────────────────────
    
    @pytest.mark.unit
    def test_uno_mas_uno_es_dos(self):
        """
        El test más simple: verificar una operación matemática.
        
        Ejecutar: pytest tests/test_hello_world.py::TestHelloWorld::test_uno_mas_uno_es_dos -v
        """
        # ARRANGE (Preparar)
        numero_1 = 1
        numero_2 = 1
        
        # ACT (Ejecutar)
        resultado = numero_1 + numero_2
        
        # ASSERT (Verificar)
        assert resultado == 2
    
    # ─────────────────────────────────────────────────────────────────
    # NIVEL 2: Test con fixture
    # ─────────────────────────────────────────────────────────────────
    
    @pytest.mark.unit
    def test_usuario_tiene_nombre(self, mock_taller):
        """
        Test usando una fixture (mock_taller).
        
        Ejecutar: pytest tests/test_hello_world.py::TestHelloWorld::test_usuario_tiene_nombre -v
        """
        # ARRANGE
        # mock_taller viene como fixture desde conftest.py
        assert mock_taller is not None
        
        # ACT
        nombre = mock_taller.nombre
        
        # ASSERT
        assert nombre == "Taller Central"
        assert mock_taller.cod == "T001"
    
    # ─────────────────────────────────────────────────────────────────
    # NIVEL 3: Test con mock de BD
    # ─────────────────────────────────────────────────────────────────
    
    @pytest.mark.unit
    def test_guardar_en_base_datos(self, mock_db):
        """
        Test que demuestra cómo usar mock_db.
        
        Ejecutar: pytest tests/test_hello_world.py::TestHelloWorld::test_guardar_en_base_datos -v
        """
        # ARRANGE
        datos = {"id": 1, "nombre": "Test"}
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        # ACT
        mock_db.add(datos)
        mock_db.commit()
        
        # ASSERT
        mock_db.add.assert_called_once_with(datos)
        mock_db.commit.assert_called_once()
    
    # ─────────────────────────────────────────────────────────────────
    # NIVEL 4: Test que valida una excepción
    # ─────────────────────────────────────────────────────────────────
    
    @pytest.mark.unit
    def test_division_por_cero_falla(self):
        """
        Test que verifica que una operación lanza una excepción.
        
        Ejecutar: pytest tests/test_hello_world.py::TestHelloWorld::test_division_por_cero_falla -v
        """
        # ARRANGE & ACT & ASSERT
        with pytest.raises(ZeroDivisionError):
            resultado = 10 / 0
    
    # ─────────────────────────────────────────────────────────────────
    # NIVEL 5: Test async
    # ─────────────────────────────────────────────────────────────────
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_operacion_asincrona(self, async_mock_socket):
        """
        Test que demuestra cómo testear código async.
        
        Ejecutar: pytest tests/test_hello_world.py::TestHelloWorld::test_operacion_asincrona -v
        """
        # ARRANGE
        async_mock_socket.broadcast = Mock()
        
        # ACT
        await async_mock_socket.broadcast({"mensaje": "Hola"})
        
        # ASSERT
        assert async_mock_socket.broadcast.called


# ─────────────────────────────────────────────────────────────────
# Tests DE INTEGRACIÓN (más complejos)
# ─────────────────────────────────────────────────────────────────

class TestIntegracionEjemplo:
    """Tests de integración - flujos más complejos"""
    
    @pytest.mark.integration
    def test_flujo_completo_emergencia(self, mock_db, mock_emergencia, mock_tecnico):
        """
        Test que demuestra un flujo completo:
        1. Cliente reporta emergencia
        2. Sistema busca técnico
        3. Sistema asigna técnico
        
        Ejecutar: pytest tests/test_hello_world.py::TestIntegracionEjemplo::test_flujo_completo_emergencia -v
        """
        # 1. Reportar emergencia
        assert mock_emergencia is not None
        assert mock_emergencia.descripcion == "Falla de motor"
        
        # 2. Buscar técnico disponible
        assert mock_tecnico.estado == "DISPONIBLE"
        
        # 3. Asignar
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        mock_db.add({"emergencia": mock_emergencia, "tecnico": mock_tecnico})
        mock_db.commit()
        
        # Verificar que se guardó
        assert mock_db.add.called
        assert mock_db.commit.called


# ─────────────────────────────────────────────────────────────────
# BONUS: Test parametrizado (mismo test con múltiples datos)
# ─────────────────────────────────────────────────────────────────

class TestParametrizado:
    """Demuestra cómo hacer el mismo test con diferentes datos"""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("numero,esperado", [
        (1, 2),   # 1 + 1 = 2
        (2, 3),   # 2 + 1 = 3
        (5, 6),   # 5 + 1 = 6
        (10, 11), # 10 + 1 = 11
    ])
    def test_sumar_uno(self, numero, esperado):
        """
        Test que se ejecuta 4 veces con diferentes valores.
        
        Ejecutar: pytest tests/test_hello_world.py::TestParametrizado::test_sumar_uno -v
        """
        resultado = numero + 1
        assert resultado == esperado


# ─────────────────────────────────────────────────────────────────
# BONUS: Fixture personalizada
# ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mi_fixture_personalizada():
    """Fixture personalizada para este archivo"""
    print("\n🟢 Setup: Preparando datos")
    datos = {"id": 1, "valor": "test"}
    
    yield datos  # El test recibe estos datos
    
    print("\n🔴 Teardown: Limpiando datos")


class TestFixturePersonalizada:
    """Demuestra cómo usar una fixture personalizada"""
    
    @pytest.mark.unit
    def test_con_fixture_personalizada(self, mi_fixture_personalizada):
        """
        Ejecutar: pytest tests/test_hello_world.py::TestFixturePersonalizada::test_con_fixture_personalizada -v -s
        (el -s muestra los prints)
        """
        assert mi_fixture_personalizada["id"] == 1
        assert mi_fixture_personalizada["valor"] == "test"


# ─────────────────────────────────────────────────────────────────
# Ejecutar este archivo completo:
# ─────────────────────────────────────────────────────────────────
# pytest tests/test_hello_world.py -v
# pytest tests/test_hello_world.py -v -s        (con prints)
# pytest tests/test_hello_world.py::TestHelloWorld -v
# pytest tests/test_hello_world.py -k "test_suma" -v
