import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpEvent, HttpResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { OfflineSyncService } from '../services/offline-sync.service';
import { Observable, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export const offlineInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const offlineSync = inject(OfflineSyncService);

  // Ignorar las peticiones de login para evitar falsos positivos offline sin token
  if (req.url.includes('/auth/login') || req.url.includes('/auth/register')) {
    return next(req);
  }

  // Verificamos si estamos sin internet antes de intentar la petición
  if (!navigator.onLine && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
    console.log(`[PWA Interceptor] Detectado sin red. Guardando payload de ${req.method} en IndexedDB...`);
    
    // Intentamos extraer los archivos del FormData si aplica
    let files: {file: File, fieldName: string}[] = [];
    let payload: any = req.body;

    if (req.body instanceof FormData) {
      payload = {};
      req.body.forEach((value, key) => {
        if (value instanceof File) {
          files.push({file: value, fieldName: key});
        } else {
          payload[key] = value;
        }
      });
    }

    const idempotencyKey = crypto.randomUUID();
    const headers: { [key: string]: string } = {};
    req.headers.keys().forEach(key => {
      headers[key] = req.headers.get(key) || '';
    });
    headers['Idempotency-Key'] = idempotencyKey;

    offlineSync.saveOfflineRequest(req.url, req.method, payload, headers, files);

    // Retornamos éxito simulado genérico
    return of(new HttpResponse({ status: 200, body: { message: 'Guardado offline exitoso' } }));
  }

  // Si hay red o es un método distinto a POST, pasa normalmente
  return next(req).pipe(
    catchError((error) => {
      // Fallback: Si falló por error de red (status 0) a pesar de onLine = true
      if (error.status === 0 && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
        let files: {file: File, fieldName: string}[] = [];
        let payload: any = req.body;
        if (req.body instanceof FormData) {
          payload = {};
          req.body.forEach((value, key) => {
            if (value instanceof File) {
              files.push({file: value, fieldName: key});
            } else {
              payload[key] = value;
            }
          });
        }
        
        const idempotencyKey = crypto.randomUUID();
        const headers: { [key: string]: string } = {};
        req.headers.keys().forEach(key => {
          headers[key] = req.headers.get(key) || '';
        });
        headers['Idempotency-Key'] = idempotencyKey;

        offlineSync.saveOfflineRequest(req.url, req.method, payload, headers, files);
        return of(new HttpResponse({ status: 200, body: { message: 'Guardado offline tras fallo de red' } }));
      }
      return throwError(() => error);
    })
  );
};
