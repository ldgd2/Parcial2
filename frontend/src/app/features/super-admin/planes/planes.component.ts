import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SaasService, Plan, PlanCreate } from '../../../core/services/saas.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-planes',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `
<div class="min-h-full bg-[#050505] text-white">

  <!-- Header -->
  <div class="border-b border-zinc-900 px-8 py-6 flex items-center justify-between">
    <div>
      <h1 class="text-xs font-bold uppercase tracking-[.3em] text-white">Suscripciones & Planes</h1>
      <p class="text-[10px] text-zinc-600 font-mono mt-1 uppercase tracking-[.2em]">Administra los tiers de la plataforma</p>
    </div>
    <button (click)="openCreate()"
      class="bg-primary hover:bg-white text-black px-5 py-2.5 text-[10px] font-bold uppercase tracking-[.2em] transition-all flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      Nuevo Plan
    </button>
  </div>

  <div class="p-8">

    <!-- Loading -->
    <div *ngIf="loading" class="flex justify-center py-16">
      <div class="w-5 h-5 border-2 border-zinc-800 border-t-primary rounded-full animate-spin"></div>
    </div>

    <!-- Plans Grid -->
    <div *ngIf="!loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
      <div *ngFor="let plan of planes()"
        class="bg-black border flex flex-col"
        [ngClass]="planBorderClass(plan.nombre)">

        <!-- Plan Header -->
        <div class="p-5 border-b border-zinc-900">
          <div class="flex items-start justify-between mb-3">
            <span class="text-[8px] font-bold uppercase tracking-widest px-2 py-0.5 border" [ngClass]="planBadgeClass(plan.nombre)">
              {{ plan.nombre }}
            </span>
            <div class="flex gap-2">
              <button (click)="openEdit(plan)" class="text-zinc-700 hover:text-white transition-colors" title="Editar">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
              <button (click)="confirmDelete(plan)" class="text-zinc-700 hover:text-red-500 transition-colors" title="Eliminar">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
              </button>
            </div>
          </div>
          <div class="text-3xl font-black" [ngClass]="planPriceClass(plan.nombre)">
            {{ plan.precio_mensual | currency:'USD':'symbol':'1.0-0' }}
            <span class="text-sm font-normal text-zinc-600">/mes</span>
          </div>
          <p class="text-[10px] font-mono text-zinc-600 mt-2">{{ plan.descripcion || 'Sin descripción' }}</p>
        </div>

        <!-- Limits -->
        <div class="p-5 flex-1 space-y-3">
          <div class="text-[8px] font-bold uppercase tracking-widest text-zinc-700 mb-3">Límites</div>

          <div class="flex justify-between items-center">
            <span class="text-[9px] font-mono text-zinc-500">Sucursales</span>
            <span class="text-[10px] font-bold text-white">{{ plan.max_sucursales }}</span>
          </div>
          <div class="w-full bg-zinc-950 h-px"></div>

          <div class="flex justify-between items-center">
            <span class="text-[9px] font-mono text-zinc-500">Técnicos</span>
            <span class="text-[10px] font-bold text-white">{{ plan.max_tecnicos }}</span>
          </div>
          <div class="w-full bg-zinc-950 h-px"></div>

          <div class="flex justify-between items-center">
            <span class="text-[9px] font-mono text-zinc-500">Admins/Sucursal</span>
            <span class="text-[10px] font-bold text-white">{{ plan.max_admins_sucursal }}</span>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-5 py-3 border-t border-zinc-900">
          <div class="flex items-center justify-between">
            <span class="text-[8px] font-mono text-zinc-700 uppercase tracking-widest">Talleres en este plan</span>
            <span class="text-sm font-black text-white">{{ plan.total_talleres ?? 0 }}</span>
          </div>
        </div>

      </div>

      <!-- Empty -->
      <div *ngIf="planes().length === 0" class="col-span-4 py-16 text-center text-[10px] font-mono text-zinc-700 uppercase tracking-widest">
        No hay planes configurados. Crea el primero.
      </div>

    </div>
  </div>
</div>

<!-- ── Modal ── -->
<div *ngIf="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
  <div class="bg-[#050505] border border-zinc-800 w-full max-w-lg shadow-2xl overflow-hidden">

    <div class="px-6 py-4 border-b border-zinc-900 flex justify-between items-center bg-zinc-950">
      <h3 class="text-[10px] font-bold uppercase tracking-widest text-white">
        {{ isEditing ? 'Editar Plan — ' + editingPlan?.nombre : 'Nuevo Plan de Suscripción' }}
      </h3>
      <button (click)="closeModal()" class="text-zinc-600 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <form [formGroup]="planForm" (ngSubmit)="savePlan()" class="p-6 space-y-4">

      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2">
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Nombre del Plan *</label>
          <input type="text" formControlName="nombre" placeholder="Ej. Profesional"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>

        <div class="col-span-2">
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Descripción</label>
          <input type="text" formControlName="descripcion" placeholder="Breve descripción del plan"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>

        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Precio/Mes (USD) *</label>
          <input type="number" formControlName="precio_mensual" placeholder="0.00" min="0" step="0.01"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>

        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Máx. Sucursales *</label>
          <input type="number" formControlName="max_sucursales" min="1"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>

        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Máx. Técnicos *</label>
          <input type="number" formControlName="max_tecnicos" min="1"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>

        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Máx. Admins/Sucursal *</label>
          <input type="number" formControlName="max_admins_sucursal" min="1"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>
      </div>

      <div class="pt-4 flex justify-end gap-3 border-t border-zinc-900">
        <button type="button" (click)="closeModal()"
          class="px-5 py-2.5 border border-zinc-800 text-zinc-500 hover:text-white hover:bg-zinc-900 text-[9px] font-bold uppercase tracking-widest transition-colors">
          Cancelar
        </button>
        <button type="submit" [disabled]="planForm.invalid || saving"
          class="px-5 py-2.5 bg-primary disabled:bg-zinc-800 disabled:text-zinc-600 text-black text-[9px] font-bold uppercase tracking-widest hover:bg-white transition-colors flex items-center gap-2">
          <div *ngIf="saving" class="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></div>
          {{ saving ? 'Guardando...' : (isEditing ? 'Actualizar Plan' : 'Crear Plan') }}
        </button>
      </div>
    </form>
  </div>
</div>
  `
})
export class PlanesComponent implements OnInit {
  private saas = inject(SaasService);
  private fb = inject(FormBuilder);

  planes = signal<Plan[]>([]);
  loading = true;
  saving = false;
  showModal = false;
  isEditing = false;
  editingPlan: Plan | null = null;

  planForm: FormGroup = this.fb.group({
    nombre: ['', Validators.required],
    descripcion: [''],
    precio_mensual: [0, [Validators.required, Validators.min(0)]],
    max_sucursales: [1, [Validators.required, Validators.min(1)]],
    max_tecnicos: [5, [Validators.required, Validators.min(1)]],
    max_admins_sucursal: [1, [Validators.required, Validators.min(1)]],
  });

  ngOnInit() { this.loadPlanes(); }

  loadPlanes() {
    this.loading = true;
    this.saas.getPlanes().subscribe({
      next: (p) => { this.planes.set(p); this.loading = false; },
      error: () => { toast.error('Error al cargar planes'); this.loading = false; }
    });
  }

  openCreate() {
    this.isEditing = false;
    this.editingPlan = null;
    this.planForm.reset({ precio_mensual: 0, max_sucursales: 1, max_tecnicos: 5, max_admins_sucursal: 1 });
    this.showModal = true;
  }

  openEdit(plan: Plan) {
    this.isEditing = true;
    this.editingPlan = plan;
    this.planForm.patchValue({
      nombre: plan.nombre,
      descripcion: plan.descripcion ?? '',
      precio_mensual: plan.precio_mensual,
      max_sucursales: plan.max_sucursales,
      max_tecnicos: plan.max_tecnicos,
      max_admins_sucursal: plan.max_admins_sucursal,
    });
    this.showModal = true;
  }

  closeModal() { this.showModal = false; this.editingPlan = null; }

  savePlan() {
    if (this.planForm.invalid) return;
    this.saving = true;
    const v = this.planForm.value as PlanCreate;

    const obs = this.isEditing && this.editingPlan
      ? this.saas.updatePlan(this.editingPlan.id, v)
      : this.saas.createPlan(v);

    obs.subscribe({
      next: () => {
        toast.success(this.isEditing ? 'Plan actualizado' : 'Plan creado');
        this.saving = false;
        this.closeModal();
        this.loadPlanes();
      },
      error: (err) => {
        toast.error(err.error?.detail || 'Error al guardar');
        this.saving = false;
      }
    });
  }

  confirmDelete(plan: Plan) {
    if (!confirm(`¿Eliminar el plan "${plan.nombre}"? Esta acción es irreversible.`)) return;
    this.saas.deletePlan(plan.id).subscribe({
      next: () => { toast.success('Plan eliminado'); this.loadPlanes(); },
      error: (err) => toast.error(err.error?.detail || 'Error al eliminar')
    });
  }

  planBorderClass(nombre: string): string {
    return { Gratuita: 'border-zinc-800', Standar: 'border-blue-900/50', Profesional: 'border-purple-900/50', Deluxe: 'border-yellow-900/50' }[nombre] ?? 'border-zinc-800';
  }
  planBadgeClass(nombre: string): string {
    return { Gratuita: 'border-zinc-700 text-zinc-400', Standar: 'border-blue-900/50 text-blue-400', Profesional: 'border-purple-900/50 text-purple-400', Deluxe: 'border-yellow-900/50 text-yellow-400' }[nombre] ?? 'border-zinc-800 text-zinc-500';
  }
  planPriceClass(nombre: string): string {
    return { Gratuita: 'text-zinc-400', Standar: 'text-blue-400', Profesional: 'text-purple-400', Deluxe: 'text-yellow-400' }[nombre] ?? 'text-white';
  }
}
