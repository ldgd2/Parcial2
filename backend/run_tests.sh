#!/bin/bash
# Script para ejecutar pruebas unitarias
# Ubicación: backend/run_tests.sh
# Uso: ./run_tests.sh [opción]
#
# Opciones:
#   all             Ejecutar todos los tests
#   cu15            Tests de CU15 (Auxilio en Tiempo Real)
#   cu17            Tests de CU17 + CU18 (Cotizaciones)
#   unit            Solo tests unitarios
#   coverage        Tests con reporte de cobertura
#   watch           Ejecutar tests en modo watch (vuelve a ejecutar cuando cambias archivos)

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir encabezados
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}\n"
}

# Validar que estamos en el directorio backend
if [ ! -f "pytest.ini" ]; then
    echo -e "${RED}Error: ejecutar desde backend/${NC}"
    echo "cd backend && ./run_tests.sh"
    exit 1
fi

# Activar venv si existe
if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate 2>/dev/null
    echo -e "${GREEN}✓ Virtual environment activado${NC}"
fi

OPTION=${1:-all}

case $OPTION in
    all)
        print_header "Ejecutando TODOS los tests"
        pytest -v --tb=short
        ;;
    
    cu15)
        print_header "Tests de CU15: Gestión de Auxilio a Tiempo Real"
        pytest app/packages/gestion_emergencias_solicitudes/modules/auxilio_tiempo_real/tests/ -v
        ;;
    
    cu17)
        print_header "Tests de CU17+CU18: Gestionar Cotizaciones"
        pytest app/packages/gestion_emergencias_solicitudes/modules/cotizaciones/tests/ -v
        ;;
    
    unit)
        print_header "Ejecutando solo tests UNITARIOS"
        pytest -m unit -v --tb=short
        ;;
    
    integration)
        print_header "Ejecutando solo tests de INTEGRACIÓN"
        pytest -m integration -v --tb=short
        ;;
    
    coverage)
        print_header "Ejecutando tests CON COBERTURA"
        pytest --cov=app --cov-report=html --cov-report=term-missing -v
        echo -e "\n${GREEN}✓ Reporte de cobertura generado en: htmlcov/index.html${NC}"
        ;;
    
    coverage-report)
        print_header "Abriendo reporte de cobertura"
        if [ -f "htmlcov/index.html" ]; then
            open htmlcov/index.html || xdg-open htmlcov/index.html || start htmlcov/index.html
        else
            echo -e "${YELLOW}Primero ejecutar: ./run_tests.sh coverage${NC}"
        fi
        ;;
    
    watch)
        print_header "Modo WATCH: Ejecutar tests automáticamente al cambiar archivos"
        pytest-watch app/packages/gestion_emergencias_solicitudes/ -- -v --tb=short
        ;;
    
    *)
        echo -e "${YELLOW}Opción desconocida: $OPTION${NC}"
        echo ""
        echo "Uso: ./run_tests.sh [opción]"
        echo ""
        echo "Opciones disponibles:"
        echo "  all              Ejecutar todos los tests"
        echo "  cu15             Tests de CU15 (Auxilio en Tiempo Real)"
        echo "  cu17             Tests de CU17 + CU18 (Cotizaciones)"
        echo "  unit             Solo tests unitarios"
        echo "  integration      Solo tests de integración"
        echo "  coverage         Tests con reporte de cobertura"
        echo "  coverage-report  Abrir reporte de cobertura"
        echo "  watch            Modo watch (se ejecuta al cambiar archivos)"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✓ Pruebas completadas${NC}\n"
