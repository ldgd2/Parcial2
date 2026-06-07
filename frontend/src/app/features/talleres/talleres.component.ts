import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { ApiService } from '../../core/api/api.service';
import { toast } from 'ngx-sonner';
import * as L from 'leaflet';

interface Especialidad {
  id: number;
  nombre: string;
  categoria: string;
}

interface SucursalCard {
  id: number;
  id_taller: string;
  nombre: string;
  direccion: string;
  estado: string;
  especialidades?: any[];
}

interface TallerCard {
  cod: string;
  nombre: string;
  direccion: string;
  estado: string;
  trabajos_activos?: number;
}

@Component({
  selector: 'app-talleres',
  standalone: true,
  imports: [CommonModule, LucideAngularModule, RouterModule, FormsModule],
  template: `
    <div class="h-full bg-[#0d0d0d] text-white p-8 lg:p-12 animate-in fade-in duration-700 relative">
      
      <!-- PAGE HEADER -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12 border-b border-zinc-800/60 pb-8">
        <div>
          <h1 class="text-[32px] font-bold tracking-tight mb-2 text-white">Mi Red Operativa</h1>
          <p class="font-mono text-[10px] uppercase tracking-[.25em] text-zinc-500">
            Gestión de Sede Principal y Sucursales
          </p>
        </div>
      </div>

      <!-- LOADING -->
      <div *ngIf="loading" class="py-20 text-center">
         <div class="w-10 h-10 border-2 border-[#FF5733] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
         <p class="font-mono text-[9px] uppercase tracking-widest text-[#FF5733]">Sincronizando red operativa...</p>
      </div>

      <div *ngIf="!loading">
        <!-- SEDE PRINCIPAL (Solo visible para Admin Taller) -->
        <div *ngIf="isAdminTaller && tallerPrincipal" class="mb-12">
            <div class="flex justify-between items-end mb-6">
                <div>
                    <h2 class="text-xl font-bold uppercase tracking-widest text-white flex items-center gap-2">
                        <lucide-icon name="building-2" size="24" class="text-[#FF5733]"></lucide-icon>
                        Sede Principal
                    </h2>
                </div>
            </div>

            <div class="border-2 border-[#FF5733]/30 bg-[#111111] p-8 flex flex-col md:flex-row justify-between items-center gap-6 shadow-[0_0_30px_rgba(255,87,51,0.05)] relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-[#FF5733]/5 blur-[100px] rounded-full"></div>
                
                <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                        <span class="bg-[#FF5733]/20 px-3 py-1 text-xs font-mono font-bold text-[#FF5733] tracking-widest border border-[#FF5733]/30">{{ tallerPrincipal.cod }}</span>
                        <span [class]="getStatusClass(tallerPrincipal.estado)" class="px-2 py-1 text-[9px] font-bold tracking-[.15em] uppercase border">
                        {{ tallerPrincipal.estado === 'ACTIVO' ? 'OPERATIVO' : tallerPrincipal.estado }}
                        </span>
                    </div>
                    <h3 class="text-2xl font-bold tracking-tight mb-2 text-white">{{ tallerPrincipal.nombre }}</h3>
                    <div class="flex items-center gap-3 text-zinc-400">
                        <lucide-icon name="map-pin" size="16" class="text-zinc-600"></lucide-icon>
                        <span class="text-sm font-medium tracking-wide">{{ tallerPrincipal.direccion || 'Ubicación base' }}</span>
                    </div>
                </div>

                <div class="flex gap-4 w-full md:w-auto z-10">
                    <button [routerLink]="['/app/taller', tallerPrincipal.cod]"
                            class="px-8 py-4 border border-zinc-700 font-bold text-[10px] uppercase tracking-[.25em] text-white hover:bg-zinc-800 transition-all">
                        CONFIGURAR SEDE
                    </button>
                    <button (click)="openSucursalModal(tallerPrincipal.cod)"
                            class="px-8 py-4 bg-[#FF5733] font-bold text-[10px] uppercase tracking-[.25em] text-white hover:brightness-110 shadow-lg shadow-[#FF5733]/20 transition-all flex items-center gap-2">
                        <lucide-icon name="plus" size="16"></lucide-icon>
                        NUEVA SUCURSAL
                    </button>
                </div>
            </div>
        </div>

        <!-- SUCURSALES GRID -->
        <div>
            <div class="flex justify-between items-end mb-6">
                <div>
                    <h2 class="text-xl font-bold uppercase tracking-widest text-white flex items-center gap-2">
                        <lucide-icon name="git-branch" size="24" class="text-[#00ff9d]"></lucide-icon>
                        {{ isAdminTaller ? 'Sucursales de la Red' : 'Mi Sucursal Asignada' }}
                    </h2>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                <div *ngFor="let s of sucursales" class="group border border-[#222222] bg-[#111111] p-8 flex flex-col transition-all hover:border-zinc-700 shadow-xl relative overflow-hidden">
                
                <div class="absolute top-0 right-0 w-32 h-32 bg-[#00ff9d]/5 blur-[50px] rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>

                <div class="flex justify-between items-center mb-6 z-10">
                    <span class="bg-zinc-800/50 px-3 py-1 text-xs font-mono font-bold text-zinc-400 tracking-widest">SUC-{{ s.id }}</span>
                    <span [class]="getStatusClass(s.estado)" class="px-2 py-1 text-[9px] font-bold tracking-[.15em] uppercase border">
                    {{ s.estado === 'ACTIVO' ? 'OPERATIVO' : s.estado }}
                    </span>
                </div>

                <div class="flex-1 flex flex-col justify-start z-10">
                    <h3 class="text-xl font-bold tracking-tight mb-4 text-white group-hover:text-[#00ff9d] transition-colors">{{ s.nombre }}</h3>
                    
                    <div class="space-y-3 mb-6">
                        <div class="flex items-start gap-3 text-zinc-400">
                        <lucide-icon name="map-pin" size="14" class="mt-1 flex-shrink-0"></lucide-icon>
                        <span class="text-xs font-medium tracking-wide leading-relaxed">{{ s.direccion }}</span>
                        </div>
                    </div>
                </div>

                <div class="mt-auto pt-6 border-t border-[#222222] flex gap-2 z-10">
                    <button (click)="openEspecialidadesModal(s)"
                            class="flex-1 py-3 border border-zinc-800 font-bold text-[10px] uppercase tracking-[.25em] text-white hover:border-[#00ff9d] hover:text-[#00ff9d] transition-all text-center flex justify-center items-center gap-2">
                        <lucide-icon name="wrench" size="14"></lucide-icon>
                        ESPECIALIDADES
                    </button>
                </div>
                </div>

                <div *ngIf="sucursales.length === 0" class="col-span-full border border-dashed border-zinc-800 p-16 text-center bg-[#111111]/50">
                    <lucide-icon name="git-branch" size="32" class="text-zinc-700 mx-auto mb-4"></lucide-icon>
                    <p class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">No hay sucursales registradas.</p>
                </div>
            </div>
        </div>
      </div>

      <!-- SUCURSAL MODAL OVERLAY -->
      <div *ngIf="showSucursalModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-[#111111] border border-[#333333] w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl relative custom-scrollbar">
          <div class="sticky top-0 bg-[#111111] p-6 border-b border-zinc-800 z-10 flex justify-between items-center">
             <div>
                <h2 class="text-xl font-bold uppercase text-white">Registrar Sucursal</h2>
                <p class="text-[9px] font-mono text-[#FF5733] uppercase tracking-widest">Añadir branch al taller base</p>
             </div>
             <button (click)="showSucursalModal = false" class="text-zinc-500 hover:text-white">
                <lucide-icon name="x" size="20"></lucide-icon>
             </button>
          </div>
          
          <div class="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
             <div class="space-y-6">
                <h3 class="font-bold text-[11px] uppercase tracking-[.25em] text-white border-l-2 border-[#FF5733] pl-2">Datos y Ubicación</h3>
                
                <div class="space-y-2">
                  <label class="font-mono text-[9px] uppercase tracking-widest text-zinc-400">Nombre de Sucursal *</label>
                  <input type="text" [(ngModel)]="newSucursal.nombre" class="w-full bg-[#050505] border border-zinc-800 p-3 text-xs text-white focus:border-[#FF5733] outline-none">
                </div>
                
                <div class="space-y-2">
                  <label class="font-mono text-[9px] uppercase tracking-widest text-zinc-400">Dirección (Click en Mapa) *</label>
                  <input type="text" [(ngModel)]="newSucursal.direccion" class="w-full bg-[#050505] border border-zinc-800 p-3 text-xs text-white focus:border-[#FF5733] outline-none">
                </div>
                
                <div class="space-y-2">
                  <label class="font-mono text-[9px] uppercase tracking-widest text-zinc-400">Mapa Satelital</label>
                  <div id="sucursalMap" class="h-48 w-full bg-[#050505] border border-zinc-800 relative z-0"></div>
                </div>
             </div>
             
             <div class="space-y-6">
                <h3 class="font-bold text-[11px] uppercase tracking-[.25em] text-white border-l-2 border-[#00ff9d] pl-2">Usuario Administrador</h3>
                
                <div class="space-y-2">
                  <label class="font-mono text-[9px] uppercase tracking-widest text-zinc-400">Seleccionar Usuario *</label>
                  <select [(ngModel)]="newSucursal.admin_usuario_id" class="w-full bg-[#050505] border border-zinc-800 p-3 text-xs text-white focus:border-[#00ff9d] outline-none">
                     <option value="" disabled selected>-- Seleccione un usuario --</option>
                     <option *ngFor="let u of candidatosAdmin" [value]="u.id">
                        {{ u.nombre }} {{ u.apellido }} ({{ u.correo }})
                     </option>
                  </select>
                </div>
                
                <div *ngIf="candidatosAdmin.length === 0" class="text-[10px] text-zinc-500 italic mt-2">
                   No hay usuarios disponibles en este taller. Registre usuarios en la sección Personal primero.
                </div>

                <div class="pt-8 mt-auto">
                    <button (click)="submitSucursalCreate()" [disabled]="creatingSucursal || !newSucursal.admin_usuario_id" class="w-full bg-[#FF5733] text-white py-4 font-bold text-[11px] uppercase tracking-widest hover:brightness-110 flex items-center justify-center gap-2 disabled:opacity-50 transition-all">
                       <lucide-icon *ngIf="creatingSucursal" name="loader-2" size="14" class="animate-spin"></lucide-icon>
                       REGISTRAR SUCURSAL Y ADMIN
                    </button>
                </div>
             </div>
          </div>
        </div>
      </div>

      <!-- ESPECIALIDADES MODAL -->
      <div *ngIf="showEspecialidadesModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-[#111111] border border-[#333333] w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col relative">
          <div class="bg-[#111111] p-6 border-b border-zinc-800 flex justify-between items-center">
             <div>
                <h2 class="text-xl font-bold uppercase text-white">Especialidades de Sucursal</h2>
                <p class="text-[9px] font-mono text-[#00ff9d] uppercase tracking-widest">{{ selectedSucursal?.nombre }}</p>
             </div>
             <button (click)="showEspecialidadesModal = false" class="text-zinc-500 hover:text-white">
                <lucide-icon name="x" size="20"></lucide-icon>
             </button>
          </div>
          
          <div class="p-8 overflow-y-auto custom-scrollbar flex-1">
             <div *ngIf="loadingEspecialidades" class="py-10 text-center">
                <div class="w-8 h-8 border-2 border-[#00ff9d] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
             </div>

             <div *ngIf="!loadingEspecialidades" class="space-y-6">
                <div *ngFor="let cat of categoriasEspecialidades" class="space-y-4">
                    <h4 class="font-bold text-[11px] uppercase tracking-[.25em] text-white border-l-2 border-[#00ff9d] pl-2">{{ cat.categoria }}</h4>
                    <div class="grid grid-cols-2 gap-4">
                        <label *ngFor="let esp of cat.items" class="flex items-center gap-3 p-3 border border-zinc-800 bg-[#0a0a0a] hover:bg-zinc-900 cursor-pointer transition-colors">
                            <input type="checkbox" 
                                   [checked]="isEspecialidadSelected(esp.id)" 
                                   (change)="toggleEspecialidad(esp.id)"
                                   class="w-4 h-4 accent-[#00ff9d] bg-zinc-800 border-zinc-700">
                            <span class="text-xs font-medium text-zinc-300">{{ esp.nombre }}</span>
                        </label>
                    </div>
                </div>
             </div>
          </div>

          <div class="p-6 border-t border-zinc-800 bg-[#0a0a0a]">
             <button (click)="saveEspecialidades()" [disabled]="savingEspecialidades" class="w-full bg-[#00ff9d] text-black py-4 font-bold text-[11px] uppercase tracking-widest hover:brightness-110 flex items-center justify-center gap-2 disabled:opacity-50 transition-all">
                <lucide-icon *ngIf="savingEspecialidades" name="loader-2" size="14" class="animate-spin"></lucide-icon>
                GUARDAR ESPECIALIDADES
             </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    :host { display: block; height: 100%; min-height: 100vh; background-color: #0d0d0d; }
  `]
})
export class TalleresComponent implements OnInit {
  loading = true;
  
  isAdminTaller = false;
  tallerPrincipal: TallerCard | null = null;
  sucursales: SucursalCard[] = [];

  showSucursalModal = false;
  creatingSucursal = false;
  candidatosAdmin: any[] = [];
  newSucursal = {
    id_taller: '',
    nombre: '',
    direccion: '',
    latitud: null as number | null,
    longitud: null as number | null,
    admin_usuario_id: ''
  };
  
  map: L.Map | null = null;
  marker: L.Marker | null = null;

  // Especialidades
  showEspecialidadesModal = false;
  selectedSucursal: SucursalCard | null = null;
  loadingEspecialidades = false;
  savingEspecialidades = false;
  todasEspecialidades: Especialidad[] = [];
  categoriasEspecialidades: {categoria: string, items: Especialidad[]}[] = [];
  selectedEspecialidadesIds: number[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadAuthAndData();
    this.loadCatalogoEspecialidades();
  }

  loadAuthAndData() {
    this.api.get<any>('/auth/me').subscribe({
      next: (me) => {
        // If sucursal is null, this user is the global Taller admin
        this.isAdminTaller = !me.sucursal;
        const tallerCod = me.taller.cod;
        
        if (this.isAdminTaller) {
          // Admin: Fetches the Taller info and all its sucursales
          this.api.get<TallerCard[]>('/talleres/mis-talleres').subscribe({
            next: (talleresRes) => {
              if (talleresRes.length > 0) {
                this.tallerPrincipal = talleresRes[0];
              }
              this.loadSucursales(tallerCod);
            },
            error: () => {
                this.loading = false;
                toast.error('Error cargando taller base');
            }
          });
        } else {
          // Admin de Sucursal: Only fetch their specific sucursal
          this.tallerPrincipal = null;
          this.loadSucursales(tallerCod, me.sucursal);
        }
      },
      error: () => {
        this.loading = false;
        toast.error('Error de autenticación');
      }
    });
  }

  loadSucursales(tallerCod: string, specificSucursalId?: number) {
    this.api.get<SucursalCard[]>(`/sucursales/taller/${tallerCod}`).subscribe({
      next: (res) => {
        if (specificSucursalId) {
            this.sucursales = res.filter(s => s.id === specificSucursalId);
        } else {
            this.sucursales = res;
        }
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        toast.error('Error cargando sucursales');
      }
    });
  }

  loadCatalogoEspecialidades() {
      this.api.get<Especialidad[]>('/auxilio/especialidades').subscribe({
          next: (res) => {
              this.todasEspecialidades = res;
              // Group by category
              const groups: {[key: string]: Especialidad[]} = {};
              res.forEach(e => {
                  const cat = e.categoria || 'OTROS';
                  if (!groups[cat]) groups[cat] = [];
                  groups[cat].push(e);
              });
              this.categoriasEspecialidades = Object.keys(groups).map(k => ({
                  categoria: k,
                  items: groups[k]
              }));
          }
      });
  }

  getStatusClass(estado: string) {
    switch (estado) {
      case 'ACTIVO': return 'bg-[#00ff9d]/10 text-[#00ff9d] border-[#00ff9d]/40';
      case 'INACTIVO': return 'bg-red-500/10 text-red-500 border-red-500/40';
      default: return 'bg-zinc-800 text-zinc-400 border-zinc-700';
    }
  }

  // --- SUCURSAL LOGIC ---
  openSucursalModal(tallerCod: string) {
    this.newSucursal = {
      id_taller: tallerCod,
      nombre: '',
      direccion: '',
      latitud: null,
      longitud: null,
      admin_usuario_id: ''
    };
    this.showSucursalModal = true;
    
    // Cargar candidatos a admin
    this.api.get<any[]>(`/sucursales/taller/${tallerCod}/candidatos-admin`).subscribe({
       next: (res) => this.candidatosAdmin = res,
       error: () => toast.error('Error cargando candidatos a administrador')
    });

    setTimeout(() => this.initMap(), 100);
  }

  initMap() {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    const mapElement = document.getElementById('sucursalMap');
    if (!mapElement) return;

    this.map = L.map('sucursalMap').setView([-12.0464, -77.0428], 10);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CARTO'
    }).addTo(this.map);

    const customIcon = L.divIcon({
        className: 'custom-pin',
        html: '<div style="background-color: #FF5733; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px rgba(255,87,51,0.8);"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    this.map.on('click', (e: L.LeafletMouseEvent) => {
        const lat = parseFloat(e.latlng.lat.toFixed(6));
        const lng = parseFloat(e.latlng.lng.toFixed(6));
        
        this.newSucursal.latitud = lat;
        this.newSucursal.longitud = lng;

        if (this.marker) {
            this.marker.setLatLng([lat, lng]);
        } else {
            this.marker = L.marker([lat, lng], { icon: customIcon }).addTo(this.map!);
        }

        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
          .then(res => res.json())
          .then(data => {
            if (data && data.display_name) {
              this.newSucursal.direccion = data.display_name;
            }
          });
    });
  }

  submitSucursalCreate() {
    if (!this.newSucursal.nombre || !this.newSucursal.direccion || !this.newSucursal.admin_usuario_id) {
      toast.warning('Complete todos los campos requeridos y seleccione un administrador');
      return;
    }
    this.creatingSucursal = true;

    const sucursalData = {
      nombre: this.newSucursal.nombre,
      direccion: this.newSucursal.direccion,
      latitud: this.newSucursal.latitud,
      longitud: this.newSucursal.longitud,
      id_taller: this.newSucursal.id_taller
    };

    this.api.post<any>('/sucursales/', sucursalData).subscribe({
      next: (suc) => {
        this.api.put<any>(`/sucursales/${suc.id}/asignar-admin/${this.newSucursal.admin_usuario_id}`, {}).subscribe({
          next: () => {
            toast.success('Sucursal registrada y administrador vinculado');
            this.creatingSucursal = false;
            this.showSucursalModal = false;
            this.loadAuthAndData(); // Recargar todo
          },
          error: (err) => {
            toast.error('Sucursal creada, pero falló la asignación de admin: ' + err.error?.detail);
            this.creatingSucursal = false;
          }
        });
      },
      error: (err) => {
        toast.error('Error al registrar sucursal: ' + err.error?.detail);
        this.creatingSucursal = false;
      }
    });
  }

  // --- ESPECIALIDADES LOGIC ---
  openEspecialidadesModal(sucursal: SucursalCard) {
      this.selectedSucursal = sucursal;
      this.selectedEspecialidadesIds = [];
      this.showEspecialidadesModal = true;
      this.loadingEspecialidades = true;

      this.api.get<any[]>(`/sucursales/${sucursal.id}/especialidades`).subscribe({
          next: (res) => {
              this.selectedEspecialidadesIds = res.map(r => r.id_especialidad);
              this.loadingEspecialidades = false;
          },
          error: () => {
              toast.error('Error al cargar especialidades de la sucursal');
              this.loadingEspecialidades = false;
          }
      });
  }

  isEspecialidadSelected(id: number): boolean {
      return this.selectedEspecialidadesIds.includes(id);
  }

  toggleEspecialidad(id: number) {
      const idx = this.selectedEspecialidadesIds.indexOf(id);
      if (idx > -1) {
          this.selectedEspecialidadesIds.splice(idx, 1);
      } else {
          this.selectedEspecialidadesIds.push(id);
      }
  }

  saveEspecialidades() {
      if (!this.selectedSucursal) return;
      this.savingEspecialidades = true;

      this.api.put(`/sucursales/${this.selectedSucursal.id}/especialidades`, {
          especialidades_ids: this.selectedEspecialidadesIds
      }).subscribe({
          next: () => {
              toast.success('Especialidades guardadas correctamente');
              this.savingEspecialidades = false;
              this.showEspecialidadesModal = false;
          },
          error: (err) => {
              toast.error('Error guardando especialidades: ' + err.error?.detail);
              this.savingEspecialidades = false;
          }
      });
  }
}
