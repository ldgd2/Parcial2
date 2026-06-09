import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SaasService, Restricciones } from '../../../core/services/saas.service';
import { toast } from 'ngx-sonner';

interface ToggleItem {
  clave: keyof Restricciones;
  label: string;
  descripcion: string;
  tipo: 'boolean' | 'number';
  peligroso?: boolean;
}

@Component({
  selector: 'app-restricciones',
  standalone: true,
  imports: [CommonModule],
  template: `
<div class="min-h-full bg-[#050505] text-white">

  <div class="border-b border-zinc-900 px-8 py-6 flex items-center justify-between">
    <div>
      <h1 class="text-xs font-bold uppercase tracking-[.3em] text-white">Restricciones del Sistema</h1>
      <p class="text-[10px] text-zinc-600 font-mono mt-1 uppercase tracking-[.2em]">Feature flags y configuración global de la plataforma</p>
    </div>
    <div *ngIf="loading" class="text-[9px] font-mono text-zinc-600 uppercase tracking-widest">Cargando...</div>
  </div>

  <div class="p-8 space-y-6" *ngIf="restricciones()">

    <!-- Warning banner for maintenance mode -->
    <div *ngIf="restricciones()!.modo_mantenimiento"
      class="border border-yellow-900/60 bg-yellow-900/10 p-4 flex items-center gap-3">
      <svg class="text-yellow-400 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      <div>
        <div class="text-[10px] font-bold uppercase tracking-widest text-yellow-400">Modo Mantenimiento Activo</div>
        <p class="text-[9px] font-mono text-yellow-600 mt-0.5">Los clientes y talleres no podrán acceder a la plataforma en este momento.</p>
      </div>
    </div>

    <!-- Toggles grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div *ngFor="let item of toggleItems"
        class="bg-black border p-5 flex items-start justify-between gap-4 transition-colors"
        [ngClass]="item.peligroso ? 'border-red-900/40 hover:border-red-900/60' : 'border-zinc-900 hover:border-zinc-800'">

        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <div class="text-[10px] font-bold uppercase tracking-wider text-white">{{ item.label }}</div>
            <span *ngIf="item.peligroso" class="text-[7px] font-bold uppercase tracking-widest border border-red-900/50 text-red-500 px-1 py-0.5">
              Crítico
            </span>
          </div>
          <p class="text-[9px] font-mono text-zinc-600 leading-relaxed">{{ item.descripcion }}</p>

          <!-- Number input for non-boolean items -->
          <div *ngIf="item.tipo === 'number'" class="mt-3 flex items-center gap-3">
            <input type="number" [value]="restricciones()![item.clave]" min="1" max="10000"
              (change)="updateNumber(item.clave, $event)"
              class="w-24 px-3 py-1.5 bg-zinc-950 border border-zinc-800 text-white text-xs focus:border-primary outline-none font-mono">
            <span class="text-[9px] font-mono text-zinc-600">emergencias simultáneas</span>
          </div>
        </div>

        <!-- Toggle for boolean items -->
        <div *ngIf="item.tipo === 'boolean'" class="flex-shrink-0 mt-0.5">
          <button (click)="toggle(item.clave)"
            [disabled]="saving === item.clave"
            class="relative w-11 h-6 rounded-full transition-colors focus:outline-none disabled:opacity-50"
            [ngClass]="restricciones()![item.clave] ? (item.peligroso ? 'bg-red-600' : 'bg-primary') : 'bg-zinc-800'">
            <span class="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform"
              [ngClass]="restricciones()![item.clave] ? 'translate-x-5' : 'translate-x-0'"></span>
          </button>
          <div class="text-[8px] font-mono text-center mt-1"
            [ngClass]="restricciones()![item.clave] ? 'text-emerald-500' : 'text-zinc-600'">
            {{ restricciones()![item.clave] ? 'ON' : 'OFF' }}
          </div>
        </div>

      </div>
    </div>

    <!-- Info -->
    <div class="border border-zinc-900 p-5 flex gap-4">
      <svg class="text-zinc-600 flex-shrink-0 mt-0.5" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p class="text-[9px] font-mono text-zinc-600 leading-relaxed">
        Los cambios se aplican inmediatamente en el servidor. Estas restricciones se resetean al reiniciar el servidor
        (almacenamiento en memoria). Para persistencia permanente, contacta al equipo de infraestructura para
        configurar variables de entorno en el servidor de producción.
      </p>
    </div>

  </div>

  <div *ngIf="loading" class="flex justify-center py-16">
    <div class="w-5 h-5 border-2 border-zinc-800 border-t-primary rounded-full animate-spin"></div>
  </div>

</div>
  `
})
export class RestriccionesComponent implements OnInit {
  private saas = inject(SaasService);

  restricciones = signal<Restricciones | null>(null);
  loading = true;
  saving: string | null = null;

  toggleItems: ToggleItem[] = [
    {
      clave: 'modo_mantenimiento',
      label: 'Modo Mantenimiento',
      descripcion: 'Bloquea el acceso de todos los usuarios a la plataforma (talleres y clientes). Solo el super admin puede acceder.',
      tipo: 'boolean',
      peligroso: true,
    },
    {
      clave: 'registro_publico_habilitado',
      label: 'Registro Público',
      descripcion: 'Permite que nuevos talleres se registren en la plataforma desde el portal público.',
      tipo: 'boolean',
    },
    {
      clave: 'nuevos_talleres_habilitados',
      label: 'Creación de Talleres',
      descripcion: 'Habilita la creación de nuevos talleres desde el panel de super admin.',
      tipo: 'boolean',
    },
    {
      clave: 'notificaciones_push_habilitadas',
      label: 'Notificaciones Push (FCM)',
      descripcion: 'Activa o desactiva el envío de notificaciones push a técnicos y clientes vía Firebase Cloud Messaging.',
      tipo: 'boolean',
    },
    {
      clave: 'ia_clasificacion_habilitada',
      label: 'IA — Clasificación Automática',
      descripcion: 'Permite que el motor de IA clasifique y asigne emergencias automáticamente.',
      tipo: 'boolean',
    },
    {
      clave: 'stripe_habilitado',
      label: 'Pagos Stripe',
      descripcion: 'Habilita el procesamiento de pagos a través de Stripe para suscripciones.',
      tipo: 'boolean',
    },
    {
      clave: 'logs_verboso',
      label: 'Logs Verbose',
      descripcion: 'Aumenta el nivel de detalle en los logs del servidor. Usar solo para debugging en producción.',
      tipo: 'boolean',
    },
    {
      clave: 'max_emergencias_simultaneas',
      label: 'Máx. Emergencias Simultáneas',
      descripcion: 'Límite global de emergencias activas que el sistema puede manejar al mismo tiempo.',
      tipo: 'number',
    },
  ];

  ngOnInit() {
    this.saas.getRestricciones().subscribe({
      next: (r) => { this.restricciones.set(r); this.loading = false; },
      error: () => { toast.error('Error al cargar restricciones'); this.loading = false; }
    });
  }

  toggle(clave: keyof Restricciones) {
    const actual = this.restricciones();
    if (!actual) return;
    const newVal = !actual[clave];

    if (clave === 'modo_mantenimiento' && newVal) {
      if (!confirm('⚠️ Activar el modo mantenimiento bloqueará el acceso a TODOS los usuarios. ¿Continuar?')) return;
    }

    this.saving = clave;
    this.saas.toggleRestriccion(clave, newVal).subscribe({
      next: (r) => {
        this.restricciones.set(r);
        this.saving = null;
        toast.success(`${clave} → ${newVal ? 'activado' : 'desactivado'}`);
      },
      error: () => { toast.error('Error al actualizar'); this.saving = null; }
    });
  }

  updateNumber(clave: keyof Restricciones, event: Event) {
    const val = Number((event.target as HTMLInputElement).value);
    if (!val || val < 1) return;
    this.saving = clave;
    this.saas.toggleRestriccion(clave, val).subscribe({
      next: (r) => { this.restricciones.set(r); this.saving = null; toast.success('Límite actualizado'); },
      error: () => { toast.error('Error al actualizar'); this.saving = null; }
    });
  }
}
