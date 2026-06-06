"""
Configuración global de fixtures para todos los tests
Ubicación: backend/tests/conftest.py
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from datetime import datetime
import asyncio


# ─── FIXTURES DE BASE DE DATOS ───────────────────────────────

@pytest.fixture
def mock_db():
    """Mock de la sesión de base de datos"""
    db = Mock(spec=Session)
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    db.delete = Mock()
    return db


# ─── FIXTURES DE AUTENTICACIÓN ───────────────────────────────

@pytest.fixture
def auth_headers_tecnico():
    """Headers con token JWT de técnico"""
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "User-Type": "tecnico",
        "X-User-ID": "T001"
    }


@pytest.fixture
def auth_headers_cliente():
    """Headers con token JWT de cliente"""
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "User-Type": "cliente",
        "X-User-ID": "CLI001"
    }


@pytest.fixture
def auth_headers_admin():
    """Headers con token JWT de administrador"""
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "User-Type": "admin",
        "X-User-ID": "ADMIN001"
    }


# ─── FIXTURES DE WEBSOCKET ───────────────────────────────────

@pytest.fixture
def mock_socket_manager():
    """Mock del gestor de WebSockets"""
    manager = AsyncMock()
    manager.send_personal_message = AsyncMock()
    manager.broadcast = AsyncMock()
    manager.send_to_taller = AsyncMock()
    manager.send_to_cliente = AsyncMock()
    return manager


# ─── FIXTURES DE MODELOS (MOCKS) ─────────────────────────────

@pytest.fixture
def mock_emergencia():
    """Mock de una emergencia completa"""
    emergency = Mock()
    emergency.id = 1
    emergency.descripcion = "Falla de motor"
    emergency.texto_adicional = "No arranca"
    emergency.latitud = -17.7833
    emergency.longitud = -63.1821
    emergency.placaVehiculo = "DEMO-123"
    emergency.estado = "REPORTADO"
    emergency.fecha_creacion = datetime.now()
    emergency.id_cliente = "CLI001"
    emergency.idTaller = None
    emergency.idEstado = 1
    emergency.cotizaciones = []
    return emergency


@pytest.fixture
def mock_tecnico():
    """Mock de un técnico disponible"""
    tech = Mock()
    tech.id = "T001"
    tech.nombre = "Juan Pérez"
    tech.correo = "juan@taller.com"
    tech.estado = "DISPONIBLE"
    tech.latitud = -17.7833
    tech.longitud = -63.1821
    tech.id_taller = "T001"
    tech.telefono = "591-70000000"
    return tech


@pytest.fixture
def mock_tecnico_ocupado():
    """Mock de un técnico que NO está disponible"""
    tech = Mock()
    tech.id = "T002"
    tech.nombre = "Carlos López"
    tech.estado = "EN_RUTA"  # No disponible
    tech.latitud = -17.7850
    tech.longitud = -63.1840
    tech.id_taller = "T001"
    return tech


@pytest.fixture
def mock_taller():
    """Mock de un taller activo"""
    workshop = Mock()
    workshop.cod = "T001"
    workshop.nombre = "Taller Central"
    workshop.estado = "ACTIVO"
    workshop.latitud = -17.7833
    workshop.longitud = -63.1821
    workshop.direccion = "Av. Principal 123"
    workshop.correo = "info@tallercentral.com"
    return workshop


@pytest.fixture
def mock_taller_inactivo():
    """Mock de un taller inactivo"""
    workshop = Mock()
    workshop.cod = "T002"
    workshop.nombre = "Taller Cerrado"
    workshop.estado = "INACTIVO"  # ❌ No disponible
    workshop.latitud = -17.7900
    workshop.longitud = -63.1900
    return workshop


@pytest.fixture
def mock_cotizacion():
    """Mock de una cotización en estado PENDIENTE"""
    quote = Mock()
    quote.id = 1
    quote.idEmergencia = 1
    quote.idTaller = "T001"
    quote.descripcion_servicio = "Cambio de aceite y filtro"
    quote.costo_mano_obra = 50.0
    quote.costo_repuestos = 30.0
    quote.tiempo_estimado_horas = 1
    quote.condiciones = "Pago inmediato"
    quote.estado = "PENDIENTE"
    quote.fecha_creacion = datetime.now()
    return quote


@pytest.fixture
def mock_estado():
    """Mock de un estado (REPORTADO, ASIGNADO, etc)"""
    state = Mock()
    state.id = 1
    state.nombre = "REPORTADO"
    state.descripcion = "Emergencia reportada por cliente"
    return state


@pytest.fixture
def mock_asignacion_tecnico():
    """Mock de una asignación de técnico a emergencia"""
    assignment = Mock()
    assignment.id = 1
    assignment.id_tecnico = "T001"
    assignment.id_emergencia = 1
    assignment.estado = "ASIGNADO"
    assignment.fecha_asignacion = datetime.now()
    assignment.eta_minutos = 10
    return assignment


# ─── FIXTURES DE DATOS PARA CREAR ───────────────────────────

@pytest.fixture
def cotizacion_data():
    """Datos para crear una cotización"""
    return {
        "descripcion_servicio": "Cambio de aceite",
        "costo_mano_obra": 50.0,
        "costo_repuestos": 30.0,
        "tiempo_estimado_horas": 1,
        "condiciones": "Pago inmediato"
    }


@pytest.fixture
def emergencia_data():
    """Datos para reportar una emergencia"""
    return {
        "descripcion": "Falla de motor",
        "texto_adicional": "No arranca",
        "direccion": "Av. Mutex 123",
        "latitud": -17.7833,
        "longitud": -63.1821,
        "placaVehiculo": "DEMO-123",
        "hora": "12:00:00"
    }


# ─── FIXTURES AVANZADAS ──────────────────────────────────────

@pytest.fixture
def mock_db_with_query_chain():
    """Mock de DB que soporta query chains: .query().filter().first()"""
    db = Mock(spec=Session)
    
    # Configurar la cadena: query() -> filter() -> first()
    query_mock = Mock()
    filter_mock = Mock()
    
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = Mock(id=1)
    filter_mock.all.return_value = [Mock(id=1), Mock(id=2)]
    
    db.query.return_value = query_mock
    
    return db


@pytest.fixture
def async_mock_socket():
    """Mock async del socket manager para tests async"""
    manager = AsyncMock()
    manager.send_personal_message = AsyncMock()
    manager.broadcast = AsyncMock()
    manager.send_to_taller = AsyncMock()
    manager.send_to_cliente = AsyncMock()
    return manager


# ─── MARCADORES DE TESTS ─────────────────────────────────────

def pytest_configure(config):
    """Registrar marcadores personalizados"""
    config.addinivalue_line(
        "markers", "unit: marca tests unitarios"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración"
    )
    config.addinivalue_line(
        "markers", "asyncio: marca tests async"
    )
    config.addinivalue_line(
        "markers", "slow: marca tests lentos"
    )


# ─── HELPERS ──────────────────────────────────────────────────

@pytest.fixture
def assert_close_coordinates():
    """Helper para validar coordenadas cercanas"""
    def _assert(lat1, lon1, lat2, lon2, tolerance_km=1):
        """
        Validar que dos coordenadas estén dentro de cierta distancia
        tolerance_km: tolerancia en kilómetros (default: 1 km)
        """
        import math
        
        R = 6371  # Radio terrestre en km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distancia = R * c
        
        assert distancia <= tolerance_km, f"Distancia {distancia}km > tolerancia {tolerance_km}km"
        return True
    
    return _assert


# ─── LIMPIEZA ─────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset automático de mocks después de cada test"""
    yield
    # Cleanup (si es necesario)
