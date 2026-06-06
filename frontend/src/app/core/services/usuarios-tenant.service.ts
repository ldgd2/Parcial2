import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UsuarioTenant {
  id: number;
  nombre: string;
  apellido?: string;
  correo: string;
  telefono?: string;
  estado: string;
  tipo: 'TECNICO' | 'ADMINISTRATIVO';
  rol_nombre: string;
  sucursal_id?: number;
}

export interface RolOut {
  id: number;
  nombre: string;
}

@Injectable({
  providedIn: 'root'
})
export class UsuariosTenantService {
  private apiUrl = `${environment.apiUrl}/usuarios-tenant`;

  constructor(private http: HttpClient) {}

  listarUsuarios(): Observable<UsuarioTenant[]> {
    return this.http.get<UsuarioTenant[]>(this.apiUrl);
  }

  crearUsuario(data: any): Observable<UsuarioTenant> {
    return this.http.post<UsuarioTenant>(this.apiUrl, data);
  }

  cambiarEstado(tipo: string, id: number, estado: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/${tipo}/${id}/status`, { estado });
  }

  resetearContrasena(tipo: string, id: number, nueva_contrasena: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/${tipo}/${id}/reset-password`, { nueva_contrasena });
  }

  obtenerRoles(): Observable<RolOut[]> {
    return this.http.get<RolOut[]>(`${this.apiUrl}/roles`);
  }
}
