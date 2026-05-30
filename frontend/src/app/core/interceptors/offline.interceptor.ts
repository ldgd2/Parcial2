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

  // Verificamos si estamos sin internet antes de intentar la petición
  if (!navigator.onLine && req.method === 'POST') {
    // Si la petición es para crear emergencia (que incluye multimedia) o en general POST
    if (req.url.includes('/gestion-emergencia') || req.url.includes('/reportar')) {
      console.log('[PWA Interceptor] Detectado sin red. Guardando payload en IndexedDB...');
      
      // Intentamos extraer los archivos del FormData si aplica
      let files: File[] = [];
      let payload: any = req.body;

      if (req.body instanceof FormData) {
        payload = {};
        req.body.forEach((value, key) => {
          if (value instanceof File) {
            files.push(value);
          } else {
            payload[key] = value;
          }
        });
      }

      // Guardamos localmente
      offlineSync.saveOfflineEmergency(payload, files);

      // Simulamos respuesta exitosa para no romper la UI
      return of(new HttpResponse({ status: 200, body: { message: 'Guardado offline exitoso' } }));
    }
  }

  // Si hay red o es un método distinto a POST, pasa normalmente
  return next(req).pipe(
    catchError((error) => {
      // Fallback: Si falló por error de red (status 0) a pesar de onLine = true
      if (error.status === 0 && req.method === 'POST') {
        if (req.url.includes('/gestion-emergencia') || req.url.includes('/reportar')) {
          let files: File[] = [];
          let payload: any = req.body;
          if (req.body instanceof FormData) {
            payload = {};
            req.body.forEach((value, key) => {
              if (value instanceof File) {
                files.push(value);
              } else {
                payload[key] = value;
              }
            });
          }
          offlineSync.saveOfflineEmergency(payload, files);
          return of(new HttpResponse({ status: 200, body: { message: 'Guardado offline tras fallo de red' } }));
        }
      }
      return throwError(() => error);
    })
  );
};
