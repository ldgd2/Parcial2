import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Tenant {
  cod: string;
  nombre: string;
  direccion: string;
  estado: string;
  plan_id?: number;
  admin_correo?: string;
}

@Injectable({
  providedIn: 'root'
})
export class SaasService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/saas/tenants`;

  getTenants(): Observable<Tenant[]> {
    return this.http.get<Tenant[]>(this.apiUrl);
  }

  createTenant(tenant: Partial<Tenant>): Observable<Tenant> {
    return this.http.post<Tenant>(this.apiUrl, tenant);
  }

  updateTenant(cod: string, tenant: Partial<Tenant>): Observable<Tenant> {
    return this.http.put<Tenant>(`${this.apiUrl}/${cod}`, tenant);
  }

  updateStatus(cod: string, estado: string): Observable<Tenant> {
    return this.http.patch<Tenant>(`${this.apiUrl}/${cod}/status`, { estado });
  }
}
