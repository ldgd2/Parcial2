import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SaasService, BitacoraEntry } from '../../../core/services/saas.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-audit-log',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
<div class="min-h-full bg-[#050505] text-white">

  <div class="border-b border-zinc-900 px-8 py-6 flex items-center justify-between">
    <div>
      <h1 class="text-xs font-bold uppercase tracking-[.3em] text-white">Bitácora del Sistema</h1>
      <p class="text-[10px] text-zinc-600 font-mono mt-1 uppercase tracking-[.2em]">Registro de todas las operaciones</p>
    </div>
    <button (click)="loadLog()" class="border border-zinc-800 hover:border-zinc-600 text-zinc-500 hover:text-white px-4 py-2.5 text-[9px] font-bold uppercase tracking-widest transition-all flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
      Actualizar
    </button>
  </div>

  <!-- Filters -->
  <div class="px-8 py-4 border-b border-zinc-900 flex flex-wrap gap-3 items-center">
    <select [(ngModel)]="filterAccion" (ngModelChange)="loadLog()"
      class="px-3 py-2 bg-black border border-zinc-800 text-zinc-400 text-[10px] focus:border-primary outline-none uppercase tracking-wider">
      <option value="">Todas las acciones</option>
      <option value="LOGIN">LOGIN</option>
      <option value="INSERT">INSERT</option>
      <option value="UPDATE">UPDATE</option>
      <option value="DELETE">DELETE</option>
    </select>

    <input type="text" [(ngModel)]="filterTabla" (ngModelChange)="onTablaChange()" placeholder="Filtrar por tabla..."
      class="px-3 py-2 bg-black border border-zinc-800 text-white text-[10px] focus:border-primary outline-none font-mono placeholder-zinc-700 w-48">

    <select [(ngModel)]="pageSize" (ngModelChange)="loadLog()"
      class="px-3 py-2 bg-black border border-zinc-800 text-zinc-400 text-[10px] focus:border-primary outline-none">
      <option [value]="50">50 registros</option>
      <option [value]="100">100 registros</option>
      <option [value]="200">200 registros</option>
    </select>

    <div class="ml-auto text-[9px] font-mono text-zinc-700 uppercase tracking-widest">
      {{ entries().length }} entradas
    </div>
  </div>

  <!-- Table -->
  <div class="overflow-x-auto">
    <table class="w-full text-left border-collapse">
      <thead>
        <tr class="border-b border-zinc-900 bg-zinc-950">
          <th class="px-6 py-3 text-[8px] font-bold text-zinc-600 uppercase tracking-widest">#</th>
          <th class="px-6 py-3 text-[8px] font-bold text-zinc-600 uppercase tracking-widest">Acción</th>
          <th class="px-6 py-3 text-[8px] font-bold text-zinc-600 uppercase tracking-widest">Tabla</th>
          <th class="px-6 py-3 text-[8px] font-bold text-zinc-600 uppercase tracking-widest">Registro ID</th>
          <th class="px-6 py-3 text-[8px] font-bold text-zinc-600 uppercase tracking-widest">Usuario ID</th>
          <th class="px-6 py-3 text-[8px] font-bold text-zinc-600 uppercase tracking-widest">IP</th>
          <th class="px-6 py-3 text-[8px] font-bold text-zinc-600 uppercase tracking-widest">Fecha</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-zinc-900">

        <tr *ngIf="loading">
          <td colspan="7" class="px-6 py-12 text-center">
            <div class="flex justify-center">
              <div class="w-5 h-5 border-2 border-zinc-800 border-t-primary rounded-full animate-spin"></div>
            </div>
          </td>
        </tr>

        <tr *ngFor="let e of entries()" class="hover:bg-zinc-900/30 transition-colors">
          <td class="px-6 py-3 text-[10px] font-mono text-zinc-700">{{ e.id }}</td>
          <td class="px-6 py-3">
            <span class="text-[8px] font-bold uppercase tracking-widest px-2 py-0.5 border" [ngClass]="accionClass(e.accion)">
              {{ e.accion }}
            </span>
          </td>
          <td class="px-6 py-3 text-[10px] font-mono text-zinc-400">{{ e.tabla || '—' }}</td>
          <td class="px-6 py-3 text-[10px] font-mono text-zinc-600">{{ e.registro_id || '—' }}</td>
          <td class="px-6 py-3 text-[10px] font-mono text-zinc-600">{{ e.idUsuario ?? '—' }}</td>
          <td class="px-6 py-3 text-[10px] font-mono text-zinc-500">{{ e.ip || '—' }}</td>
          <td class="px-6 py-3 text-[9px] font-mono text-zinc-600">{{ e.fecha ? (e.fecha | date:'dd/MM/yy HH:mm:ss') : '—' }}</td>
        </tr>

        <tr *ngIf="!loading && entries().length === 0">
          <td colspan="7" class="px-6 py-16 text-center text-[9px] font-mono text-zinc-700 uppercase tracking-widest">
            No hay registros con los filtros aplicados.
          </td>
        </tr>

      </tbody>
    </table>
  </div>

  <!-- Pagination bar -->
  <div *ngIf="!loading" class="px-8 py-4 border-t border-zinc-900 flex items-center gap-4">
    <button (click)="prevPage()" [disabled]="offset === 0"
      class="border border-zinc-800 disabled:opacity-30 text-zinc-500 hover:text-white px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest transition-colors">
      ← Anterior
    </button>
    <span class="text-[9px] font-mono text-zinc-700">
      Página {{ (offset / pageSize) + 1 }}
    </span>
    <button (click)="nextPage()" [disabled]="entries().length < pageSize"
      class="border border-zinc-800 disabled:opacity-30 text-zinc-500 hover:text-white px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest transition-colors">
      Siguiente →
    </button>
  </div>

</div>
  `
})
export class AuditLogComponent implements OnInit {
  private saas = inject(SaasService);

  entries = signal<BitacoraEntry[]>([]);
  loading = false;

  filterAccion = '';
  filterTabla = '';
  pageSize = 100;
  offset = 0;

  private tablaTimer: any;

  ngOnInit() { this.loadLog(); }

  loadLog() {
    this.loading = true;
    this.saas.getAuditLog({
      limit: this.pageSize,
      offset: this.offset,
      accion: this.filterAccion || undefined,
      tabla: this.filterTabla || undefined,
    }).subscribe({
      next: (log) => { this.entries.set(log); this.loading = false; },
      error: () => { toast.error('Error al cargar bitácora'); this.loading = false; }
    });
  }

  onTablaChange() {
    clearTimeout(this.tablaTimer);
    this.tablaTimer = setTimeout(() => this.loadLog(), 500);
  }

  prevPage() { if (this.offset > 0) { this.offset -= this.pageSize; this.loadLog(); } }
  nextPage() { this.offset += this.pageSize; this.loadLog(); }

  accionClass(accion: string): string {
    return {
      LOGIN: 'border-blue-900/50 text-blue-400',
      INSERT: 'border-emerald-900/50 text-emerald-400',
      UPDATE: 'border-yellow-900/50 text-yellow-400',
      DELETE: 'border-red-900/50 text-red-400',
    }[accion] ?? 'border-zinc-800 text-zinc-500';
  }
}
