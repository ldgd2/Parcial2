import { Injectable } from '@angular/core';
import { openDB, IDBPDatabase } from 'idb';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { toast } from 'ngx-sonner';

export interface OfflineEmergency {
  id?: number;
  payload: any;
  files?: { file: Blob; name: string }[];
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
        if (!db.objectStoreNames.contains('offline-emergencies')) {
          db.createObjectStore('offline-emergencies', { keyPath: 'id', autoIncrement: true });
        }
      },
    });

    this.setupListeners();
  }

  private setupListeners() {
    window.addEventListener('online', () => {
      console.log('[PWA] Conexión recuperada. Iniciando sincronización...');
      this.syncPendingEmergencies();
    });
  }

  async saveOfflineEmergency(payload: any, files?: File[]) {
    const db = await this.dbPromise;
    
    // Convert File objects to Blobs for IndexedDB storage
    const storedFiles = files?.map(f => ({
      file: new Blob([f], { type: f.type }),
      name: f.name
    }));

    const emergencyData: OfflineEmergency = {
      payload,
      files: storedFiles,
      createdAt: Date.now()
    };

    await db.add('offline-emergencies', emergencyData);
    toast.info('Modo Offline: Emergencia guardada. Se enviará al recuperar conexión.');
  }

  async syncPendingEmergencies() {
    if (this.isSyncing || !navigator.onLine) return;

    this.isSyncing = true;
    try {
      const db = await this.dbPromise;
      const tx = db.transaction('offline-emergencies', 'readwrite');
      const store = tx.objectStore('offline-emergencies');
      const pending = await store.getAll();

      if (pending.length === 0) {
        this.isSyncing = false;
        return;
      }

      toast.loading(`Sincronizando ${pending.length} emergencias offline...`);

      for (const item of pending) {
        try {
          let audioUrl = null;
          let imageUrls: string[] = [];

          // 1. Upload files first if they exist
          if (item.files && item.files.length > 0) {
            const formData = new FormData();
            item.files.forEach((f: any) => {
              formData.append('files', f.file, f.name);
            });

            // Assuming there's a multimedia upload endpoint similar to Flutter
            const uploadRes: any = await this.http.post(`${environment.apiUrl}/gestion-emergencia/upload-multimedia`, formData).toPromise();
            
            if (uploadRes && uploadRes.archivos) {
              uploadRes.archivos.forEach((a: any) => {
                if (a.url.endsWith('.m4a') || a.url.endsWith('.aac') || a.url.endsWith('.wav')) {
                  audioUrl = a.url;
                } else {
                  imageUrls.push(a.url);
                }
              });
            }
          }

          // 2. Modify payload with URLs
          const finalPayload = {
            ...item.payload,
            audio_url: audioUrl || item.payload.audio_url,
            evidencias_urls: imageUrls.length > 0 ? imageUrls : item.payload.evidencias_urls
          };

          // 3. Send final payload
          await this.http.post(`${environment.apiUrl}/gestion-emergencia`, finalPayload).toPromise();

          // 4. Remove from IndexedDB on success
          await store.delete(item.id!);
        } catch (err) {
          console.error(`Error sincronizando emergencia offline ${item.id}`, err);
          // Keep it in DB if it failed to retry later
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
