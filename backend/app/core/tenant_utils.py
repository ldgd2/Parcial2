import re

def get_tenant_schema_name(nombre_taller: str, codigo_taller: str) -> str:
    """
    Genera el nombre del esquema para un tenant en el formato: {nombreTaller}_{codigoTaller}
    Slugifica el nombre para evitar caracteres inválidos en PostgreSQL.
    """
    # Convertir a minúsculas, reemplazar espacios con guiones bajos y quitar caracteres no alfanuméricos
    clean_name = re.sub(r'[^a-z0-9_]', '', nombre_taller.lower().replace(' ', '_'))
    return f"{clean_name}_{codigo_taller.lower()}"
