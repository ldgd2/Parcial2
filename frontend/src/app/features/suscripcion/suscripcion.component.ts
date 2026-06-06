import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { LucideAngularModule } from 'lucide-angular';
import { ThemeService } from '../../core/services/theme.service';

@Component({
  selector: 'app-suscripcion',
  standalone: true,
  imports: [CommonModule, LucideAngularModule],
  template: `
    <div class="space-y-6">
      
      <!-- HEADER COMPONENT -->
      <header class="flex justify-between items-end border-b border-zinc-200 dark:border-zinc-800 pb-4">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 uppercase font-mono flex items-center gap-3">
            <lucide-icon name="credit-card" class="w-8 h-8 text-[#FF5733]"></lucide-icon>
            Módulo de Suscripción
          </h1>
          <p class="text-sm text-zinc-500 font-mono tracking-widest uppercase mt-2">
            Gestión de Plan y Límites de Operación
          </p>
        </div>
      </header>

      <!-- CONTENT -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6" *ngIf="auth.currentUser() as user">
        
        <!-- PLAN ACTUAL CARD -->
        <div class="lg:col-span-1 bg-white dark:bg-[#0a0a0a] border border-zinc-200 dark:border-zinc-800 shadow-sm p-6 relative overflow-hidden group hover:border-[#FF5733] transition-colors">
          <div class="absolute top-0 right-0 w-16 h-16 bg-[#FF5733]/10 rounded-bl-full -z-0"></div>
          
          <h3 class="font-mono text-[10px] font-bold tracking-widest text-zinc-500 uppercase mb-4">Plan Vigente</h3>
          
          <div class="flex items-center gap-4 mb-6">
            <div class="w-12 h-12 rounded-full bg-zinc-100 dark:bg-zinc-900 flex items-center justify-center border border-zinc-200 dark:border-zinc-800">
              <lucide-icon name="zap" class="w-6 h-6 text-[#FF5733]"></lucide-icon>
            </div>
            <div>
              <p class="text-2xl font-bold font-mono text-zinc-900 dark:text-white uppercase">{{ user.plan.nombre || 'Desconocido' }}</p>
              <p class="text-xs text-zinc-500 tracking-wide">Activo y Operando</p>
            </div>
          </div>

          <div class="space-y-4 font-mono text-sm">
            <div class="flex justify-between items-center border-b border-zinc-100 dark:border-zinc-800 pb-2">
              <span class="text-zinc-500">Inversión Mensual</span>
              <span class="font-bold text-zinc-900 dark:text-white">\${{ user.plan.precio_mensual || 0 }} USD</span>
            </div>
            
            <button class="w-full mt-4 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold tracking-widest uppercase text-xs py-3 hover:bg-[#FF5733] dark:hover:bg-[#FF5733] dark:hover:text-white transition-colors flex justify-center items-center gap-2">
              <lucide-icon name="arrow-up-circle" class="w-4 h-4"></lucide-icon> Actualizar Plan
            </button>
          </div>
        </div>

        <!-- LÍMITES CARD -->
        <div class="lg:col-span-2 bg-white dark:bg-[#0a0a0a] border border-zinc-200 dark:border-zinc-800 shadow-sm p-6 relative">
          <h3 class="font-mono text-[10px] font-bold tracking-widest text-zinc-500 uppercase mb-6 flex items-center gap-2">
            <lucide-icon name="bar-chart-2" class="w-4 h-4"></lucide-icon> Límites de Operación
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            <!-- Técnicos -->
            <div>
              <div class="flex justify-between text-xs font-mono uppercase mb-2">
                <span class="text-zinc-900 dark:text-zinc-100 font-bold">Unidades Técnicas</span>
                <span class="text-zinc-500">Límite: {{ user.plan.max_tecnicos || '∞' }}</span>
              </div>
              <div class="w-full h-3 bg-zinc-100 dark:bg-zinc-900 rounded-full overflow-hidden">
                <!-- Por ahora un mockup de progreso 30% -->
                <div class="h-full bg-[#FF5733] w-[30%] relative">
                  <div class="absolute top-0 right-0 bottom-0 left-0 bg-white/20 animate-pulse"></div>
                </div>
              </div>
            </div>

            <!-- Sucursales -->
            <div>
              <div class="flex justify-between text-xs font-mono uppercase mb-2">
                <span class="text-zinc-900 dark:text-zinc-100 font-bold">Sucursales Físicas</span>
                <span class="text-zinc-500">Límite: {{ user.plan.max_sucursales || '∞' }}</span>
              </div>
              <div class="w-full h-3 bg-zinc-100 dark:bg-zinc-900 rounded-full overflow-hidden">
                <!-- Por ahora un mockup de progreso 100% -->
                <div class="h-full bg-zinc-400 dark:bg-zinc-600 w-[100%]"></div>
              </div>
            </div>

          </div>
          
          <div class="mt-8 p-4 bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 text-sm text-zinc-600 dark:text-zinc-400 font-mono">
            <lucide-icon name="info" class="w-4 h-4 inline-block mr-2 text-[#FF5733]"></lucide-icon>
            Para incrementar los límites de operación o desbloquear características avanzadas (como reportes BI), debes actualizar tu plan de suscripción corporativo.
          </div>
        </div>

      </div>
    </div>
  `
})
export class SuscripcionComponent {
  public auth = inject(AuthService);
}
