#!/bin/bash

# =================================================================
# 🚀 ULTRA-SETUP VPS PREMIUM - TALLER AI
# =================================================================
# Versión: 3.0 (PostgreSQL Admin Integration)
# =================================================================

# --- CONFIGURACIÓN ---
PYTHON_VER="3.12.3"
DB_PACKAGE="postgresql-16" # Cambiado a 16 por estabilidad, o usar la solicitada si está en repo
DB_VERSION_REQ="18.3-1.pgdg24.04+1" 
VENV_NAME=".venv"
ENV_FILE=".env"

# Colores Premium
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# --- ANIMACIONES Y UI ---



progress_bar() {
    local duration=$1
    local width=40
    local progress=0
    while [ $progress -le 100 ]; do
        local filled=$((progress * width / 100))
        local empty=$((width - filled))
        printf "\r${CYAN} Progreso: [${GREEN}"
        printf "%${filled}s" | tr ' ' '█'
        printf "${NC}"
        printf "%${empty}s" | tr ' ' '░'
        printf "${CYAN}] %d%%${NC}" "$progress"
        progress=$((progress + 5))
        sleep 0.1
    done
    echo ""
}

show_banner() {
    clear
    echo -e "${MAGENTA}${BOLD}"
    echo "  ██████╗ ███████╗████████╗██╗   ██╗██████╗ "
    echo "  ██╔══██╗██╔════╝╚══██╔══╝██║   ██║██╔══██╗"
    echo "  ██████╔╝█████╗     ██║   ██║   ██║██████╔╝"
    echo "  ██╔═══╝ ██╔══╝     ██║   ██║   ██║██╔═══╝ "
    echo "  ██║     ███████╗   ██║   ╚██████╔╝██║     "
    echo "  ╚═╝     ╚══════╝   ╚═╝    ╚═════╝ ╚═╝     "
    echo -e "         ${CYAN}ADMIN DEPLOYMENT v3.0${NC}\n"
}

# --- INICIO DEL SCRIPT ---

show_banner
echo -e "${YELLOW}${BOLD}>>> INICIANDO CONFIGURACIÓN NIVEL ADMINISTRADOR${NC}"
progress_bar

# 1. CAPTURA DE DATOS INTERACTIVA
echo -ne "\n${BLUE}${BOLD}[ DETECCIÓN DE RED ]${NC}\n  🔍 Detectando IP pública del servidor..."
VPS_IP=$(curl -4 -s ifconfig.me)
echo -e " ${GREEN}$VPS_IP${NC}"

echo -e "\n${BLUE}${BOLD}[ CONFIGURACIÓN DE BASE DE DATOS ]${NC}"
read -p "  👤 Ingrese Usuario de DB [postgres]: " DB_USER
if [ -z "$DB_USER" ]; then DB_USER="postgres"; fi

while true; do
    read -s -p "  🔑 Ingrese Contraseña para $DB_USER: " DB_PASS
    echo ""
    read -s -p "  🔄 Repita la Contraseña: " DB_PASS_CONF
    echo ""
    if [ "$DB_PASS" == "$DB_PASS_CONF" ]; then
        if [ -z "$DB_PASS" ]; then
            echo -e "  ${RED}❌ La contraseña no puede estar vacía. Intente de nuevo.${NC}"
        else
            echo -e "  ${GREEN}✅ Contraseñas coinciden.${NC}"
            break
        fi
    else
        echo -e "  ${RED}❌ Las contraseñas no coinciden. Intente de nuevo.${NC}"
    fi
done

echo -e "\n${BLUE}${BOLD}[ CONEXIÓN BASE DE DATOS ]${NC}"
echo -e "  1) Localhost (127.0.0.1) - Recomendado si el backend está en el mismo server"
echo -e "  2) IP del VPS ($VPS_IP)"
read -p "  Seleccione opción [1]: " HOST_CHOICE

if [ "$HOST_CHOICE" == "2" ]; then
    DB_HOST=$VPS_IP
else
    DB_HOST="127.0.0.1"
fi

# 2. ACTUALIZACIÓN DEL SISTEMA Y ZONA HORARIA
echo -e "\n${YELLOW}>>> 1. Configurando Zona Horaria (La Paz) y Actualizando sistema...${NC}"
sudo timedatectl set-timezone America/La_Paz

# Para evitar prompts interactivos en Ubuntu durante upgrade
export DEBIAN_FRONTEND=noninteractive
sudo apt update
sudo apt upgrade -yq
echo -e "${GREEN}   ✅ Hora configurada (UTC-4) y Sistema al día.${NC}"

# 3. INSTALAR POSTGRESQL Y CONFIGURAR SUPERUSER
echo -e "\n${YELLOW}>>> 2. Instalando y Configurando PostgreSQL ($DB_VERSION_REQ)...${NC}"
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update > /dev/null 2>&1

# Instalación de servidor y cliente
sudo apt install -yq postgresql postgresql-contrib postgresql-client build-essential jq

echo -e "   🐘 Configurando usuario '$DB_USER' en PostgreSQL..."
sudo systemctl start postgresql

if [ "$DB_USER" == "postgres" ]; then
    # Actualizar contraseña del superusuario por defecto
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '$DB_PASS';" > /dev/null 2>&1
else
    # Crear usuario con permisos de SUPERUSER (Administrador total)
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH SUPERUSER PASSWORD '$DB_PASS';" > /dev/null 2>&1
fi

# Crear base de datos por defecto si no existe
DB_NAME_VAL="taller_db"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME_VAL OWNER $DB_USER;" > /dev/null 2>&1
echo -e "${GREEN}   ✅ Usuario '$DB_USER' (SUPERUSER) listo y Base de Datos $DB_NAME_VAL creada.${NC}"

# 4. INSTALAR PYTHON 3.12.3
echo -e "\n${YELLOW}>>> 3. Instalando Python $PYTHON_VER vía pyenv...${NC}"
if [ ! -d "$HOME/.pyenv" ]; then
    curl https://pyenv.run | bash
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

if ! grep -q "pyenv" "$HOME/.bashrc"; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
fi

echo -e "   ⚙️  Compilando Python $PYTHON_VER (paciencia...)"
pyenv install $PYTHON_VER -s
pyenv global $PYTHON_VER

# 5. ENTORNO VIRTUAL Y DEPENDENCIAS
echo -e "\n${YELLOW}>>> 4. Configurando Entorno Virtual y Reqs...${NC}"
python -m venv $VENV_NAME
source $VENV_NAME/bin/activate

pip install --upgrade pip
pip install -r backend/requirements.txt rich questionary
echo -e "${GREEN}   ✅ Entorno listo.${NC}"

# 6. CONFIGURAR .ENV
echo -e "\n${YELLOW}>>> 5. Generando archivo $ENV_FILE con tu configuración...${NC}"

cat > $ENV_FILE << EOL
APP_HOST=$VPS_IP
APP_PORT_BACKEND=8000
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_HOST=$DB_HOST
DB_PORT=5432
DB_NAME=$DB_NAME_VAL
EOL

echo -e "${GREEN}   ✅ Archivo .env configurado exitosamente.${NC}"

# 7. FINALIZACIÓN Y LANZAMIENTO
echo -e "\n${MAGENTA}${BOLD}=================================================${NC}"
echo -e "${GREEN}${BOLD}   SISTEMA LISTO Y AUTORIZADO${NC}"
echo -e "${MAGENTA}${BOLD}=================================================${NC}"
progress_bar

echo -e "${CYAN}🚀 Lanzando Navaja Suiza (taller.py)...${NC}"
sleep 1
python taller.py
