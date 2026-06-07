import { Component, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import * as L from 'leaflet';

import { ApiService } from '../../core/api/api.service';
import { LucideAngularModule } from 'lucide-angular';
import { toast } from 'ngx-sonner';
import { SocketService } from '../../core/services/socket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-radar',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    FormsModule,
    LucideAngularModule
  ],
  template: `
    <div class="relative w-full h-screen overflow-hidden bg-black font-sans text-white">
      
      <!-- LEAFLET MAP CONTAINER -->
      <div id="radar-map" class="absolute inset-0 z-0"></div>

      <!-- HUD: TOP BAR -->
      <div class="absolute top-0 left-0 right-0 z-10 p-6 lg:p-10 pointer-events-none">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-start gap-8 pointer-events-auto">
          <!-- TITLE -->
          <div class="bg-black/80 backdrop-blur-md border border-zinc-800 p-6 shadow-2xl">
            <h1 class="text-3xl font-bold tracking-widest mb-2 uppercase text-white shadow-black drop-shadow-md">Radar Ops</h1>
            <div class="flex items-center gap-4">
              <p class="font-mono text-[9px] uppercase tracking-[.3em] text-zinc-400">
                Monitor en Tiempo Real
              </p>
              <div class="h-px w-12 bg-zinc-700"></div>
              <span class="font-mono text-[9px] text-primary animate-pulse tracking-widest font-bold">LIVE</span>
            </div>
          </div>

          <!-- FILTERS -->
          <div class="flex items-center bg-black/80 backdrop-blur-md border border-zinc-800 p-1 shadow-2xl">
            <button (click)="setFilter('all')" 
                    [class]="filter === 'all' ? 'bg-primary text-black' : 'text-zinc-500 hover:text-white'" 
                    class="px-6 py-3 font-bold text-[9px] uppercase tracking-[.2em] transition-all">
              Todas
            </button>
            <button (click)="setFilter('PENDIENTE')" 
                    [class]="filter === 'PENDIENTE' ? 'bg-primary text-black' : 'text-zinc-500 hover:text-white'" 
                    class="px-6 py-3 font-bold text-[9px] uppercase tracking-[.2em] transition-all">
              Pendientes
            </button>
            <button (click)="setFilter('BLOQUEADO')" 
                    [class]="filter === 'BLOQUEADO' ? 'bg-primary text-black' : 'text-zinc-500 hover:text-white'" 
                    class="px-6 py-3 font-bold text-[9px] uppercase tracking-[.2em] transition-all">
              En Análisis
            </button>
          </div>
        </div>
      </div>

      <!-- HUD: STATS PANEL (BOTTOM LEFT) -->
      <div class="absolute bottom-10 left-6 lg:left-10 z-10 pointer-events-none">
        <div class="flex gap-px bg-zinc-900 border border-zinc-800 shadow-2xl pointer-events-auto">
          <div class="bg-black/80 backdrop-blur-md p-6 flex flex-col justify-between w-32 hover:bg-zinc-950 transition-colors cursor-default">
            <span class="font-mono text-[8px] uppercase tracking-[.25em] text-zinc-500 mb-4 flex items-center gap-2">
              Total
            </span>
            <span class="font-mono text-3xl font-bold tracking-tighter">{{ stats.total }}</span>
          </div>
          <div class="bg-black/80 backdrop-blur-md p-6 flex flex-col justify-between w-32 border-l border-zinc-900 hover:bg-zinc-950 transition-colors cursor-default">
            <span class="font-mono text-[8px] uppercase tracking-[.25em] text-red-500 mb-4 flex items-center gap-2">
              <div class="w-1.5 h-1.5 bg-red-500 animate-pulse"></div> Críticas
            </span>
            <span class="font-mono text-3xl font-bold tracking-tighter text-red-500">{{ stats.critical }}</span>
          </div>
          <div class="bg-black/80 backdrop-blur-md p-6 flex flex-col justify-between w-32 border-l border-zinc-900 hover:bg-zinc-950 transition-colors cursor-default">
            <span class="font-mono text-[8px] uppercase tracking-[.25em] text-zinc-500 mb-4 flex items-center gap-2">
              <div class="w-1.5 h-1.5 bg-emerald-500"></div> Libres
            </span>
            <span class="font-mono text-3xl font-bold tracking-tighter">{{ stats.pending }}</span>
          </div>
        </div>
      </div>

      <!-- LOADING OR NO DATA -->
      <div *ngIf="loading" class="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm pointer-events-none">
         <div class="w-16 h-16 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
         <p class="font-mono text-[10px] uppercase tracking-widest text-zinc-500 mt-6">Conectando a satélite geoespacial...</p>
      </div>

      <!-- NOTIFICACION FLOTANTE NUEVA EMERGENCIA -->
      <div *ngIf="newAlert" class="absolute top-32 left-1/2 -translate-x-1/2 z-50 pointer-events-none animate-in slide-in-from-top-10 fade-in duration-300">
        <div class="bg-primary text-black font-bold text-[10px] uppercase tracking-widest px-8 py-3 shadow-[0_0_20px_rgba(var(--color-primary),0.5)]">
          ¡Nueva emergencia detectada en la red!
        </div>
      </div>

    </div>
  `,
  styles: [`
    #radar-map { height: 100%; width: 100%; background: #050505; }
    .leaflet-container { background: #050505 !important; font-family: 'Inter', sans-serif; }
    
    /* TOOLTIP Y POPUPS DE LEAFLET PERSONALIZADOS */
    .leaflet-popup-content-wrapper { 
      background: rgba(5, 5, 5, 0.95); 
      border: 1px solid #27272a; 
      color: white; 
      border-radius: 0; 
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); 
    }
    .leaflet-popup-tip { background: #27272a; }
    .leaflet-popup-content { margin: 16px; font-family: monospace; }
    .leaflet-tooltip {
      background: rgba(0, 0, 0, 0.9);
      border: 1px solid #3f3f46;
      color: white;
      font-family: monospace;
      font-size: 10px;
      text-transform: uppercase;
      padding: 8px 12px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5);
    }
    .leaflet-tooltip-left::before { border-left-color: #3f3f46; }
    .leaflet-tooltip-right::before { border-right-color: #3f3f46; }

    /* ESTILOS GLOBALES PARA EL HTML DENTRO DEL POPUP */
    ::ng-deep .radar-popup-btn {
      display: inline-block;
      width: 100%;
      text-align: center;
      background: #10b981;
      color: black;
      font-weight: bold;
      text-transform: uppercase;
      letter-spacing: 2px;
      font-size: 9px;
      padding: 10px 0;
      margin-top: 15px;
      cursor: pointer;
      transition: background 0.2s;
    }
    ::ng-deep .radar-popup-btn:hover { background: #059669; }
  `]
})
export class RadarComponent implements OnInit, OnDestroy, AfterViewInit {
  emergencies: any[] = [];
  filter: 'all' | 'PENDIENTE' | 'BLOQUEADO' = 'all';
  loading = true;
  newAlert = false;
  
  private socketSub?: Subscription;
  private map: L.Map | null = null;
  private markersLayer: L.LayerGroup | null = null;
  private markersMap: Map<number, L.Marker> = new Map();
  private currentWorkshop = localStorage.getItem('cod_taller') || 'TALLER_01';

  constructor(
    private api: ApiService, 
    private router: Router,
    private socketService: SocketService
  ) {
    // Exponer función de enrutamiento a window para poder usarla desde popups nativos de Leaflet
    (window as any).radarNavigateTo = (id: number) => {
      this.router.navigate(['/app/emergency', id]);
    };
  }

  ngOnInit() {
    this.refreshData();
    
    // Connect to WebSocket for real-time updates
    this.socketService.connect(this.currentWorkshop);
    
    this.socketSub = this.socketService.getMessages().subscribe(msg => {
      if (msg.type === 'db_update' && msg.table === 'emergencia') {
        console.log('Real-time update received on Radar:', msg);
        
        // Efecto visual de nueva emergencia
        this.triggerNewAlert();
        this.refreshData(true);
      }
    });
  }

  ngAfterViewInit() {
    this.initMap();
  }

  ngOnDestroy() {
    if (this.socketSub) this.socketSub.unsubscribe();
    if (this.map) this.map.remove();
    // Limpiar window method
    delete (window as any).radarNavigateTo;
  }

  triggerNewAlert() {
    this.newAlert = true;
    setTimeout(() => this.newAlert = false, 4000);
  }

  tallerCoords: L.LatLng | null = null;
  sucursalesCoords: L.LatLng[] = [];

  initMap() {
    // Primero, inicializamos el mapa con una vista por defecto
    this.map = L.map('radar-map', {
      zoomControl: false,
      attributionControl: false
    }).setView([-16.5, -68.15], 13);

    // CartoDB Dark Matter tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(this.map);
    
    // Contenedor para pines
    this.markersLayer = L.layerGroup().addTo(this.map);

    // Obtener la ubicación del taller y centrar el mapa
    this.api.get<any>(`/talleres/${this.currentWorkshop}`).subscribe({
      next: (taller) => {
        if (taller.latitud && taller.longitud && this.map) {
          this.tallerCoords = L.latLng(taller.latitud, taller.longitud);
          this.map.setView(this.tallerCoords, 14); // Zoom 14 (~5km de radio)
          this.renderMarkers(false); // Renderizar ahora que tenemos la ubicación
        }
      }
    });

    // Cargar también las sucursales para que el radar intercepte emergencias cerca de ellas
    this.api.get<any[]>(`/sucursales/taller/${this.currentWorkshop}`).subscribe({
      next: (sucursales) => {
        if (sucursales && sucursales.length > 0) {
          this.sucursalesCoords = sucursales
            .filter((s: any) => s.latitud && s.longitud)
            .map((s: any) => L.latLng(s.latitud, s.longitud));
          this.renderMarkers(false);
        }
      },
      error: (e) => console.error("Error cargando sucursales para el radar", e)
    });
  }

  refreshData(isUpdate = false) {
    this.api.get<any[]>('/gestion-emergencia/disponibles').subscribe({
      next: (res) => {
        this.emergencies = res;
        this.loading = false;
        this.renderMarkers(isUpdate);
      },
      error: (e) => {
        console.error('Error loading radar data', e);
        this.loading = false;
      }
    });
  }

  setFilter(f: 'all' | 'PENDIENTE' | 'BLOQUEADO') {
    this.filter = f;
    this.renderMarkers();
  }

  get filteredEmergencies() {
    return this.emergencies.filter(emg => {
      // Filtrar por estado
      if (this.filter !== 'all') {
        if (this.filter === 'BLOQUEADO' && !emg.is_locked) return false;
        if (this.filter !== 'BLOQUEADO' && (emg.estado_actual !== this.filter || emg.is_locked)) return false;
      }

      // Filtrar por distancia (solo cercanas, e.g. < 10 km de la matriz o cualquier sucursal)
      if (emg.latitud && emg.longitud) {
        const emgLatLng = L.latLng(emg.latitud, emg.longitud);
        let minDistance = Infinity;
        
        if (this.tallerCoords) {
          minDistance = this.tallerCoords.distanceTo(emgLatLng);
        }
        
        for (const suc of this.sucursalesCoords) {
          const d = suc.distanceTo(emgLatLng);
          if (d < minDistance) {
            minDistance = d;
          }
        }
        
        if (minDistance > 10000) { // 10 km
          return false;
        }
      }

      return true;
    });
  }

  get stats() {
    return {
      total: this.emergencies.length,
      critical: this.emergencies.filter(e => e.idPrioridad >= 4).length,
      pending: this.emergencies.filter(e => e.estado_actual === 'PENDIENTE' && !e.is_locked).length
    };
  }

  // Define marker color based on Priority
  // Nivel 5: Rojo
  // Nivel 4: Naranja
  // Nivel 3: Amarillo
  // Nivel 2: Azul
  // Nivel 1: Gris
  getPriorityColorHex(prioridad: number): string {
    switch (prioridad) {
      case 5: return '#ef4444'; // Red 500
      case 4: return '#f97316'; // Orange 500
      case 3: return '#eab308'; // Yellow 500
      case 2: return '#3b82f6'; // Blue 500
      case 1: return '#71717a'; // Zinc 500
      default: return '#10b981'; // Emerald (default)
    }
  }

  getPriorityLabel(prioridad: number): string {
    switch (prioridad) {
      case 5: return 'CRÍTICA';
      case 4: return 'ALTA';
      case 3: return 'MEDIA';
      case 2: return 'BAJA';
      case 1: return 'MÍNIMA';
      default: return 'DESCONOCIDA';
    }
  }

  renderMarkers(isUpdate = false) {
    if (!this.map || !this.markersLayer) return;

    // Limpiar capa
    this.markersLayer.clearLayers();
    this.markersMap.clear();

    const bounds = L.latLngBounds([]);

    this.filteredEmergencies.forEach(emg => {
      if (!emg.latitud || !emg.longitud) return;

      const latlng = L.latLng(emg.latitud, emg.longitud);
      bounds.extend(latlng);

      const color = this.getPriorityColorHex(emg.idPrioridad);
      const isCritical = emg.idPrioridad >= 4;

      // Crear el HTML del Pin
      const htmlIcon = `
        <div style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
          ${isCritical ? `<div style="position: absolute; width: 30px; height: 30px; background-color: ${color}; border-radius: 50%; opacity: 0.4; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>` : ''}
          <div style="width: 14px; height: 14px; background-color: ${color}; border: 2px solid white; border-radius: 50%; box-shadow: 0 0 15px ${color}; z-index: 10;"></div>
        </div>
      `;

      const icon = L.divIcon({
        className: 'custom-radar-pin',
        html: htmlIcon,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });

      const marker = L.marker(latlng, { icon }).addTo(this.markersLayer!);
      
      // Resumen e IA
      const resumen = emg.resumen_ia?.resumen || 'Sin resumen disponible.';
      const statusLabel = emg.is_locked ? 'EN ANÁLISIS' : emg.estado_actual;
      const vehiculo = emg.vehiculo ? `${emg.vehiculo.marca} ${emg.vehiculo.modelo}` : 'Vehículo Desconocido';
      
      // Popup HTML (Se usa onclick nativo hacia window.radarNavigateTo)
      const popupHtml = `
        <div style="min-width: 200px;">
          <div style="font-size: 8px; color: ${color}; letter-spacing: 2px; margin-bottom: 5px;">PRIORIDAD ${this.getPriorityLabel(emg.idPrioridad)}</div>
          <div style="font-weight: bold; font-family: sans-serif; font-size: 14px; margin-bottom: 8px; color: white;">${emg.descripcion}</div>
          <div style="font-size: 11px; color: #a1a1aa; margin-bottom: 10px; font-style: italic;">"${resumen}"</div>
          
          <div style="border-top: 1px solid #27272a; padding-top: 8px; font-size: 10px; color: #d4d4d8;">
            <div style="margin-bottom: 4px;"><strong>VEHÍCULO:</strong> ${vehiculo}</div>
            <div style="margin-bottom: 4px;"><strong>PLACA:</strong> ${emg.placaVehiculo}</div>
            <div style="margin-bottom: 4px;"><strong>ESTADO:</strong> ${statusLabel}</div>
          </div>
          
          <button class="radar-popup-btn" onclick="window.radarNavigateTo(${emg.id})">
            Tomar Misión
          </button>
        </div>
      `;

      marker.bindPopup(popupHtml);
      
      // Tooltip flotante (Hover)
      marker.bindTooltip(`P${emg.idPrioridad} - ${vehiculo} - ${statusLabel}`, {
        direction: 'top',
        offset: [0, -10],
        opacity: 0.9
      });

      this.markersMap.set(emg.id, marker);
    });
  }

}
