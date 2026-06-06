import { Component, EventEmitter, Input, OnInit, Output, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as L from 'leaflet';

@Component({
  selector: 'app-map-picker',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="map-container">
      <div id="map" class="map-frame"></div>
      <div class="map-overlay" *ngIf="loading">
        <div class="loader"></div>
        <span>Buscando dirección...</span>
      </div>
      <div class="map-info" *ngIf="currentAddress && !loading">
         <i class="las la-map-marker"></i> {{ currentAddress }}
      </div>
    </div>
  `,
  styles: [`
    .map-container {
      position: relative;
      width: 100%;
      height: 300px;
      border-radius: var(--radius-md);
      overflow: hidden;
      border: 1px solid var(--border-color);
      margin-bottom: var(--space-4);
      box-shadow: var(--shadow-sm);
    }
    .map-frame {
      width: 100%;
      height: 100%;
      z-index: 1;
    }
    .map-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(255, 255, 255, 0.7);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      backdrop-filter: blur(2px);
    }
    .map-info {
      position: absolute;
      bottom: var(--space-3);
      left: var(--space-3);
      right: var(--space-3);
      background: white;
      padding: var(--space-2) var(--space-3);
      border-radius: var(--radius-sm);
      font-size: var(--font-size-sm);
      box-shadow: var(--shadow-md);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--color-text-main);
      border-left: 4px solid var(--color-primary);
    }
    .loader {
      width: 30px;
      height: 30px;
      border: 3px solid var(--color-primary-light);
      border-top: 3px solid var(--color-primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 8px;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  `]
})
export class MapPickerComponent implements OnInit, OnDestroy {
  @Input() initialLat = -17.7833; // Default Santa Cruz, Bolivia
  @Input() initialLng = -63.1821;
  @Output() locationSelected = new EventEmitter<{lat: number, lng: number, address: string}>();

  private map?: L.Map;
  private marker?: L.Marker;
  loading = false;
  currentAddress = '';

  ngOnInit() {
    // Timeout para asegurar que el contenedor esté listo
    setTimeout(() => this.initMap(), 100);
  }

  ngOnDestroy() {
    if (this.map) {
      this.map.remove();
    }
  }

  private initMap() {
    this.map = L.map('map').setView([this.initialLat, this.initialLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(this.map);

    const icon = L.icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41]
    });

    this.marker = L.marker([this.initialLat, this.initialLng], { 
      icon, 
      draggable: true 
    }).addTo(this.map);

    this.marker.on('dragend', () => this.onMarkerMove());
    this.map.on('click', (e: any) => {
      this.marker?.setLatLng(e.latlng);
      this.onMarkerMove();
    });

    // Intentar obtener geolocalización actual
    if (navigator.geolocation) {
       navigator.geolocation.getCurrentPosition((pos) => {
         const { latitude, longitude } = pos.coords;
         this.map?.setView([latitude, longitude], 15);
         this.marker?.setLatLng([latitude, longitude]);
         this.onMarkerMove();
       });
    }
  }

  private async onMarkerMove() {
    if (!this.marker) return;
    const latlng = this.marker.getLatLng();
    this.loading = true;

    try {
      const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}&zoom=18&addressdetails=1`);
      const data = await resp.json();
      this.currentAddress = data.display_name || 'Coordenadas seleccionadas en el mapa';
      this.loading = false;
      this.locationSelected.emit({
        lat: latlng.lat,
        lng: latlng.lng,
        address: this.currentAddress
      });
    } catch (error) {
      console.error('Error reverse geocoding:', error);
      this.currentAddress = 'Coordenadas seleccionadas en el mapa';
      this.loading = false;
      this.locationSelected.emit({
        lat: latlng.lat,
        lng: latlng.lng,
        address: this.currentAddress
      });
    }
  }
}
