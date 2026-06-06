import { Injectable, inject } from '@angular/core';
import { ApiService } from '../api/api.service';
import { ConfigService } from '../config/config.service';
import { Observable } from 'rxjs';
import { HttpParams } from '@angular/common/http';

export interface StatsResumen {
  total_servicios: number;
  ingreso_bruto: number;
  comisiones_pagadas: number;
  ingreso_neto: number;
  mes: number;
  anio: number;
}

export interface StatsGrafica {
  fecha: string;
  monto: number;
}

export interface StatsResponse {
  resumen: StatsResumen;
  grafica: StatsGrafica[];
}

export interface KpiResumen {
  total_activas: number;
  total_atendidas: number;
  tiempo_promedio_asignacion: number;
  tiempo_promedio_llegada: number;
  tiempo_respuesta_minutos: number;
  tasa_asignacion: number;
  calificacion_promedio: number;
  tasa_cumplimiento_sla: number;
}

export interface AnaliticaAvanzada {
  incidentes_por_tipo: { tipo: string, cantidad: number }[];
  zonas_incidentes: { zona: string, cantidad: number }[];
  ranking_sucursales: { sucursal: string, eficiencia_promedio_min: number, atendidas: number }[];
}

export interface KpiResponse {
  kpis: KpiResumen;
  analitica: AnaliticaAvanzada;
  grafica: any[];
}

export interface VehiculoOut {
  placa: string;
  marca: string;
  modelo: string;
  anio: number;
}

export interface HistorialVehicularItem {
  id_emergencia: number;
  fecha: string;
  estado_final: string;
  tipo_emergencia: string;
  diagnostico_inicial: string;
  diagnostico_final: string | null;
  servicios_realizados: string | null;
  monto_total: number | null;
  calificacion_taller: number | null;
  calificacion_tecnico: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class ReportesService {
  private api = inject(ApiService);
  private configService = inject(ConfigService);

  getStats(mes: number, anio: number): Observable<StatsResponse> {
    const params = new HttpParams()
      .set('mes', mes.toString())
      .set('anio', anio.toString());
    return this.api.get<StatsResponse>('/reportes/stats', params);
  }

  obtenerVehiculosAtendidos(): Observable<VehiculoOut[]> {
    return this.api.get<VehiculoOut[]>('/reportes/vehiculos-atendidos');
  }

  obtenerHistorialVehiculo(placa: string): Observable<HistorialVehicularItem[]> {
    return this.api.get<HistorialVehicularItem[]>(`/reportes/vehiculos-atendidos/${placa}/historial`);
  }

  getKpis(rango: 'diario' | 'semanal' | 'mensual'): Observable<KpiResponse> {
    const params = new HttpParams().set('rango', rango);
    return this.api.get<KpiResponse>('/reportes/kpis-legacy', params);
  }

  downloadPdf(mes: number, anio: number): void {
    const token = localStorage.getItem('access_token');
    const url = `${this.configService.apiUrl}/reportes/pdf?mes=${mes}&anio=${anio}`;

    fetch(url, {
      method: 'GET',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
      .then(res => {
        if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
        return res.blob();
      })
      .then(blob => {
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `reporte_${mes}_${anio}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);
      })
      .catch(err => console.error('❌ Error descargando reporte PDF:', err));
  }
}
