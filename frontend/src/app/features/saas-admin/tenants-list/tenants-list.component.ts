import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SaasService, Tenant, Plan, SaasStats, TenantUser, TenantUserCreate } from '../../../core/services/saas.service';
import { toast } from 'ngx-sonner';

type ModalMode = 'create-tenant' | 'edit-tenant' | 'create-user' | null;
type StatusFilter = 'TODOS' | 'ACTIVO' | 'SUSPENDIDO' | 'CANCELADO';

@Component({
  selector: 'app-tenants-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `
<div class="min-h-full bg-[#050505] text-white">

  <!-- ── Header ──────────────────────────────────────────────────────────────── -->
  <div class="border-b border-zinc-900 px-8 py-6 flex items-center justify-between">
    <div>
      <h1 class="text-xs font-bold uppercase tracking-[.3em] text-white">Panel SaaS</h1>
      <p class="text-[10px] text-zinc-600 font-mono mt-1 uppercase tracking-[.2em]">Administración global de clientes y talleres</p>
    </div>
    <button (click)="openCreateTenant()"
      class="bg-primary hover:bg-white text-black px-5 py-2.5 text-[10px] font-bold uppercase tracking-[.2em] transition-all flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      Nuevo Taller
    </button>
  </div>

  <div class="p-8 space-y-8">

    <!-- ── Stats Cards ────────────────────────────────────────────────────────── -->
    <div *ngIf="stats()" class="grid grid-cols-2 lg:grid-cols-4 gap-4">

      <div class="bg-black border border-zinc-900 p-5 space-y-3">
        <div class="text-[9px] font-bold uppercase tracking-[.25em] text-zinc-600">Total Talleres</div>
        <div class="text-3xl font-black text-white">{{ stats()!.total_tenants }}</div>
        <div class="flex gap-3 text-[9px] font-mono">
          <span class="text-emerald-500">{{ stats()!.tenants_activos }} activos</span>
          <span class="text-zinc-600">·</span>
          <span class="text-yellow-500">{{ stats()!.tenants_suspendidos }} susp.</span>
        </div>
      </div>

      <div class="bg-black border border-zinc-900 p-5 space-y-3">
        <div class="text-[9px] font-bold uppercase tracking-[.25em] text-zinc-600">Usuarios Admin</div>
        <div class="text-3xl font-black text-white">{{ stats()!.total_usuarios }}</div>
        <div class="text-[9px] font-mono text-zinc-600">operadores + supervisores</div>
      </div>

      <div class="bg-black border border-zinc-900 p-5 space-y-3">
        <div class="text-[9px] font-bold uppercase tracking-[.25em] text-zinc-600">Técnicos</div>
        <div class="text-3xl font-black text-white">{{ stats()!.total_tecnicos }}</div>
        <div class="text-[9px] font-mono text-zinc-600">mecánicos activos en plataforma</div>
      </div>

      <div class="bg-black border border-zinc-900 p-5 space-y-3">
        <div class="text-[9px] font-bold uppercase tracking-[.25em] text-zinc-600">Ingresos / Mes</div>
        <div class="text-3xl font-black text-primary">{{ stats()!.ingresos_mensuales | currency:'USD':'symbol':'1.0-0' }}</div>
        <div class="text-[9px] font-mono text-zinc-600">estimado basado en planes</div>
      </div>

    </div>

    <!-- Stats skeleton -->
    <div *ngIf="!stats() && loadingStats" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div *ngFor="let i of [1,2,3,4]" class="bg-black border border-zinc-900 p-5 animate-pulse h-28"></div>
    </div>

    <!-- ── Filters ─────────────────────────────────────────────────────────────── -->
    <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
      <div class="relative flex-1">
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" [(ngModel)]="searchTerm" placeholder="Buscar por nombre, código o correo..."
          class="w-full pl-10 pr-4 py-2.5 bg-black border border-zinc-800 text-white text-xs focus:border-primary focus:ring-0 outline-none transition-colors font-mono placeholder-zinc-700">
      </div>

      <div class="flex gap-2">
        <button *ngFor="let s of statusOptions" (click)="statusFilter = s.value"
          [ngClass]="statusFilter === s.value ? 'bg-primary text-black border-primary' : 'bg-black text-zinc-500 border-zinc-800 hover:border-zinc-600'"
          class="px-3 py-2 border text-[9px] font-bold uppercase tracking-widest transition-all">
          {{ s.label }}
        </button>
      </div>

      <select [(ngModel)]="planFilter"
        class="px-3 py-2.5 bg-black border border-zinc-800 text-zinc-400 text-[10px] focus:border-primary focus:ring-0 outline-none uppercase tracking-wider">
        <option value="">Todos los planes</option>
        <option *ngFor="let p of planes()" [value]="p.nombre">{{ p.nombre }}</option>
      </select>
    </div>

    <!-- ── Tenants Table ───────────────────────────────────────────────────────── -->
    <div class="bg-black border border-zinc-900 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-zinc-900">
              <th class="px-6 py-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">Taller</th>
              <th class="px-6 py-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">Código</th>
              <th class="px-6 py-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">Plan</th>
              <th class="px-6 py-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">Admin</th>
              <th class="px-6 py-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">Equipo</th>
              <th class="px-6 py-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">Estado</th>
              <th class="px-6 py-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-900">

            <tr *ngFor="let tenant of filteredTenants"
              class="hover:bg-zinc-900/30 transition-colors cursor-pointer"
              [ngClass]="selectedTenant?.cod === tenant.cod ? 'bg-zinc-900/20' : ''">

              <td class="px-6 py-4">
                <div class="font-bold text-xs uppercase tracking-wider text-white">{{ tenant.nombre }}</div>
                <div class="text-[10px] font-mono text-zinc-600 mt-0.5">{{ tenant.direccion }}</div>
              </td>

              <td class="px-6 py-4">
                <span class="font-mono text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-1 text-zinc-400">
                  {{ tenant.cod }}
                </span>
              </td>

              <td class="px-6 py-4">
                <span [ngClass]="planColorClass(tenant.plan_nombre)"
                  class="px-2 py-0.5 border text-[9px] font-bold uppercase tracking-widest">
                  {{ tenant.plan_nombre || 'Sin plan' }}
                </span>
              </td>

              <td class="px-6 py-4 text-[10px] font-mono text-zinc-500">
                {{ tenant.admin_correo || '—' }}
              </td>

              <td class="px-6 py-4">
                <div class="flex gap-3 text-[10px] font-mono">
                  <span class="text-zinc-400">{{ tenant.total_usuarios }} adm</span>
                  <span class="text-zinc-600">·</span>
                  <span class="text-zinc-400">{{ tenant.total_tecnicos }} tec</span>
                </div>
              </td>

              <td class="px-6 py-4">
                <span [ngClass]="estadoColorClass(tenant.estado)"
                  class="px-2 py-0.5 border text-[9px] font-bold uppercase tracking-widest">
                  {{ tenant.estado }}
                </span>
              </td>

              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-3">
                  <button (click)="selectTenant(tenant)"
                    class="text-[9px] font-bold uppercase tracking-widest text-zinc-500 hover:text-primary transition-colors border border-zinc-800 hover:border-primary px-2.5 py-1">
                    Gestionar
                  </button>
                  <button (click)="openEditTenant(tenant)"
                    class="text-zinc-600 hover:text-white transition-colors" title="Editar">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  </button>
                  <button (click)="cycleStatus(tenant)"
                    [title]="'Estado actual: ' + tenant.estado"
                    class="text-zinc-600 hover:text-yellow-400 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                  </button>
                </div>
              </td>
            </tr>

            <tr *ngIf="filteredTenants.length === 0 && !loadingTenants">
              <td colspan="7" class="px-6 py-16 text-center text-[10px] font-mono text-zinc-700 uppercase tracking-widest">
                No se encontraron talleres con los filtros aplicados.
              </td>
            </tr>

            <tr *ngIf="loadingTenants">
              <td colspan="7" class="px-6 py-12 text-center">
                <div class="flex justify-center">
                  <div class="w-5 h-5 border-2 border-zinc-800 border-t-primary rounded-full animate-spin"></div>
                </div>
              </td>
            </tr>

          </tbody>
        </table>
      </div>

      <div class="px-6 py-3 border-t border-zinc-900 flex items-center justify-between">
        <span class="text-[9px] font-mono text-zinc-700 uppercase tracking-widest">
          {{ filteredTenants.length }} de {{ tenants().length }} talleres
        </span>
      </div>
    </div>

  </div>
</div>

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- Tenant Detail Side Panel                                                    -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->
<div *ngIf="selectedTenant" class="fixed inset-0 z-40 flex justify-end">
  <!-- Overlay -->
  <div class="flex-1 bg-black/60 backdrop-blur-sm" (click)="closeTenantPanel()"></div>

  <!-- Panel -->
  <div class="w-full max-w-2xl bg-[#050505] border-l border-zinc-800 flex flex-col h-full overflow-hidden shadow-2xl animate-slide-in-right">

    <!-- Panel Header -->
    <div class="px-6 py-5 border-b border-zinc-900 flex items-start justify-between flex-shrink-0">
      <div>
        <div class="flex items-center gap-3 mb-1">
          <span class="font-mono text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-0.5 text-zinc-500">{{ selectedTenant.cod }}</span>
          <span [ngClass]="estadoColorClass(selectedTenant.estado)"
            class="px-2 py-0.5 border text-[9px] font-bold uppercase tracking-widest">
            {{ selectedTenant.estado }}
          </span>
        </div>
        <h2 class="text-sm font-bold uppercase tracking-widest text-white">{{ selectedTenant.nombre }}</h2>
        <p class="text-[10px] font-mono text-zinc-600 mt-1">{{ selectedTenant.direccion }}</p>
      </div>
      <button (click)="closeTenantPanel()" class="text-zinc-600 hover:text-white transition-colors mt-1">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Plan Info -->
    <div class="px-6 py-4 border-b border-zinc-900 flex-shrink-0 grid grid-cols-3 gap-4">
      <div>
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-1">Plan</div>
        <span [ngClass]="planColorClass(selectedTenant.plan_nombre)"
          class="px-2 py-0.5 border text-[9px] font-bold uppercase tracking-widest">
          {{ selectedTenant.plan_nombre || 'Sin plan' }}
        </span>
      </div>
      <div>
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-1">Admins</div>
        <div class="text-lg font-black text-white">{{ selectedTenant.total_usuarios }}</div>
      </div>
      <div>
        <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-1">Técnicos</div>
        <div class="text-lg font-black text-white">{{ selectedTenant.total_tecnicos }}</div>
      </div>
    </div>

    <!-- Users Section Header -->
    <div class="px-6 py-4 border-b border-zinc-900 flex-shrink-0 flex items-center justify-between">
      <div>
        <h3 class="text-[10px] font-bold uppercase tracking-widest text-white">Usuarios del Taller</h3>
        <p class="text-[9px] font-mono text-zinc-600 mt-0.5">{{ tenantUsers.length }} registros</p>
      </div>
      <button (click)="openCreateUser()"
        class="bg-primary hover:bg-white text-black px-4 py-2 text-[9px] font-bold uppercase tracking-widest transition-all flex items-center gap-1.5">
        <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Nuevo Usuario
      </button>
    </div>

    <!-- Users List -->
    <div class="flex-1 overflow-y-auto">

      <!-- Loading -->
      <div *ngIf="loadingUsers" class="flex justify-center py-12">
        <div class="w-5 h-5 border-2 border-zinc-800 border-t-primary rounded-full animate-spin"></div>
      </div>

      <!-- Empty -->
      <div *ngIf="!loadingUsers && tenantUsers.length === 0"
        class="py-16 text-center text-[10px] font-mono text-zinc-700 uppercase tracking-widest">
        No hay usuarios registrados en este taller.
      </div>

      <!-- User rows -->
      <div *ngIf="!loadingUsers" class="divide-y divide-zinc-900">
        <div *ngFor="let u of tenantUsers" class="px-6 py-4 flex items-center justify-between hover:bg-zinc-900/30 transition-colors">
          <div class="flex items-center gap-4">
            <div class="w-9 h-9 bg-zinc-950 border border-zinc-800 flex items-center justify-center text-[11px] font-black uppercase"
              [ngClass]="u.tipo === 'TECNICO' ? 'text-blue-400' : 'text-primary'">
              {{ u.nombre.charAt(0) }}
            </div>
            <div>
              <div class="text-xs font-bold uppercase tracking-wider text-white">
                {{ u.nombre }} {{ u.apellido || '' }}
              </div>
              <div class="text-[10px] font-mono text-zinc-600 mt-0.5">{{ u.correo }}</div>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-[8px] font-bold uppercase tracking-widest border px-1.5 py-0.5"
                  [ngClass]="u.tipo === 'TECNICO' ? 'border-blue-900/50 text-blue-500' : 'border-purple-900/50 text-purple-500'">
                  {{ u.tipo === 'TECNICO' ? (u.rol_nombre || 'Técnico') : (u.rol_nombre || 'Admin') }}
                </span>
                <span *ngIf="u.telefono" class="text-[9px] font-mono text-zinc-600">{{ u.telefono }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3 flex-shrink-0">
            <span [ngClass]="u.estado === 'ACTIVO' ? 'border-emerald-900/50 text-emerald-500' : 'border-red-900/50 text-red-500'"
              class="px-2 py-0.5 border text-[8px] font-bold uppercase tracking-widest">
              {{ u.estado }}
            </span>
            <button (click)="toggleUserStatus(u)"
              [title]="u.estado === 'ACTIVO' ? 'Desactivar' : 'Activar'"
              class="text-zinc-700 hover:text-yellow-400 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>
            </button>
            <button (click)="promptResetPassword(u)"
              title="Resetear contraseña"
              class="text-zinc-700 hover:text-blue-400 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- Modals                                                                      -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->
<div *ngIf="modalMode" class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
  <div class="bg-[#050505] border border-zinc-800 w-full shadow-2xl overflow-hidden"
    [ngClass]="modalMode === 'create-user' ? 'max-w-xl' : 'max-w-lg'">

    <!-- Modal Header -->
    <div class="px-6 py-4 border-b border-zinc-900 flex justify-between items-center bg-zinc-950">
      <h3 class="text-[10px] font-bold uppercase tracking-widest text-white">
        <span *ngIf="modalMode === 'create-tenant'">Nuevo Taller Cliente</span>
        <span *ngIf="modalMode === 'edit-tenant'">Editar Taller — {{ editingTenant?.cod }}</span>
        <span *ngIf="modalMode === 'create-user'">Nuevo Usuario en {{ selectedTenant?.nombre }}</span>
      </h3>
      <button (click)="closeModal()" class="text-zinc-600 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- ── Create / Edit Tenant Form ── -->
    <form *ngIf="modalMode === 'create-tenant' || modalMode === 'edit-tenant'"
      [formGroup]="tenantForm" (ngSubmit)="saveTenant()" class="p-6 space-y-4">

      <div>
        <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Nombre del Taller *</label>
        <input type="text" formControlName="nombre" placeholder="Ej. Taller El Rayo S.A."
          class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
      </div>

      <div>
        <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Dirección</label>
        <input type="text" formControlName="direccion" placeholder="Ej. Av. Principal 123"
          class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
      </div>

      <div>
        <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Plan de Suscripción</label>
        <select formControlName="plan_id"
          class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
          <option [value]="null">Sin plan asignado</option>
          <option *ngFor="let p of planes()" [value]="p.id">
            {{ p.nombre }} — {{ p.precio_mensual | currency:'USD':'symbol':'1.0-0' }}/mes
          </option>
        </select>
      </div>

      <!-- Only on create -->
      <ng-container *ngIf="modalMode === 'create-tenant'">
        <div class="pt-2 border-t border-zinc-900">
          <div class="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-4">Administrador del Taller</div>
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Nombre</label>
                <input type="text" formControlName="admin_nombre" placeholder="Juan"
                  class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
              </div>
              <div>
                <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Apellido</label>
                <input type="text" formControlName="admin_apellido" placeholder="Pérez"
                  class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
              </div>
            </div>
            <div>
              <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Correo Admin *</label>
              <input type="email" formControlName="admin_correo" placeholder="admin@taller.com"
                class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors font-mono">
            </div>
            <div>
              <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Contraseña Inicial</label>
              <input type="text" formControlName="admin_contrasena" placeholder="Admin123!"
                class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors font-mono">
              <p class="text-[9px] text-zinc-700 mt-1.5 font-mono">Se usará Admin123! si se deja en blanco</p>
            </div>
          </div>
        </div>
      </ng-container>

      <div class="pt-4 flex justify-end gap-3 border-t border-zinc-900">
        <button type="button" (click)="closeModal()"
          class="px-5 py-2.5 border border-zinc-800 text-zinc-500 hover:text-white hover:bg-zinc-900 text-[9px] font-bold uppercase tracking-widest transition-colors">
          Cancelar
        </button>
        <button type="submit" [disabled]="tenantForm.invalid || saving"
          class="px-5 py-2.5 bg-primary disabled:bg-zinc-800 disabled:text-zinc-600 text-black text-[9px] font-bold uppercase tracking-widest hover:bg-white transition-colors flex items-center gap-2">
          <div *ngIf="saving" class="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></div>
          {{ saving ? 'Guardando...' : (modalMode === 'create-tenant' ? 'Crear Taller' : 'Guardar Cambios') }}
        </button>
      </div>
    </form>

    <!-- ── Create User Form ── -->
    <form *ngIf="modalMode === 'create-user'"
      [formGroup]="userForm" (ngSubmit)="saveUser()" class="p-6 space-y-4">

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Rol *</label>
          <select formControlName="rol_id"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors uppercase">
            <option value="">Seleccionar rol...</option>
            <option *ngFor="let r of availableRoles" [value]="r.id">{{ r.nombre }}</option>
          </select>
        </div>

        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Nombre *</label>
          <input type="text" formControlName="nombre" placeholder="Juan"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>

        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Apellido</label>
          <input type="text" formControlName="apellido" placeholder="Pérez"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors">
        </div>

        <div>
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Teléfono</label>
          <input type="text" formControlName="telefono" placeholder="Requerido para técnicos"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors font-mono">
        </div>

        <div class="col-span-2">
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Correo *</label>
          <input type="email" formControlName="correo" placeholder="usuario@taller.com"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors font-mono">
        </div>

        <div class="col-span-2">
          <label class="block text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-2">Contraseña temporal *</label>
          <input type="text" formControlName="contrasena" placeholder="Mínimo 6 caracteres"
            class="w-full px-4 py-3 bg-black border border-zinc-800 text-white text-xs focus:border-primary outline-none transition-colors font-mono">
        </div>
      </div>

      <div class="pt-4 flex justify-end gap-3 border-t border-zinc-900">
        <button type="button" (click)="closeModal()"
          class="px-5 py-2.5 border border-zinc-800 text-zinc-500 hover:text-white hover:bg-zinc-900 text-[9px] font-bold uppercase tracking-widest transition-colors">
          Cancelar
        </button>
        <button type="submit" [disabled]="userForm.invalid || saving"
          class="px-5 py-2.5 bg-primary disabled:bg-zinc-800 disabled:text-zinc-600 text-black text-[9px] font-bold uppercase tracking-widest hover:bg-white transition-colors flex items-center gap-2">
          <div *ngIf="saving" class="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></div>
          {{ saving ? 'Guardando...' : 'Crear Usuario' }}
        </button>
      </div>
    </form>

  </div>
</div>
  `,
  styles: [`
    @keyframes slideInRight {
      from { transform: translateX(100%); opacity: 0; }
      to   { transform: translateX(0);    opacity: 1; }
    }
    .animate-slide-in-right { animation: slideInRight 0.25s ease-out; }
  `]
})
export class TenantsListComponent implements OnInit {
  private saas = inject(SaasService);
  private fb = inject(FormBuilder);

  // ── State ──────────────────────────────────────────────────────────────────
  tenants = signal<Tenant[]>([]);
  tenantUsers: TenantUser[] = [];
  selectedTenant: Tenant | null = null;
  editingTenant: Tenant | null = null;

  loadingTenants = true;
  loadingStats = true;
  loadingUsers = false;
  saving = false;

  modalMode: ModalMode = null;
  searchTerm = '';
  statusFilter: StatusFilter = 'TODOS';
  planFilter = '';

  stats = signal<SaasStats | null>(null);
  planes = signal<Plan[]>([]);

  statusOptions: { label: string; value: StatusFilter }[] = [
    { label: 'Todos', value: 'TODOS' },
    { label: 'Activos', value: 'ACTIVO' },
    { label: 'Suspendidos', value: 'SUSPENDIDO' },
    { label: 'Cancelados', value: 'CANCELADO' },
  ];

  availableRoles = [
    { id: 2, nombre: 'ADMIN_TALLER' },
    { id: 3, nombre: 'ADMIN_SUCURSAL' },
    { id: 4, nombre: 'SUPERVISOR' },
    { id: 5, nombre: 'OPERADOR' },
    { id: 6, nombre: 'MECANICO' },
    { id: 7, nombre: 'TECNICO' },
  ];

  // ── Forms ──────────────────────────────────────────────────────────────────
  tenantForm: FormGroup = this.fb.group({
    nombre: ['', Validators.required],
    direccion: [''],
    plan_id: [null],
    admin_nombre: [''],
    admin_apellido: [''],
    admin_correo: ['', Validators.email],
    admin_contrasena: [''],
  });

  userForm: FormGroup = this.fb.group({
    nombre: ['', Validators.required],
    apellido: [''],
    correo: ['', [Validators.required, Validators.email]],
    contrasena: ['', [Validators.required, Validators.minLength(6)]],
    rol_id: ['', Validators.required],
    telefono: [''],
  });

  // ── Computed ───────────────────────────────────────────────────────────────
  get filteredTenants(): Tenant[] {
    const term = this.searchTerm.toLowerCase();
    return this.tenants().filter(t => {
      const matchSearch = !term ||
        t.nombre.toLowerCase().includes(term) ||
        t.cod.toLowerCase().includes(term) ||
        (t.admin_correo || '').toLowerCase().includes(term);
      const matchStatus = this.statusFilter === 'TODOS' || t.estado === this.statusFilter;
      const matchPlan = !this.planFilter || t.plan_nombre === this.planFilter;
      return matchSearch && matchStatus && matchPlan;
    });
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────
  ngOnInit() {
    this.loadTenants();
    this.loadStats();
    this.loadPlanes();
  }

  loadTenants() {
    this.loadingTenants = true;
    this.saas.getTenants().subscribe({
      next: (data) => { this.tenants.set(data); this.loadingTenants = false; },
      error: () => { toast.error('Error al cargar talleres'); this.loadingTenants = false; }
    });
  }

  loadStats() {
    this.loadingStats = true;
    this.saas.getStats().subscribe({
      next: (s) => { this.stats.set(s); this.loadingStats = false; },
      error: () => this.loadingStats = false
    });
  }

  loadPlanes() {
    this.saas.getPlanes().subscribe({
      next: (p) => this.planes.set(p),
      error: () => {}
    });
  }

  // ── Tenant Panel ───────────────────────────────────────────────────────────
  selectTenant(tenant: Tenant) {
    this.selectedTenant = tenant;
    this.tenantUsers = [];
    this.loadingUsers = true;
    this.saas.getTenantUsuarios(tenant.cod).subscribe({
      next: (users) => { this.tenantUsers = users; this.loadingUsers = false; },
      error: () => { toast.error('Error al cargar usuarios'); this.loadingUsers = false; }
    });
  }

  closeTenantPanel() {
    this.selectedTenant = null;
    this.tenantUsers = [];
  }

  // ── Status ─────────────────────────────────────────────────────────────────
  cycleStatus(tenant: Tenant) {
    const cycle: Record<string, string> = {
      ACTIVO: 'SUSPENDIDO',
      SUSPENDIDO: 'ACTIVO',
      CANCELADO: 'ACTIVO',
    };
    const next = cycle[tenant.estado] || 'ACTIVO';
    if (!confirm(`¿Cambiar estado de "${tenant.nombre}" a ${next}?`)) return;
    this.saas.updateStatus(tenant.cod, next).subscribe({
      next: (updated) => {
        this.tenants.update(list => list.map(t => t.cod === tenant.cod ? { ...t, ...updated } : t));
        if (this.selectedTenant?.cod === tenant.cod) {
          this.selectedTenant = { ...this.selectedTenant, ...updated };
        }
        this.loadStats();
        toast.success(`Estado actualizado a ${next}`);
      },
      error: () => toast.error('Error al cambiar estado')
    });
  }

  // ── User Actions ───────────────────────────────────────────────────────────
  toggleUserStatus(u: TenantUser) {
    if (!this.selectedTenant) return;
    const next = u.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    this.saas.cambiarEstadoUsuarioTenant(this.selectedTenant.cod, u.tipo, u.id, next).subscribe({
      next: () => { u.estado = next; toast.success('Estado actualizado'); },
      error: () => toast.error('Error al actualizar estado')
    });
  }

  promptResetPassword(u: TenantUser) {
    const nueva = prompt(`Nueva contraseña para ${u.nombre}:`);
    if (!nueva || nueva.length < 6) {
      if (nueva !== null) toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    if (!this.selectedTenant) return;
    this.saas.resetPasswordUsuarioTenant(this.selectedTenant.cod, u.tipo, u.id, nueva).subscribe({
      next: () => toast.success('Contraseña restablecida'),
      error: () => toast.error('Error al restablecer contraseña')
    });
  }

  // ── Modals ─────────────────────────────────────────────────────────────────
  openCreateTenant() {
    this.editingTenant = null;
    this.tenantForm.reset({ plan_id: null });
    this.modalMode = 'create-tenant';
  }

  openEditTenant(tenant: Tenant) {
    this.editingTenant = tenant;
    this.tenantForm.patchValue({
      nombre: tenant.nombre,
      direccion: tenant.direccion,
      plan_id: tenant.plan_id ?? null,
    });
    this.modalMode = 'edit-tenant';
  }

  openCreateUser() {
    this.userForm.reset();
    this.modalMode = 'create-user';
  }

  closeModal() {
    this.modalMode = null;
    this.editingTenant = null;
  }

  // ── Save ───────────────────────────────────────────────────────────────────
  saveTenant() {
    if (this.tenantForm.invalid) return;
    this.saving = true;
    const v = this.tenantForm.value;

    if (this.modalMode === 'edit-tenant' && this.editingTenant) {
      this.saas.updateTenant(this.editingTenant.cod, {
        nombre: v.nombre,
        direccion: v.direccion,
        plan_id: v.plan_id || undefined,
      }).subscribe({
        next: (updated) => {
          const idx = this.tenants().findIndex(t => t.cod === this.editingTenant!.cod);
          if (idx !== -1) this.tenants.update(list => list.map((t, i) => i === idx ? updated : t));
          toast.success('Taller actualizado');
          this.saving = false;
          this.closeModal();
        },
        error: (err) => {
          toast.error(err.error?.detail || 'Error al actualizar');
          this.saving = false;
        }
      });
    } else {
      this.saas.createTenant({
        nombre: v.nombre,
        direccion: v.direccion,
        plan_id: v.plan_id || undefined,
        admin_nombre: v.admin_nombre || undefined,
        admin_apellido: v.admin_apellido || undefined,
        admin_correo: v.admin_correo || undefined,
        admin_contrasena: v.admin_contrasena || undefined,
      }).subscribe({
        next: (created) => {
          this.tenants.update(list => [created, ...list]);
          this.loadStats();
          toast.success('Taller creado correctamente');
          this.saving = false;
          this.closeModal();
        },
        error: (err) => {
          toast.error(err.error?.detail || 'Error al crear taller');
          this.saving = false;
        }
      });
    }
  }

  saveUser() {
    if (this.userForm.invalid || !this.selectedTenant) return;
    this.saving = true;
    const v = this.userForm.value;
    const payload: TenantUserCreate = {
      nombre: v.nombre,
      apellido: v.apellido || undefined,
      correo: v.correo,
      contrasena: v.contrasena,
      rol_id: Number(v.rol_id),
      telefono: v.telefono || undefined,
    };

    this.saas.crearUsuarioEnTenant(this.selectedTenant.cod, payload).subscribe({
      next: (u) => {
        this.tenantUsers = [u, ...this.tenantUsers];
        if (this.selectedTenant) {
          if (u.tipo === 'TECNICO') this.selectedTenant.total_tecnicos = (this.selectedTenant.total_tecnicos || 0) + 1;
          else this.selectedTenant.total_usuarios = (this.selectedTenant.total_usuarios || 0) + 1;
        }
        toast.success('Usuario creado correctamente');
        this.saving = false;
        this.closeModal();
      },
      error: (err) => {
        toast.error(err.error?.detail || 'Error al crear usuario');
        this.saving = false;
      }
    });
  }

  // ── Style Helpers ──────────────────────────────────────────────────────────
  estadoColorClass(estado: string): string {
    return {
      ACTIVO: 'border-emerald-900/50 bg-emerald-900/10 text-emerald-500',
      SUSPENDIDO: 'border-yellow-900/50 bg-yellow-900/10 text-yellow-500',
      CANCELADO: 'border-red-900/50 bg-red-900/10 text-red-500',
    }[estado] ?? 'border-zinc-800 text-zinc-500';
  }

  planColorClass(plan?: string): string {
    return {
      Gratuita: 'border-zinc-700 text-zinc-400',
      Standar: 'border-blue-900/50 text-blue-400',
      Profesional: 'border-purple-900/50 text-purple-400',
      Deluxe: 'border-yellow-900/50 text-yellow-400',
    }[plan || ''] ?? 'border-zinc-800 text-zinc-600';
  }
}
// Triggering TS server update
