import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

// ── Tenant ──────────────────────────────────────────────────────────────────
export interface Tenant {
  cod: string;
  nombre: string;
  direccion: string;
  estado: string;
  plan_id?: number;
  plan_nombre?: string;
  admin_correo?: string;
  total_usuarios?: number;
  total_tecnicos?: number;
}

// ── Plan ─────────────────────────────────────────────────────────────────────
export interface Plan {
  id: number;
  nombre: string;
  descripcion?: string;
  precio_mensual: number;
  max_sucursales: number;
  max_tecnicos: number;
  max_admins_sucursal: number;
  total_talleres?: number;
}

export interface PlanCreate {
  nombre: string;
  descripcion?: string;
  precio_mensual: number;
  max_sucursales: number;
  max_tecnicos: number;
  max_admins_sucursal: number;
}

// ── Stats ─────────────────────────────────────────────────────────────────────
export interface SaasStats {
  total_tenants: number;
  tenants_activos: number;
  tenants_suspendidos: number;
  tenants_cancelados: number;
  total_usuarios: number;
  total_tecnicos: number;
  ingresos_mensuales: number;
}

// ── System Health ─────────────────────────────────────────────────────────────
export interface SaludSistema {
  estado: string;
  db_conectada: boolean;
  total_talleres: number;
  total_usuarios: number;
  total_tecnicos: number;
  version: string;
  timestamp: string;
}

// ── Audit Log ─────────────────────────────────────────────────────────────────
export interface BitacoraEntry {
  id: number;
  accion: string;
  tabla?: string;
  registro_id?: string;
  ip?: string;
  fecha?: string;
  idUsuario?: number;
}

// ── Restrictions ──────────────────────────────────────────────────────────────
export interface Restricciones {
  registro_publico_habilitado: boolean;
  nuevos_talleres_habilitados: boolean;
  modo_mantenimiento: boolean;
  max_emergencias_simultaneas: number;
  notificaciones_push_habilitadas: boolean;
  ia_clasificacion_habilitada: boolean;
  stripe_habilitado: boolean;
  logs_verboso: boolean;
}

// ── Tenant Users ──────────────────────────────────────────────────────────────
export interface TenantUser {
  id: number;
  nombre: string;
  apellido?: string;
  correo: string;
  telefono?: string;
  estado: string;
  tipo: 'ADMINISTRATIVO' | 'TECNICO';
  rol_nombre?: string;
}

export interface TenantUserCreate {
  nombre: string;
  apellido?: string;
  correo: string;
  contrasena: string;
  rol_id: number;
  telefono?: string;
}

@Injectable({ providedIn: 'root' })
export class SaasService {
  private http = inject(HttpClient);
  private tenantsUrl = `${environment.apiUrl}/saas/tenants`;
  private sistemaUrl = `${environment.apiUrl}/saas/sistema`;

  // ── Tenants ────────────────────────────────────────────────────────────────
  getTenants(): Observable<Tenant[]> {
    return this.http.get<Tenant[]>(this.tenantsUrl);
  }

  getTenant(cod: string): Observable<Tenant> {
    return this.http.get<Tenant>(`${this.tenantsUrl}/${cod}`);
  }

  createTenant(tenant: any): Observable<Tenant> {
    return this.http.post<Tenant>(this.tenantsUrl, tenant);
  }

  updateTenant(cod: string, tenant: Partial<Tenant>): Observable<Tenant> {
    return this.http.put<Tenant>(`${this.tenantsUrl}/${cod}`, tenant);
  }

  updateStatus(cod: string, estado: string): Observable<Tenant> {
    return this.http.patch<Tenant>(`${this.tenantsUrl}/${cod}/status`, { estado });
  }

  getStats(): Observable<SaasStats> {
    return this.http.get<SaasStats>(`${this.tenantsUrl}/stats`);
  }

  // ── Tenant Users ───────────────────────────────────────────────────────────
  getTenantUsuarios(cod: string): Observable<TenantUser[]> {
    return this.http.get<TenantUser[]>(`${this.tenantsUrl}/${cod}/usuarios`);
  }

  crearUsuarioEnTenant(cod: string, data: TenantUserCreate): Observable<TenantUser> {
    return this.http.post<TenantUser>(`${this.tenantsUrl}/${cod}/usuarios`, data);
  }

  cambiarEstadoUsuarioTenant(cod: string, tipo: string, id: number, estado: string): Observable<any> {
    return this.http.patch(`${this.tenantsUrl}/${cod}/usuarios/${tipo}/${id}/status`, { estado });
  }

  resetPasswordUsuarioTenant(cod: string, tipo: string, id: number, nueva_contrasena: string): Observable<any> {
    return this.http.patch(`${this.tenantsUrl}/${cod}/usuarios/${tipo}/${id}/reset-password`, { nueva_contrasena });
  }

  // ── Planes (CRUD completo via sistema) ────────────────────────────────────
  getPlanes(): Observable<Plan[]> {
    return this.http.get<Plan[]>(`${this.sistemaUrl}/planes`);
  }

  createPlan(data: PlanCreate): Observable<Plan> {
    return this.http.post<Plan>(`${this.sistemaUrl}/planes`, data);
  }

  updatePlan(id: number, data: Partial<PlanCreate>): Observable<Plan> {
    return this.http.put<Plan>(`${this.sistemaUrl}/planes/${id}`, data);
  }

  deletePlan(id: number): Observable<any> {
    return this.http.delete(`${this.sistemaUrl}/planes/${id}`);
  }

  // ── Sistema ────────────────────────────────────────────────────────────────
  getSalud(): Observable<SaludSistema> {
    return this.http.get<SaludSistema>(`${this.sistemaUrl}/salud`);
  }

  getAuditLog(params?: { limit?: number; offset?: number; accion?: string; tabla?: string }): Observable<BitacoraEntry[]> {
    const qp = new URLSearchParams();
    if (params?.limit) qp.set('limit', String(params.limit));
    if (params?.offset) qp.set('offset', String(params.offset));
    if (params?.accion) qp.set('accion', params.accion);
    if (params?.tabla) qp.set('tabla', params.tabla);
    const query = qp.toString() ? `?${qp}` : '';
    return this.http.get<BitacoraEntry[]>(`${this.sistemaUrl}/audit-log${query}`);
  }

  getRestricciones(): Observable<Restricciones> {
    return this.http.get<Restricciones>(`${this.sistemaUrl}/restricciones`);
  }

  updateRestricciones(data: Restricciones): Observable<Restricciones> {
    return this.http.put<Restricciones>(`${this.sistemaUrl}/restricciones`, data);
  }

  toggleRestriccion(clave: string, valor: any): Observable<Restricciones> {
    return this.http.patch<Restricciones>(`${this.sistemaUrl}/restricciones`, { clave, valor });
  }

  exportarTenant(cod: string): Observable<Blob> {
    return this.http.get(`${this.sistemaUrl}/exportar/${cod}`, { responseType: 'blob' });
  }

  exportarGlobal(): Observable<Blob> {
    return this.http.get(`${this.sistemaUrl}/exportar-global`, { responseType: 'blob' });
  }
}
