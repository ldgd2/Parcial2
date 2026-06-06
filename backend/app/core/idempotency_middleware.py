import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.db.session import AsyncSessionLocal
from app.db.idempotency_key import IdempotencyKey
from sqlalchemy import select

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Solo aplicar a métodos que mutan estado
        if request.method not in ["POST", "PUT", "DELETE", "PATCH"]:
            return await call_next(request)

        idempotency_key = request.headers.get("idempotency-key")
        if not idempotency_key:
            return await call_next(request)

        # Verificar en base de datos si la llave ya existe
        async with AsyncSessionLocal() as db:
            stmt = select(IdempotencyKey).where(IdempotencyKey.key == idempotency_key)
            result = await db.execute(stmt)
            existing_key = result.scalar_one_or_none()

            if existing_key:
                if existing_key.status == "completed":
                    # Retornar la respuesta guardada
                    return JSONResponse(
                        content=existing_key.response_body,
                        status_code=existing_key.response_code
                    )
                elif existing_key.status == "processing":
                    # En procesamiento (ej. doble click rápido)
                    return JSONResponse(
                        content={"detail": "Request already in progress"},
                        status_code=409
                    )

            # Si no existe, crearlo como processing
            new_key = IdempotencyKey(
                key=idempotency_key,
                method=request.method,
                path=request.url.path,
                status="processing"
            )
            db.add(new_key)
            await db.commit()

        # Ejecutar la ruta real
        response = await call_next(request)

        # Solo guardar respuestas de éxito o errores cliente controlados
        # No guardamos errores de servidor (5xx) para permitir reintentos
        if response.status_code < 500:
            # Leer el body de la respuesta
            res_body = b""
            async for chunk in response.body_iterator:
                res_body += chunk
            
            try:
                json_body = json.loads(res_body.decode())
            except:
                json_body = {"detail": "non-json response"}

            # Actualizar llave a completed
            async with AsyncSessionLocal() as db:
                stmt = select(IdempotencyKey).where(IdempotencyKey.key == idempotency_key)
                result = await db.execute(stmt)
                db_key = result.scalar_one()
                db_key.status = "completed"
                db_key.response_code = response.status_code
                db_key.response_body = json_body
                await db.commit()

            # Reconstruir la respuesta para que el cliente la reciba
            return JSONResponse(
                content=json_body,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

        # Si falló feo (500), lo borramos para que pueda reintentar
        async with AsyncSessionLocal() as db:
            stmt = select(IdempotencyKey).where(IdempotencyKey.key == idempotency_key)
            result = await db.execute(stmt)
            db_key = result.scalar_one_or_none()
            if db_key:
                await db.delete(db_key)
                await db.commit()

        return response
