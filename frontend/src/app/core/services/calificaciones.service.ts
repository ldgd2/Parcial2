import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface CalificacionModerada {
  id: number;
  idEmergencia: number;
  idCliente: number;
  idTaller: string;
  idTecnico: number;
  puntuacion_taller: number;
  puntuacion_tecnico: number;
  comentario: string;
  estado: string;
  fecha: string;
  cliente_nombre: string;
  tecnico_nombre: string;
}

@Injectable({
  providedIn: 'root'
})
export class CalificacionesService {
  private apiUrl = `${environment.apiUrl}/calificaciones`;

  constructor(private http: HttpClient) {}

  obtenerCalificacionesTaller(): Observable<CalificacionModerada[]> {
    return this.http.get<CalificacionModerada[]>(`${this.apiUrl}/taller`);
  }

  moderarCalificacion(id: number, estado: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/${id}/moderar`, { estado });
  }
}
