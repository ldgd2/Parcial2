import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.ext.asyncio import AsyncSession
import os
from app.core.socket_manager import manager
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.repositories.fcm_token_repo import FCMTokenRepository
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.repositories.usuario_repo import UsuarioRepository
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.repositories.cliente_repo import ClienteRepository

class NotificationService:
    _initialized = False

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            # Obtener la ruta base del proyecto (app/) de forma dinámica
            # __file__ es .../app/services/notification_service.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_app_dir = os.path.dirname(current_dir) # .../app
            
            cred_path = os.path.join(
                base_app_dir, 
                "core", 
                "notification", 
                "universidadtest-cccae-firebase-adminsdk-fbsvc-178b0378fd.json"
            )

            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                print("Firebase Admin SDK inicializado correctamente (Ruta Relativa).")
            else:
                print(f"Error: No se encontró el archivo de credenciales en {cred_path}")

    @staticmethod
    async def registrar_token(db: AsyncSession, user_id: int, token: str, dispositivo: str = "android", role: str = "cliente"):
        # 1. Registrar en la tabla centralizada FCMToken
        fcm_repo = FCMTokenRepository(db)
        await fcm_repo.delete_by_token(token)
        
        obj_in = {
            "token": token,
            "dispositivo": dispositivo
        }
        
        # Asignar según rol
        if role == "cliente":
            obj_in["idCliente"] = user_id
        else:
            obj_in["idUsuario"] = user_id
            
        nuevo_fcm = await fcm_repo.create(obj_in=obj_in)

        # 2. Registrar directamente en la tabla específica para visibilidad inmediata
        if role == "cliente":
            cliente_repo = ClienteRepository(db)
            cliente = await cliente_repo.get(user_id)
            if cliente:
                await cliente_repo.update(db_obj=cliente, obj_in={"fcm_token": token})
        else:
            usuario_repo = UsuarioRepository(db)
            usuario = await usuario_repo.get(user_id)
            if usuario:
                await usuario_repo.update(db_obj=usuario, obj_in={"fcm_token": token})

        await db.commit()
        return nuevo_fcm

    @staticmethod
    async def enviar_notificacion_usuario(db: AsyncSession, user_id: int, titulo: str, cuerpo: str, data: dict = None):
        """Envía una notificación push a todos los dispositivos de un usuario."""
        # 0. Notificación en tiempo real via WebSocket
        await manager.send_personal_message({
            "type": "notification",
            "title": titulo,
            "body": cuerpo,
            "data": data
        }, str(user_id))

        NotificationService.initialize()
        
        # Obtener tokens del usuario o cliente
        fcm_repo = FCMTokenRepository(db)
        fcm_tokens = await fcm_repo.get_by_user_or_client(user_id)
        tokens = [t.token for t in fcm_tokens]
        
        if not tokens:
            print(f"DEBUG NOTIFICACION: No se encontraron tokens para el usuario/cliente ID {user_id}")
            return 0
        
        print(f"DEBUG NOTIFICACION: Enviando a {len(tokens)} tokens para ID {user_id}")
        
        # Asegurar que todos los valores en 'data' sean strings (Requisito de FCM)
        clean_data = {}
        if data:
            for k, v in data.items():
                clean_data[str(k)] = str(v)

        # Enviar cada mensaje individualmente pero agrupado (Multicast moderno)
        messages = [
            messaging.Message(
                notification=messaging.Notification(
                    title=titulo,
                    body=cuerpo,
                ),
                data=clean_data,
                token=token,
            )
            for token in tokens
        ]
        
        try:
            response = messaging.send_each(messages)
            print(f"Notificación enviada: {response.success_count} exitosas, {response.failure_count} fallidas.")
            return response.success_count
        except Exception as e:
            print(f"ERROR CRITICO FIREBASE: {str(e)}")
            return 0

    @staticmethod
    async def enviar_notificacion_topic(topic: str, titulo: str, cuerpo: str, data: dict = None):
        """Envía una notificación a todos los suscritos a un tópico (ej: 'todos', 'tecnicos')."""
        NotificationService.initialize()
        
        # Asegurar que todos los valores en 'data' sean strings
        clean_data = {}
        if data:
            for k, v in data.items():
                clean_data[str(k)] = str(v)

        message = messaging.Message(
            notification=messaging.Notification(
                title=titulo,
                body=cuerpo,
            ),
            data=clean_data,
            topic=topic,
        )
        
        response = messaging.send(message)
        print(f"Notificación enviada al tópico {topic}: {response}")
        return response

    @staticmethod
    async def enviar_notificacion_directa(token: str, titulo: str, cuerpo: str, data: dict = None):
        """Envía una notificación push a un token específico."""
        NotificationService.initialize()
        
        # Asegurar que todos los valores en 'data' sean strings
        clean_data = {}
        if data:
            for k, v in data.items():
                clean_data[str(k)] = str(v)

        message = messaging.Message(
            notification=messaging.Notification(
                title=titulo,
                body=cuerpo,
            ),
            data=clean_data,
            token=token,
        )
        
        response = messaging.send(message)
        print(f"Notificación directa enviada: {response}")
        return response
