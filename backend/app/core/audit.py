from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.models.bitacora import Bitacora
from app.core.context import get_user_context, get_ip_context
from datetime import date, datetime, time
from decimal import Decimal
import asyncio
from app.core.socket_manager import manager

def json_serializable(obj):
    """Convierte objetos no serializables en JSON a strings o floats."""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def get_model_changes(instance):
    """Obtiene los cambios (valores nuevos y viejos) de una instancia."""
    changes = {}
    from sqlalchemy import inspect
    
    state = inspect(instance)
    for attr in state.mapper.column_attrs:
        history = state.get_history(attr.key, True)
        if history.has_changes():
            changes[attr.key] = {
                "antes": json_serializable(history.deleted[0]) if history.deleted else None,
                "despues": json_serializable(history.added[0]) if history.added else None
            }
    return changes

def get_instance_dict(instance):
    """Convierte una instancia en un diccionario de valores serializables."""
    from sqlalchemy import inspect
    state = inspect(instance)
    return {attr.key: json_serializable(getattr(instance, attr.key)) for attr in state.mapper.column_attrs}

def get_primary_key(instance):
    """Obtiene el valor de la clave primaria de una instancia."""
    from sqlalchemy import inspect
    state = inspect(instance)
    pk_values = [getattr(instance, attr.key) for attr in state.mapper.primary_key]
    return ", ".join(map(str, pk_values)) if pk_values else "N/A"

def register_audit_listeners(Base):
    """Registra los listeners de auditoría para todos los modelos que heredan de Base."""
    
    @event.listens_for(Session, "after_flush")
    def receive_after_flush(session, flush_context):
        # Usamos una bandera en la sesión para evitar recursividad si el listener
        # vuelve a dispararse por los session.add(entry) de abajo
        if getattr(session, "_audit_active", False):
            return
            
        entries = []
        
        try:
            session._audit_active = True
            
            # INSERT
            for instance in session.new:
                if not hasattr(instance, "__tablename__") or instance.__tablename__ == "bitacora":
                    continue
                
                entries.append(Bitacora(
                    idUsuario=get_user_context(),
                    accion="INSERT",
                    tabla=instance.__tablename__,
                    registro_id=get_primary_key(instance),
                    detalles={"nuevo": get_instance_dict(instance)},
                    ip=get_ip_context()
                ))

            # UPDATE
            for instance in session.dirty:
                if not hasattr(instance, "__tablename__") or instance.__tablename__ == "bitacora":
                    continue
                
                changes = get_model_changes(instance)
                if changes:
                    entries.append(Bitacora(
                        idUsuario=get_user_context(),
                        accion="UPDATE",
                        tabla=instance.__tablename__,
                        registro_id=get_primary_key(instance),
                        detalles=changes,
                        ip=get_ip_context()
                    ))

            # DELETE
            for instance in session.deleted:
                if not hasattr(instance, "__tablename__") or instance.__tablename__ == "bitacora":
                    continue
                
                entries.append(Bitacora(
                    idUsuario=get_user_context(),
                    accion="DELETE",
                    tabla=instance.__tablename__,
                    registro_id=get_primary_key(instance),
                    detalles={"eliminado": get_instance_dict(instance)},
                    ip=get_ip_context()
                ))

            for entry in entries:
                session.add(entry)
                
                # Broadcast real-time updates for specific tables
                if entry.tabla in ["emergencia", "pago"]:
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.create_task(manager.broadcast({
                                "type": "db_update",
                                "table": entry.tabla,
                                "id": entry.registro_id,
                                "action": entry.accion
                            }))
                    except Exception as e:
                        print(f"Error broadcasting: {e}")
                        
        finally:
            session._audit_active = False
