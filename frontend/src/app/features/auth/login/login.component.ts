import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';

import { AuthService } from '../../../core/services/auth.service';
import { ThemeService } from '../../../core/services/theme.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, LucideAngularModule],
  template: `
    <div class="min-h-screen bg-zinc-50 dark:bg-[#0a0a0a] text-zinc-900 dark:text-zinc-100 font-sans flex flex-col selection:bg-[#FF5733] selection:text-white relative">
      
      <!-- Top minimal nav -->
      <nav class="p-6 flex justify-between items-center absolute w-full top-0 z-10">
        <a routerLink="/" class="inline-flex items-center gap-3 font-mono text-[10px] font-bold uppercase tracking-[.25em] text-zinc-500 hover:text-zinc-900 dark:hover:text-white transition-colors group">
          <lucide-icon name="arrow-left" class="w-4 h-4 group-hover:-translate-x-1 transition-transform"></lucide-icon> Volver al Inicio
        </a>
        <button 
          (click)="theme.toggleTheme()"
          class="p-2 border border-zinc-200 dark:border-[#222222] bg-white dark:bg-[#111111] hover:bg-zinc-100 dark:hover:bg-[#1a1a1a] transition-colors"
          aria-label="Alternar tema"
        >
          <lucide-icon [name]="theme.isDark ? 'sun' : 'moon'" class="w-4 h-4"></lucide-icon>
        </button>
      </nav>

      <div class="flex-1 flex items-center justify-center p-6 mt-16">
        <div class="w-full max-w-md bg-white dark:bg-[#0d0d0d] border border-zinc-200 dark:border-[#222222] shadow-2xl relative">
          
          <!-- Architectural corner details -->
          <div class="absolute top-0 left-0 w-2 h-2 border-t border-l border-zinc-900 dark:border-zinc-500"></div>
          <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-zinc-900 dark:border-zinc-500"></div>
          <div class="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-zinc-900 dark:border-zinc-500"></div>
          <div class="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-zinc-900 dark:border-zinc-500"></div>

          <!-- Header -->
          <div class="border-b border-zinc-200 dark:border-[#222222] p-8 pb-6 bg-[#0a0a0a]">
            <div class="font-mono text-xs font-bold tracking-widest flex items-center gap-2 mb-6 justify-center">
              <span class="text-[#FF5733]">■</span>
              FIELDWORK<span class="text-zinc-400 dark:text-zinc-600">_OS</span>
            </div>
            <h1 class="text-2xl font-bold tracking-tight text-center uppercase">Acceso al Sistema</h1>
            <p class="text-zinc-500 text-[10px] font-mono tracking-widest uppercase mt-2 text-center">Credenciales de Operador de Taller</p>
          </div>

          <form (ngSubmit)="onLogin()" #loginForm="ngForm" class="p-8 space-y-6">
            
            <div class="space-y-3">
              <label class="font-mono text-[9px] font-bold uppercase tracking-[.25em] text-zinc-500">
                Identificador de Usuario
              </label>
              <div class="relative">
                <lucide-icon name="mail" class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500"></lucide-icon>
                <input 
                  type="email"
                  name="correo"
                  [(ngModel)]="formData.correo"
                  required
                  placeholder="operador@taller.com"
                  class="w-full bg-zinc-50 dark:bg-[#050505] border border-zinc-300 dark:border-[#222222] text-sm pl-12 pr-4 py-4 outline-none focus:border-zinc-900 dark:focus:border-[#FF5733] transition-colors placeholder:text-zinc-700 font-mono"
                />
              </div>
            </div>

            <div class="space-y-3">
              <label class="flex justify-between font-mono text-[9px] font-bold uppercase tracking-[.25em] text-zinc-500 items-end">
                <span>Clave de Acceso</span>
                <a routerLink="/auth/register" class="text-[#FF5733] hover:underline normal-case tracking-normal font-sans text-xs font-medium">Registrar Unidad</a>
              </label>
              <div class="relative">
                <lucide-icon name="key-round" class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500"></lucide-icon>
                <input 
                  type="password"
                  name="contrasena"
                  [(ngModel)]="formData.contrasena"
                  required
                  placeholder="••••••••"
                  class="w-full bg-zinc-50 dark:bg-[#050505] border border-zinc-300 dark:border-[#222222] text-sm pl-12 pr-4 py-4 outline-none focus:border-zinc-900 dark:focus:border-[#FF5733] transition-colors font-mono tracking-[.2em]"
                />
              </div>
            </div>
            
            <!-- Error panel -->
            <div *ngIf="errorMessage" class="bg-red-950/40 border border-red-900/50 p-4 text-center">
              <p class="font-mono text-[9px] uppercase tracking-widest text-red-500 font-bold">{{ errorMessage }}</p>
            </div>

            <button 
              type="submit"
              [disabled]="loading"
              class="w-full bg-[#FF5733] text-white px-8 py-5 font-mono text-[11px] font-bold uppercase tracking-[.25em] hover:brightness-110 shadow-lg shadow-[#FF5733]/20 transition-all mt-4 flex items-center justify-center gap-3 disabled:opacity-50"
            >
              <lucide-icon *ngIf="loading" name="loader-2" class="animate-spin w-4 h-4"></lucide-icon>
              {{ loading ? 'Sincronizando...' : 'INICIAR SESIÓN' }}
            </button>
          </form>

        </div>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; }
  `]
})
export class LoginComponent {
  formData = {
    correo: '',
    contrasena: '',
    rol: 'admin' // Mantenemos internamente la lógica
  };

  loading = false;
  errorMessage = '';
  
  public theme = inject(ThemeService);
  private authService = inject(AuthService);
  private router = inject(Router);

  onLogin() {
    if (!this.formData.correo || !this.formData.contrasena) {
      this.errorMessage = 'CÓDIGOS DE ACCESO FALTANTES';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService.loginWeb(this.formData).subscribe({
      next: () => {
        this.loading = false;
        const user = this.authService.currentUser();
        const isSuperAdmin = !user?.taller;
        const target = isSuperAdmin ? '/app/super/dashboard' : '/app/dashboard';
        this.router.navigate([target]).then(success => {
          if (!success) {
            console.error('[Router] Navegación cancelada o fallida.');
          }
        }).catch(err => {
          console.error('[Router] Error fatal durante navegación:', err);
          this.errorMessage = 'ERROR INTERNO: ' + (err.message || 'La vista falló al cargar.');
        });
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.detail || 'FALLA EN AUTENTICACIÓN';
      }
    });
  }
}
