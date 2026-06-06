import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { LucideAngularModule } from 'lucide-angular';
import { ApiService } from '../../core/api/api.service';
import { FormsModule } from '@angular/forms';
import { toast } from 'ngx-sonner';

interface Tecnico {
  id: number;
  nombre: string;
  correo: string;
  telefono: string;
  estado: string;
  contrasena?: string;
  idTaller?: string;
  especialidades?: any[];
}

@Component({
  selector: 'app-tecnicos',
  standalone: true,
  imports: [CommonModule, LucideAngularModule, FormsModule],
  template: `
    <div class="p-8 lg:p-12 max-w-[1400px] mx-auto animate-in fade-in duration-700">
      
      <!-- HEADER -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12 border-b border-zinc-900 pb-8">
        <div>
          <h1 class="text-3xl font-bold tracking-tight mb-2 uppercase">Gestión de Personal</h1>
          <p class="font-mono text-[10px] uppercase tracking-[.25em] text-zinc-500">
            Administración de técnicos, roles y especialidades
          </p>
        </div>

        <button (click)="openModal()" 
                class="btn-industrial btn-industrial-primary shadow-lg shadow-primary/20">
          <lucide-icon name="plus" size="14"></lucide-icon> Registrar Técnico
        </button>
      </div>

      <!-- LISTING -->
      <div class="card-industrial overflow-hidden shadow-2xl">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-zinc-900/80 border-b border-zinc-800">
              <th class="p-6 font-mono text-[9px] uppercase tracking-widest text-zinc-400">ID_OP</th>
              <th class="p-6 font-mono text-[9px] uppercase tracking-widest text-zinc-400">Nombre Completo</th>
              <th class="p-6 font-mono text-[9px] uppercase tracking-widest text-zinc-400">Contacto / Correo</th>
              <th class="p-6 font-mono text-[9px] uppercase tracking-widest text-zinc-400">Especialidades (Rol)</th>
              <th class="p-6 font-mono text-[9px] uppercase tracking-widest text-zinc-400">Estado</th>
              <th class="p-6 font-mono text-[9px] uppercase tracking-widest text-zinc-400 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let t of tecnicos" class="border-b border-zinc-900/50 hover:bg-zinc-900/30 transition-colors group">
              <td class="p-6 font-mono text-[10px] text-zinc-500">#{{ t.id }}</td>
              <td class="p-6">
                <div class="font-bold text-sm tracking-tight text-white">{{ t.nombre }}</div>
              </td>
              <td class="p-6">
                <div class="text-xs text-zinc-300 mb-1 font-medium">{{ t.correo }}</div>
                <div class="text-[10px] font-mono text-zinc-500">{{ t.telefono }}</div>
              </td>
              <td class="p-6">
                <div class="flex flex-wrap gap-1">
                  <span *ngFor="let esp of (t.especialidades?.length ? t.especialidades : [])"
                        class="px-2 py-0.5 bg-primary/10 border border-primary/30 text-[8px] font-bold uppercase tracking-widest text-primary">
                    {{ esp.nombre }}
                  </span>
                  <span *ngIf="!t.especialidades?.length"
                        class="px-3 py-1 bg-zinc-900 border border-zinc-800 text-[9px] font-bold uppercase tracking-widest text-zinc-600">
                    SIN ROL ASIGNADO
                  </span>
                </div>
              </td>
              <td class="p-6">
                <div class="flex items-center gap-2">
                  <div [class]="t.estado === 'ACTIVO' ? 'bg-emerald-500' : 'bg-red-500'" class="w-1.5 h-1.5 rounded-full"></div>
                  <span class="text-[10px] font-bold uppercase tracking-widest" [class]="t.estado === 'ACTIVO' ? 'text-emerald-500' : 'text-red-500'">
                    {{ t.estado }}
                  </span>
                </div>
              </td>
              <td class="p-6 text-right">
                <div class="flex justify-end gap-2">
                  <button (click)="openModal(t)" class="w-10 h-10 border border-zinc-800 flex items-center justify-center hover:bg-zinc-900 transition-all text-zinc-400 hover:text-primary hover:border-primary" title="Editar perfil">
                    <lucide-icon name="settings" size="14"></lucide-icon>
                  </button>
                  <button (click)="openRolModal(t)" class="w-10 h-10 border border-zinc-800 flex items-center justify-center hover:bg-primary/10 hover:border-primary/30 transition-all text-zinc-400 hover:text-primary" title="Gestionar especialidades (CU13)">
                    <lucide-icon name="tag" size="14"></lucide-icon>
                  </button>
                  <button (click)="deleteTecnico(t.id)" class="w-10 h-10 border border-zinc-800 flex items-center justify-center hover:bg-red-950/20 hover:border-red-900 transition-all text-zinc-500 hover:text-red-500" title="Desactivar">
                    <lucide-icon name="log-out" size="14"></lucide-icon>
                  </button>
                </div>
              </td>
            </tr>
            <tr *ngIf="tecnicos.length === 0 && !loading">
              <td colspan="6" class="p-20 text-center font-mono text-[10px] uppercase tracking-widest text-zinc-600 italic">
                No se han detectado perfiles operativos en este taller.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- MODAL: EDITAR / CREAR TÉCNICO -->
      <div *ngIf="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
        <div class="bg-zinc-950 border border-zinc-800 w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-300">
          <div class="p-8 border-b border-zinc-900 flex justify-between items-center">
            <h2 class="font-bold text-lg uppercase tracking-widest">{{ editingId ? 'Editar Perfil' : 'Nuevo Técnico' }}</h2>
            <button (click)="closeModal()" class="text-zinc-600 hover:text-white transition-colors">
              <lucide-icon name="x" size="20"></lucide-icon>
            </button>
          </div>

          <div class="p-8 space-y-6">
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Nombre Completo</label>
              <input [(ngModel)]="form.nombre" type="text" 
                     class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary focus:ring-1 focus:ring-primary/20 outline-none transition-all">
            </div>
            
            <div class="grid grid-cols-2 gap-6">
              <div class="space-y-2">
                <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Correo Electrónico</label>
                <input [(ngModel)]="form.correo" type="email" 
                       class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none">
              </div>
              <div class="space-y-2">
                <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Teléfono</label>
                <input [(ngModel)]="form.telefono" type="text" 
                       class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none">
              </div>
            </div>

            <div class="space-y-2" *ngIf="!editingId">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Contraseña Temporal</label>
              <input [(ngModel)]="form.contrasena" type="password" 
                     class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none">
            </div>
          </div>

          <div class="p-8 bg-zinc-900/30 flex gap-4">
            <button (click)="closeModal()" 
                    [disabled]="saving"
                    class="flex-1 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500 hover:text-white disabled:opacity-30">
              Cancelar
            </button>
            <button (click)="save()" 
                    [disabled]="saving || !form.nombre || !form.correo"
                    class="flex-1 bg-primary text-white py-4 font-bold text-[10px] uppercase tracking-widest disabled:opacity-30 flex items-center justify-center gap-3">
              <span *ngIf="saving" class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              {{ saving ? 'Procesando...' : (editingId ? 'Guardar Cambios' : 'Confirmar Registro') }}
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL: GESTIONAR ROL / ESPECIALIDADES (CU13) -->
      <div *ngIf="showRolModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
        <div class="bg-zinc-950 border border-zinc-800 w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-300">
          <div class="p-8 border-b border-zinc-900 flex justify-between items-center">
            <div>
              <h2 class="font-bold text-lg uppercase tracking-widest">Gestionar Rol — CU13</h2>
              <p class="font-mono text-[9px] text-zinc-600 uppercase tracking-widest mt-1">{{ rolTecnicoNombre }} · Especialidades de servicio</p>
            </div>
            <button (click)="showRolModal = false" class="text-zinc-600 hover:text-white">
              <lucide-icon name="x" size="20"></lucide-icon>
            </button>
          </div>

          <div class="p-8 space-y-6">
            <p class="font-mono text-[10px] text-zinc-500 uppercase tracking-widest">Selecciona las especialidades que puede atender este técnico:</p>
            
            <div class="grid grid-cols-1 gap-px bg-zinc-900 max-h-64 overflow-y-auto">
              <div *ngFor="let esp of todasEspecialidades"
                   (click)="toggleEspecialidad(esp.id)"
                   class="bg-[#050505] p-5 flex items-center justify-between cursor-pointer group hover:bg-zinc-900/50 transition-colors">
                <div class="flex items-center gap-4">
                  <div [class.bg-primary]="selectedEspecialidades.includes(esp.id)"
                       class="w-4 h-4 border border-zinc-800 transition-colors flex items-center justify-center">
                    <lucide-icon *ngIf="selectedEspecialidades.includes(esp.id)" name="check" class="text-white" size="10"></lucide-icon>
                  </div>
                  <div>
                    <div class="font-bold text-sm" [class.text-primary]="selectedEspecialidades.includes(esp.id)">{{ esp.nombre }}</div>
                    <div class="text-[9px] uppercase tracking-widest text-zinc-600 mt-0.5">{{ esp.descripcion }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tags seleccionados -->
            <div *ngIf="selectedEspecialidades.length > 0" class="flex flex-wrap gap-2 pt-4 border-t border-zinc-900">
              <div *ngFor="let id of selectedEspecialidades" class="flex items-center gap-2 px-3 py-1.5 bg-primary/10 border border-primary/30 text-[9px] font-bold uppercase text-primary">
                {{ getEspNombre(id) }}
                <button (click)="toggleEspecialidad(id)" class="hover:text-white ml-1">×</button>
              </div>
            </div>
          </div>

          <div class="p-8 bg-zinc-900/30 flex gap-4">
            <button (click)="showRolModal = false" class="flex-1 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500 hover:text-white">
              Cancelar
            </button>
            <button (click)="saveRol()" 
                    [disabled]="savingRol"
                    class="flex-1 bg-primary text-white py-4 font-bold text-[10px] uppercase tracking-widest disabled:opacity-30 flex items-center justify-center gap-3">
              <span *ngIf="savingRol" class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              {{ savingRol ? 'Guardando...' : 'Confirmar Rol' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class TecnicosComponent implements OnInit {
  auth = inject(AuthService);

  tecnicos: Tecnico[] = [];
  loading = true;
  saving = false;
  showModal = false;
  editingId: number | null = null;
  currentWorkshop = this.auth.currentUser()?.taller?.cod || 'TALLER_01';

  // Rol modal (CU13)
  showRolModal = false;
  savingRol = false;
  rolTecnicoId: number | null = null;
  rolTecnicoNombre = '';
  todasEspecialidades: any[] = [];
  selectedEspecialidades: number[] = [];

  form: Partial<Tecnico> = {
    nombre: '',
    correo: '',
    telefono: '',
    contrasena: '123456',
    idTaller: this.currentWorkshop
  };

  constructor(private api: ApiService) {}

  ngOnInit() { 
    this.load(); 
    this.loadEspecialidades();
  }

  load() {
    this.api.get<Tecnico[]>(`/tecnicos/taller/${this.currentWorkshop}`).subscribe({
      next: (res) => { this.tecnicos = res; this.loading = false; },
      error: () => { this.loading = false; toast.error('Error al sincronizar personal'); }
    });
  }

  loadEspecialidades() {
    this.api.get<any[]>('/catalogos/especialidades').subscribe({
      next: (res) => this.todasEspecialidades = res,
      error: () => {}
    });
  }

  // ─── CRUD Técnico ────────────────────────────────────────────────
  openModal(t?: Tecnico) {
    if (t) {
      this.editingId = t.id;
      this.form = { nombre: t.nombre, correo: t.correo, telefono: t.telefono, contrasena: '', idTaller: this.currentWorkshop };
    } else {
      this.editingId = null;
      this.form = { nombre: '', correo: '', telefono: '', contrasena: '123456', idTaller: this.currentWorkshop };
    }
    this.showModal = true;
  }

  closeModal() { 
    if (this.saving) return;
    this.showModal = false; 
  }

  save() {
    if (!this.form.nombre || !this.form.correo) return;
    this.saving = true;
    const request = this.editingId 
      ? this.api.put(`/tecnicos/${this.editingId}`, this.form)
      : this.api.post('/tecnicos', this.form);

    request.subscribe({
      next: () => {
        toast.success(this.editingId ? 'Perfil actualizado' : 'Técnico registrado correctamente');
        this.saving = false;
        this.load();
        this.closeModal();
      },
      error: (err) => {
        this.saving = false;
        toast.error('Fallo en el registro', { description: err.error?.detail || 'Error de comunicación' });
      }
    });
  }

  deleteTecnico(id: number) {
    if (confirm('¿Desactivar este perfil operativo?')) {
      this.api.delete(`/tecnicos/${id}`).subscribe({
        next: () => { toast.success('Técnico desactivado'); this.load(); },
        error: () => toast.error('Fallo en la desactivación')
      });
    }
  }

  // ─── CU13: Gestionar Rol / Especialidades ────────────────────────
  openRolModal(t: Tecnico) {
    this.rolTecnicoId = t.id;
    this.rolTecnicoNombre = t.nombre;
    this.selectedEspecialidades = t.especialidades?.map((e: any) => e.id) || [];
    this.showRolModal = true;
  }

  toggleEspecialidad(id: number) {
    if (this.selectedEspecialidades.includes(id)) {
      this.selectedEspecialidades = this.selectedEspecialidades.filter(e => e !== id);
    } else {
      this.selectedEspecialidades.push(id);
    }
  }

  getEspNombre(id: number): string {
    return this.todasEspecialidades.find(e => e.id === id)?.nombre || `ID:${id}`;
  }

  saveRol() {
    if (!this.rolTecnicoId) return;
    this.savingRol = true;
    this.api.put(`/tecnicos/${this.rolTecnicoId}/especialidades`, this.selectedEspecialidades).subscribe({
      next: () => {
        toast.success('Rol actualizado correctamente');
        this.savingRol = false;
        this.showRolModal = false;
        this.load();
      },
      error: (err) => {
        this.savingRol = false;
        toast.error('Error al actualizar rol', { description: err.error?.detail || 'Error de comunicación' });
      }
    });
  }
}
