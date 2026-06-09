import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SaasService, Tenant } from '../../../core/services/saas.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-backups',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
<div class="min-h-full bg-[#050505] text-white">

  <div class="border-b border-zinc-900 px-8 py-6">
    <h1 class="text-xs font-bold uppercase tracking-[.3em] text-white">Backups & Exportación</h1>
    <p class="text-[10px] text-zinc-600 font-mono mt-1 uppercase tracking-[.2em]">Exporta datos de la plataforma en formato JSON</p>
  </div>

  <div class="p-8 space-y-8">

    <!-- ── Global Export ── -->
    <div class="bg-black border border-zinc-900 p-6">
      <div class="flex items-start justify-between">
        <div>
          <div class="text-[10px] font-bold uppercase tracking-widest text-white mb-1">Exportación Global</div>
          <p class="text-[10px] font-mono text-zinc-500 max-w-md">
            Descarga un resumen de todos los talleres, sin datos sensibles (contraseñas excluidas).
            Incluye: talleres, conteos de usuarios y técnicos.
          </p>
        </div>
        <button (click)="exportarGlobal()" [disabled]="downloading === 'global'"
          class="bg-primary hover:bg-white disabled:bg-zinc-800 disabled:text-zinc-600 text-black px-5 py-2.5 text-[9px] font-bold uppercase tracking-widest transition-all flex items-center gap-2 flex-shrink-0 ml-6">
          <div *ngIf="downloading === 'global'" class="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></div>
          <svg *ngIf="downloading !== 'global'" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="8 17 12 21 16 17"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/></svg>
          {{ downloading === 'global' ? 'Exportando...' : 'Descargar Global' }}
        </button>
      </div>
    </div>

    <!-- ── Per Tenant Export ── -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Exportar por Taller</div>
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" [(ngModel)]="searchTenant" placeholder="Buscar taller..."
            class="pl-8 pr-4 py-2 bg-black border border-zinc-800 text-white text-[10px] focus:border-primary outline-none font-mono placeholder-zinc-700 w-52">
        </div>
      </div>

      <div *ngIf="loadingTenants" class="flex justify-center py-8">
        <div class="w-5 h-5 border-2 border-zinc-800 border-t-primary rounded-full animate-spin"></div>
      </div>

      <div *ngIf="!loadingTenants" class="bg-black border border-zinc-900 divide-y divide-zinc-900">
        <div *ngFor="let t of filteredTenants" class="px-5 py-4 flex items-center justify-between hover:bg-zinc-900/30 transition-colors">
          <div class="flex items-center gap-4">
            <span class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 px-2 py-0.5 text-zinc-600">{{ t.cod }}</span>
            <div>
              <div class="text-xs font-bold uppercase tracking-wider text-white">{{ t.nombre }}</div>
              <div class="text-[9px] font-mono text-zinc-600 mt-0.5">
                {{ t.total_usuarios }} admins · {{ t.total_tecnicos }} técnicos
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <span [ngClass]="estadoClass(t.estado)" class="px-2 py-0.5 border text-[8px] font-bold uppercase tracking-widest">
              {{ t.estado }}
            </span>
            <button (click)="exportarTenant(t)" [disabled]="downloading === t.cod"
              class="border border-zinc-800 hover:border-primary text-zinc-500 hover:text-primary disabled:opacity-30 px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest transition-all flex items-center gap-1.5">
              <div *ngIf="downloading === t.cod" class="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></div>
              <svg *ngIf="downloading !== t.cod" xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="8 17 12 21 16 17"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/></svg>
              {{ downloading === t.cod ? 'Exportando...' : 'Exportar JSON' }}
            </button>
          </div>
        </div>

        <div *ngIf="filteredTenants.length === 0 && !loadingTenants" class="px-5 py-12 text-center text-[9px] font-mono text-zinc-700 uppercase tracking-widest">
          No se encontraron talleres.
        </div>
      </div>
    </div>

    <!-- ── Info Box ── -->
    <div class="border border-zinc-900 p-5 flex gap-4">
      <svg class="text-zinc-600 flex-shrink-0 mt-0.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <div class="space-y-1">
        <div class="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Sobre los backups</div>
        <p class="text-[9px] font-mono text-zinc-600 leading-relaxed">
          Las exportaciones JSON contienen datos operativos sin contraseñas ni información sensible.
          Para un backup completo de la base de datos PostgreSQL, ejecuta <code class="bg-zinc-900 px-1">pg_dump</code> directamente en el servidor.
          Los archivos exportados están en formato UTF-8 y son compatibles con herramientas estándar de importación.
        </p>
      </div>
    </div>

  </div>
</div>
  `
})
export class BackupsComponent implements OnInit {
  private saas = inject(SaasService);

  tenants = signal<Tenant[]>([]);
  loadingTenants = true;
  downloading: string | null = null;
  searchTenant = '';

  ngOnInit() {
    this.saas.getTenants().subscribe({
      next: (t) => { this.tenants.set(t); this.loadingTenants = false; },
      error: () => { toast.error('Error al cargar talleres'); this.loadingTenants = false; }
    });
  }

  get filteredTenants(): Tenant[] {
    const q = this.searchTenant.toLowerCase();
    return this.tenants().filter(t =>
      !q || t.nombre.toLowerCase().includes(q) || t.cod.toLowerCase().includes(q)
    );
  }

  exportarGlobal() {
    this.downloading = 'global';
    this.saas.exportarGlobal().subscribe({
      next: (blob) => {
        this.triggerDownload(blob, 'backup_global.json');
        this.downloading = null;
        toast.success('Exportación global descargada');
      },
      error: () => { toast.error('Error al exportar'); this.downloading = null; }
    });
  }

  exportarTenant(t: Tenant) {
    this.downloading = t.cod;
    this.saas.exportarTenant(t.cod).subscribe({
      next: (blob) => {
        this.triggerDownload(blob, `backup_${t.cod}.json`);
        this.downloading = null;
        toast.success(`Exportación de ${t.nombre} descargada`);
      },
      error: () => { toast.error('Error al exportar'); this.downloading = null; }
    });
  }

  private triggerDownload(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  estadoClass(estado: string): string {
    return { ACTIVO: 'border-emerald-900/50 text-emerald-500', SUSPENDIDO: 'border-yellow-900/50 text-yellow-500', CANCELADO: 'border-red-900/50 text-red-500' }[estado] ?? 'border-zinc-800 text-zinc-500';
  }
}
