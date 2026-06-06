import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SaasService, Tenant } from '../../../core/services/saas.service';

@Component({
  selector: 'app-tenants-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Gestión SaaS</h1>
          <p class="text-gray-500 dark:text-gray-400">Administración de clientes y talleres de la plataforma</p>
        </div>
        <button (click)="openModal()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm flex items-center gap-2">
          <i class="fas fa-plus"></i>
          <span>Nuevo Cliente</span>
        </button>
      </div>

      <!-- Tabla de Tenants -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead class="bg-gray-50 dark:bg-gray-900 border-b border-gray-100 dark:border-gray-700">
              <tr>
                <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Taller</th>
                <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Código</th>
                <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Plan</th>
                <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Admin Correo</th>
                <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
                <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr *ngFor="let tenant of tenants" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <td class="px-6 py-4">
                  <div class="font-medium text-gray-900 dark:text-white">{{tenant.nombre}}</div>
                  <div class="text-xs text-gray-500">{{tenant.direccion}}</div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                  <span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono">{{tenant.cod}}</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                  ID: {{tenant.plan_id || 'N/A'}}
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                  {{tenant.admin_correo || 'No asignado'}}
                </td>
                <td class="px-6 py-4">
                  <span class="px-3 py-1 rounded-full text-xs font-medium"
                    [ngClass]="{
                      'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400': tenant.estado === 'ACTIVO',
                      'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400': tenant.estado === 'SUSPENDIDO'
                    }">
                    {{tenant.estado}}
                  </span>
                </td>
                <td class="px-6 py-4 text-right space-x-2">
                  <button (click)="toggleStatus(tenant)" class="text-gray-400 hover:text-blue-600 transition-colors" title="Cambiar Estado">
                    <i class="fas fa-power-off"></i>
                  </button>
                  <button (click)="openModal(tenant)" class="text-gray-400 hover:text-blue-600 transition-colors" title="Editar">
                    <i class="fas fa-edit"></i>
                  </button>
                </td>
              </tr>
              <tr *ngIf="tenants.length === 0 && !loading">
                <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                  No hay clientes registrados en la plataforma.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Loading -->
      <div *ngIf="loading" class="flex justify-center p-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    </div>

    <!-- Modal Formulario -->
    <div *ngIf="showModal" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg overflow-hidden border border-gray-100 dark:border-gray-700 animate-fade-in-up">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            {{ isEditing ? 'Editar Cliente' : 'Nuevo Cliente SaaS' }}
          </h3>
          <button (click)="closeModal()" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form (ngSubmit)="saveTenant()" class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre del Taller *</label>
              <input type="text" [(ngModel)]="currentTenant.nombre" name="nombre" required
                class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500">
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Código (Ej. T001) *</label>
              <input type="text" [(ngModel)]="currentTenant.cod" name="cod" required [disabled]="isEditing"
                class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 disabled:opacity-50">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Plan ID *</label>
              <input type="number" [(ngModel)]="currentTenant.plan_id" name="plan_id" required
                class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500">
            </div>
            
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dirección</label>
              <input type="text" [(ngModel)]="currentTenant.direccion" name="direccion"
                class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500">
            </div>

            <div class="col-span-2" *ngIf="!isEditing">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Correo Administrador *</label>
              <input type="email" [(ngModel)]="currentTenant.admin_correo" name="admin_correo" required
                class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500">
              <p class="text-xs text-gray-500 mt-1">La contraseña por defecto será Admin123!</p>
            </div>
          </div>
          
          <div class="pt-4 flex justify-end gap-3">
            <button type="button" (click)="closeModal()" 
              class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
              Cancelar
            </button>
            <button type="submit" [disabled]="saving"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50">
              {{ saving ? 'Guardando...' : 'Guardar Cliente' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .animate-fade-in-up {
      animation: fadeInUp 0.3s ease-out;
    }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class TenantsListComponent implements OnInit {
  private saasService = inject(SaasService);
  
  tenants: Tenant[] = [];
  loading = true;
  saving = false;

  showModal = false;
  isEditing = false;
  currentTenant: Partial<Tenant> = {};

  ngOnInit() {
    this.loadTenants();
  }

  loadTenants() {
    this.loading = true;
    this.saasService.getTenants().subscribe({
      next: (res) => {
        this.tenants = res;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando tenants', err);
        this.loading = false;
      }
    });
  }

  toggleStatus(tenant: Tenant) {
    const newStatus = tenant.estado === 'ACTIVO' ? 'SUSPENDIDO' : 'ACTIVO';
    if(confirm(`¿Estás seguro que deseas cambiar el estado de este Taller a ${newStatus}?`)) {
      this.saasService.updateStatus(tenant.cod, newStatus).subscribe({
        next: () => this.loadTenants(),
        error: (err) => console.error(err)
      });
    }
  }

  openModal(tenant?: Tenant) {
    if (tenant) {
      this.isEditing = true;
      this.currentTenant = { ...tenant };
    } else {
      this.isEditing = false;
      this.currentTenant = { estado: 'ACTIVO', plan_id: 1 };
    }
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.currentTenant = {};
  }

  saveTenant() {
    this.saving = true;
    if (this.isEditing) {
      this.saasService.updateTenant(this.currentTenant.cod!, this.currentTenant).subscribe({
        next: () => {
          this.saving = false;
          this.closeModal();
          this.loadTenants();
        },
        error: (err) => {
          console.error(err);
          this.saving = false;
        }
      });
    } else {
      this.saasService.createTenant(this.currentTenant).subscribe({
        next: () => {
          this.saving = false;
          this.closeModal();
          this.loadTenants();
        },
        error: (err) => {
          console.error(err);
          alert(err.error?.detail || 'Error al crear el tenant');
          this.saving = false;
        }
      });
    }
  }
}
