import { Injectable, inject, signal } from '@angular/core';
import { ApiService } from '../api/api.service';
import { Router } from '@angular/router';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { Observable, of, BehaviorSubject, throwError } from 'rxjs';

export interface PlanInfo {
  nombre: string;
  precio_mensual: number;
  max_sucursales: number;
  max_tecnicos: number;
}

export interface AuthMeResponse {
  usuario: any;
  taller: any | null;  // null para super admins sin taller
  plan: PlanInfo;
  sucursal?: number;
  permisos: string[];
  is_super_admin?: boolean;
  role?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private api = inject(ApiService);
  private router = inject(Router);

  // Use a BehaviorSubject or signals for global state
  public currentUser = signal<AuthMeResponse | null>(null);
  public isAuthenticated = signal<boolean>(false);
  public isReady = signal<boolean>(false);

  constructor() {
    this.initAuth();
  }

  private initAuth() {
    const token = localStorage.getItem('access_token');
    if (token) {
      this.fetchMe().subscribe({
        next: (me) => {
          this.currentUser.set(me);
          this.isAuthenticated.set(true);
          this.isReady.set(true);
        },
        error: () => {
          this.logout();
          this.isReady.set(true);
        }
      });
    } else {
      this.isReady.set(true);
    }
  }

  loginWeb(credentials: any): Observable<any> {
    return this.api.post<any>('/auth/login/web', credentials).pipe(
      tap(res => {
        localStorage.setItem('access_token', res.access_token);
        localStorage.setItem('rol', res.rol);
        localStorage.setItem('user_name', res.nombre);
        localStorage.setItem('cod_taller', res.cod_taller || '');
        localStorage.setItem('nombre_taller', res.nombre_taller || 'Taller OS');
      }),
      switchMap(() => this.fetchMe()),
      tap({
        next: (me) => {
          this.currentUser.set(me);
          this.isAuthenticated.set(true);
        },
        error: (err) => {
          console.error('[AuthService] fetchMe failed in loginWeb:', err);
          this.logout();
        }
      }),
      catchError(err => {
        console.error('[AuthService] Fatal error in loginWeb observable chain:', err);
        return throwError(() => err);
      })
    );
  }

  fetchMe(): Observable<AuthMeResponse> {
    return this.api.get<AuthMeResponse>('/auth/me');
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('rol');
    localStorage.removeItem('user_name');
    localStorage.removeItem('cod_taller');
    localStorage.removeItem('nombre_taller');
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
    this.router.navigate(['/auth/login']);
  }

  hasPermission(permissionCode: string): boolean {
    const user = this.currentUser();
    if (!user) return false;
    // System admin fallback or specific permission
    return user.permisos.includes(permissionCode) || user.permisos.includes('ALL_PERMISSIONS_FALLBACK_IF_ANY');
  }
}
