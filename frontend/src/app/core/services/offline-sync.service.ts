import { Injectable } from '@angular/core';
import { openDB, IDBPDatabase } from 'idb';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { toast } from 'ngx-sonner';

export interface OfflineRequest {
  id?: number;
  url: string;
  method: string;
  payload: any;
  files?: { file: Blob; name: string; fieldName: string }[];
  headers?: { [key: string]: string };
  createdAt: number;
}

@Injectable({
  providedIn: 'root'
})
export class OfflineSyncService {
  private dbPromise: Promise<IDBPDatabase>;
  private isSyncing = false;

  constructor(private http: HttpClient) {
    this.dbPromise = openDB('taller-pwa-db', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('offline-requests')) {
          db.createObjectStore('offline-requests', { keyPath: 'id', autoIncrement: true });
        }
      },
    });

    this.setupListeners();
  }

  private setupListeners() {
    window.addEventListener('online', () => {
      console.log('[PWA] Conexión recuperada. Iniciando sincronización...');
      this.syncPendingRequests();
    });
  }

  async saveOfflineRequest(url: string, method: string, payload: any, headers?: any, files?: {file: File, fieldName: string}[]) {
    const db = await this.dbPromise;
    
    const storedFiles = files?.map(f => ({
      file: new Blob([f.file], { type: f.file.type }),
      name: f.file.name,
      fieldName: f.fieldName
    }));

    const requestData: OfflineRequest = {
      url,
      method,
      headers,
      payload,
      files: storedFiles,
      createdAt: Date.now()
    };

    await db.add('offline-requests', requestData);
    toast.info('Se enviará tu petición cuando haya conexión');
  }

  async syncPendingRequests() {
    if (this.isSyncing || !navigator.onLine) return;

    this.isSyncing = true;
    try {
      const db = await this.dbPromise;
      const tx = db.transaction('offline-requests', 'readwrite');
      const store = tx.objectStore('offline-requests');
      const pending = await store.getAll();

      if (pending.length === 0) {
        this.isSyncing = false;
        return;
      }

      toast.loading(`Sincronizando ${pending.length} peticiones offline...`);

      for (const item of pending) {
        try {
          let bodyData: any = item.payload;

          // Si había archivos (es un form-data)
          if (item.files && item.files.length > 0) {
            const formData = new FormData();
            
            // Añadir payload original
            if (item.payload) {
              Object.keys(item.payload).forEach(k => formData.append(k, item.payload[k]));
            }
            
            item.files.forEach((f: any) => {
              formData.append(f.fieldName, f.file, f.name);
            });
            bodyData = formData;
          }

          const httpHeaders: any = { ...item.headers };

          // Enviar petición original reconstruida
          await this.http.request(item.method, item.url, {
            body: bodyData,
            headers: httpHeaders
          }).toPromise();

          // Remover de IndexedDB si fue exitoso
          await store.delete(item.id!);
        } catch (err) {
          console.error(`Error sincronizando petición offline ${item.id}`, err);
        }
      }
      
      toast.dismiss();
      toast.success('Sincronización PWA completada exitosamente.');

    } catch (e) {
      console.error('Error in sync process', e);
    } finally {
      this.isSyncing = false;
    }
  }
}
