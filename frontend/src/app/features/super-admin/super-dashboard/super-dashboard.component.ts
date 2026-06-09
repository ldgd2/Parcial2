import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SaasService, SaasStats, SaludSistema, BitacoraEntry } from '../../../core/services/saas.service';

@Component({
  selector: 'app-super-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
<div class="min-h-full bg-[#050505] text-white">

  <!-- ── Header ──────────────────────────────────────────────────────────────── -->
  <div class="border-b border-zinc-900 px-8 py-6">
    <div class="flex items-center gap-3 mb-1">
      <div class="w-2 h-2 rounded-full animate-pulse" [ngClass]="salud()?.db_conectada ? 'bg-emerald-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500'"></div>
      <span class="text-[9px] font-mono uppercase tracking-widest text-zinc-600">
        Sistema {{ salud()?.estado || 'verificando...' }} · v{{ salud()?.version || '—' }}
      </span>
    </div>
    <h1 class="text-sm font-black uppercase tracking-[.3em] text-white">Centro de Control</h1>
    <p class="text-[10px] text-zinc-600 font-mono mt-1 uppercase tracking-[.2em]">
      Super Admin — {{ salud()?.timestamp ? (salud()!.timestamp | date:'dd/MM/yyyy HH:mm') : '' }}
    </p>
  </div>

  <div class="p-8 space-y-10">

    <!-- ── System Health Bar ──────────────────────────────────────────────────── -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
      <div class="bg-black border border-zinc-900 p-4 flex flex-col gap-2">
        <div class="text-[8px] font-bold uppercase tracking-widest text-zinc-600">Base de Datos</div>
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full" [ngClass]="salud()?.db_conectada ? 'bg-emerald-500' : 'bg-red-500'"></div>
          <span class="text-xs font-bold" [ngClass]="salud()?.db_conectada ? 'text-emerald-400' : 'text-red-400'">
            {{ salud()?.db_conectada ? 'Conectada' : 'Error' }}
          </span>
        </div>
      </div>
      <div class="bg-black border border-zinc-900 p-4 flex flex-col gap-2">
        <div class="text-[8px] font-bold uppercase tracking-widest text-zinc-600">Talleres</div>
        <div class="text-2xl font-black text-white">{{ salud()?.total_talleres ?? '—' }}</div>
      </div>
      <div class="bg-black border border-zinc-900 p-4 flex flex-col gap-2">
        <div class="text-[8px] font-bold uppercase tracking-widest text-zinc-600">Usuarios Admin</div>
        <div class="text-2xl font-black text-white">{{ salud()?.total_usuarios ?? '—' }}</div>
      </div>
      <div class="bg-black border border-zinc-900 p-4 flex flex-col gap-2">
        <div class="text-[8px] font-bold uppercase tracking-widest text-zinc-600">Técnicos</div>
        <div class="text-2xl font-black text-white">{{ salud()?.total_tecnicos ?? '—' }}</div>
      </div>
      <div class="bg-black border border-zinc-900 p-4 flex flex-col gap-2">
        <div class="text-[8px] font-bold uppercase tracking-widest text-zinc-600">Ingresos / Mes</div>
        <div class="text-2xl font-black text-primary">
          {{ stats()?.ingresos_mensuales != null ? (stats()!.ingresos_mensuales | currency:'USD':'symbol':'1.0-0') : '—' }}
        </div>
      </div>
    </div>

    <!-- ── Tenant Status Breakdown ───────────────────────────────────────────── -->
    <div *ngIf="stats()" class="grid grid-cols-3 gap-4">
      <div class="bg-black border border-emerald-900/40 p-6 space-y-2">
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Talleres Activos</div>
        <div class="text-4xl font-black text-emerald-400">{{ stats()!.tenants_activos }}</div>
        <div class="text-[9px] font-mono text-zinc-700">
          {{ stats()!.total_tenants > 0 ? ((stats()!.tenants_activos / stats()!.total_tenants * 100) | number:'1.0-0') : 0 }}% del total
        </div>
        <div class="w-full bg-zinc-900 h-0.5 mt-2">
          <div class="bg-emerald-500 h-0.5" [style.width.%]="stats()!.total_tenants > 0 ? (stats()!.tenants_activos / stats()!.total_tenants * 100) : 0"></div>
        </div>
      </div>
      <div class="bg-black border border-yellow-900/40 p-6 space-y-2">
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Suspendidos</div>
        <div class="text-4xl font-black text-yellow-400">{{ stats()!.tenants_suspendidos }}</div>
        <div class="text-[9px] font-mono text-zinc-700">
          {{ stats()!.total_tenants > 0 ? ((stats()!.tenants_suspendidos / stats()!.total_tenants * 100) | number:'1.0-0') : 0 }}% del total
        </div>
        <div class="w-full bg-zinc-900 h-0.5 mt-2">
          <div class="bg-yellow-500 h-0.5" [style.width.%]="stats()!.total_tenants > 0 ? (stats()!.tenants_suspendidos / stats()!.total_tenants * 100) : 0"></div>
        </div>
      </div>
      <div class="bg-black border border-red-900/40 p-6 space-y-2">
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Cancelados</div>
        <div class="text-4xl font-black text-red-400">{{ stats()!.tenants_cancelados }}</div>
        <div class="text-[9px] font-mono text-zinc-700">
          {{ stats()!.total_tenants > 0 ? ((stats()!.tenants_cancelados / stats()!.total_tenants * 100) | number:'1.0-0') : 0 }}% del total
        </div>
        <div class="w-full bg-zinc-900 h-0.5 mt-2">
          <div class="bg-red-500 h-0.5" [style.width.%]="stats()!.total_tenants > 0 ? (stats()!.tenants_cancelados / stats()!.total_tenants * 100) : 0"></div>
        </div>
      </div>
    </div>

    <!-- ── Quick Actions Grid ─────────────────────────────────────────────────── -->
    <div>
      <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-4">Acciones Rápidas</div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">

        <a routerLink="/app/super/tenants"
          class="bg-black border border-zinc-900 hover:border-primary p-6 flex flex-col gap-4 transition-all group cursor-pointer">
          <div class="w-10 h-10 border border-zinc-800 group-hover:border-primary flex items-center justify-center transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-zinc-600 group-hover:text-primary transition-colors"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </div>
          <div>
            <div class="text-[10px] font-bold uppercase tracking-widest text-white">Talleres</div>
            <div class="text-[9px] font-mono text-zinc-600 mt-1">Gestionar tenants y usuarios</div>
          </div>
        </a>

        <a routerLink="/app/super/planes"
          class="bg-black border border-zinc-900 hover:border-primary p-6 flex flex-col gap-4 transition-all group cursor-pointer">
          <div class="w-10 h-10 border border-zinc-800 group-hover:border-primary flex items-center justify-center transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-zinc-600 group-hover:text-primary transition-colors"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
          </div>
          <div>
            <div class="text-[10px] font-bold uppercase tracking-widest text-white">Suscripciones</div>
            <div class="text-[9px] font-mono text-zinc-600 mt-1">Planes, precios y límites</div>
          </div>
        </a>

        <a routerLink="/app/super/restricciones"
          class="bg-black border border-zinc-900 hover:border-primary p-6 flex flex-col gap-4 transition-all group cursor-pointer">
          <div class="w-10 h-10 border border-zinc-800 group-hover:border-primary flex items-center justify-center transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-zinc-600 group-hover:text-primary transition-colors"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <div>
            <div class="text-[10px] font-bold uppercase tracking-widest text-white">Restricciones</div>
            <div class="text-[9px] font-mono text-zinc-600 mt-1">Feature flags del sistema</div>
          </div>
        </a>

        <a routerLink="/app/super/backups"
          class="bg-black border border-zinc-900 hover:border-primary p-6 flex flex-col gap-4 transition-all group cursor-pointer">
          <div class="w-10 h-10 border border-zinc-800 group-hover:border-primary flex items-center justify-center transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-zinc-600 group-hover:text-primary transition-colors"><polyline points="8 17 12 21 16 17"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/></svg>
          </div>
          <div>
            <div class="text-[10px] font-bold uppercase tracking-widest text-white">Backups</div>
            <div class="text-[9px] font-mono text-zinc-600 mt-1">Exportar y respaldar datos</div>
          </div>
        </a>

      </div>
    </div>

    <!-- ── Recent Audit Activity ──────────────────────────────────────────────── -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Actividad Reciente</div>
        <a routerLink="/app/super/audit-log" class="text-[9px] font-bold uppercase tracking-widest text-primary hover:text-white transition-colors">
          Ver todo →
        </a>
      </div>

      <div *ngIf="loadingAudit" class="flex justify-center py-8">
        <div class="w-5 h-5 border-2 border-zinc-800 border-t-primary rounded-full animate-spin"></div>
      </div>

      <div *ngIf="!loadingAudit" class="bg-black border border-zinc-900 divide-y divide-zinc-900">
        <div *ngFor="let entry of auditLog()" class="px-5 py-3 flex items-center gap-4 hover:bg-zinc-900/30 transition-colors">
          <span class="text-[8px] font-bold uppercase tracking-widest px-2 py-0.5 border flex-shrink-0"
            [ngClass]="accionClass(entry.accion)">
            {{ entry.accion }}
          </span>
          <div class="flex-1 min-w-0">
            <span class="text-[10px] font-mono text-zinc-400 truncate block">
              {{ entry.tabla || 'sistema' }}
              <span *ngIf="entry.registro_id" class="text-zinc-700"> · #{{ entry.registro_id }}</span>
            </span>
          </div>
          <div class="text-[9px] font-mono text-zinc-700 flex-shrink-0">
            {{ entry.ip }}
          </div>
          <div class="text-[9px] font-mono text-zinc-700 flex-shrink-0">
            {{ entry.fecha ? (entry.fecha | date:'dd/MM HH:mm') : '' }}
          </div>
        </div>
        <div *ngIf="auditLog().length === 0" class="px-5 py-8 text-center text-[9px] font-mono text-zinc-700 uppercase tracking-widest">
          Sin actividad registrada.
        </div>
      </div>
    </div>

  </div>
</div>
  `
})
export class SuperDashboardComponent implements OnInit {
  private saas = inject(SaasService);

  salud = signal<SaludSistema | null>(null);
  stats = signal<SaasStats | null>(null);
  auditLog = signal<BitacoraEntry[]>([]);
  loadingAudit = true;

  ngOnInit() {
    this.saas.getSalud().subscribe({ next: (s) => this.salud.set(s), error: () => {} });
    this.saas.getStats().subscribe({ next: (s) => this.stats.set(s), error: () => {} });
    this.saas.getAuditLog({ limit: 15 }).subscribe({
      next: (log) => { this.auditLog.set(log); this.loadingAudit = false; },
      error: () => { this.loadingAudit = false; }
    });
  }

  accionClass(accion: string): string {
    return {
      LOGIN:  'border-blue-900/50 text-blue-400',
      INSERT: 'border-emerald-900/50 text-emerald-400',
      UPDATE: 'border-yellow-900/50 text-yellow-400',
      DELETE: 'border-red-900/50 text-red-400',
    }[accion] ?? 'border-zinc-800 text-zinc-500';
  }
}
