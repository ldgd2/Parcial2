import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { environment } from '../../../environments/environment';
import { RouterModule, Router } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { trigger, transition, style, animate, query, stagger } from '@angular/animations';
import { HttpClient } from '@angular/common/http';

interface Plan {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_mensual: number;
  max_sucursales: number;
  max_tecnicos: number;
  max_admins_sucursal: number;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule],
  animations: [
    trigger('fadeInUp', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(30px)' }),
        animate('0.6s cubic-bezier(0.16, 1, 0.3, 1)', style({ opacity: 1, transform: 'translateY(0)' }))
      ])
    ]),
    trigger('staggerList', [
      transition(':enter', [
        query('.stagger-item', [
          style({ opacity: 0, transform: 'translateY(20px)' }),
          stagger(100, [
            animate('0.5s ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
          ])
        ], { optional: true })
      ])
    ])
  ],
  template: `
    <div class="min-h-screen bg-[#050505] text-white selection:bg-[#FF5733] selection:text-white font-sans overflow-x-hidden">
      
      <!-- TOP NAVIGATION -->
      <nav class="border-b border-[#222222] bg-[#050505]/90 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-[1600px] mx-auto px-6 h-20 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2.5 h-2.5 bg-[#FF5733] shadow-[0_0_10px_#FF5733]"></div>
            <span class="font-mono text-xs font-bold tracking-widest uppercase text-white">FIELDWORK <span class="text-zinc-600">_OS</span></span>
          </div>
          <div class="flex items-center gap-4">
            <button (click)="irALogin()" class="text-zinc-400 hover:text-white font-bold text-[10px] tracking-widest uppercase transition-colors mr-4">
              INICIAR SESIÓN
            </button>
            <button (click)="irARegistro()" class="bg-[#FF5733] text-white px-6 py-2.5 font-bold text-[10px] tracking-widest uppercase hover:bg-[#e04c2c] transition-colors shadow-[0_0_15px_rgba(255,87,51,0.3)]">
              CREAR TALLER
            </button>
          </div>
        </div>
      </nav>

      <!-- HERO SECTION -->
      <main class="relative px-6 py-24 lg:py-32 max-w-[1600px] mx-auto" @fadeInUp>
         <!-- BG glow decorative -->
         <div class="absolute top-10 left-1/4 w-[600px] h-[600px] bg-[#FF5733]/10 blur-[150px] rounded-full pointer-events-none"></div>

         <div class="max-w-4xl relative z-10">
           <div class="inline-flex items-center gap-3 px-3 py-1.5 border border-[#222222] bg-[#111111] mb-8">
             <div class="w-1.5 h-1.5 bg-[#FF5733] animate-pulse"></div>
             <span class="font-mono text-[9px] font-bold uppercase tracking-[.25em] text-zinc-300">PLATAFORMA INTELIGENTE DE EMERGENCIA</span>
           </div>
           
           <h1 class="text-5xl md:text-7xl lg:text-[90px] font-extrabold tracking-tighter uppercase leading-[0.95] mb-8 text-white">
             CONTROL ABSOLUTO<br/><span class="text-transparent bg-clip-text bg-gradient-to-r from-white to-zinc-600">DEL CAMPO AL TALLER.</span>
           </h1>
           
           <p class="text-zinc-400 text-base md:text-xl max-w-2xl leading-relaxed mb-12">
             El primer sistema operativo (SaaS) diseñado para la gestión de incidencias mecánicas, despachos en tiempo real y asignación inteligente de técnicos. Deja atrás el caos, asume el control.
           </p>
           
           <div class="flex flex-col sm:flex-row gap-4">
             <button (click)="irARegistro()" class="bg-[#FF5733] text-white px-8 py-5 font-bold text-[12px] uppercase tracking-[.2em] shadow-lg shadow-[#FF5733]/20 hover:brightness-110 hover:shadow-[#FF5733]/40 transition-all flex items-center justify-center gap-3">
               COMIENZA GRATIS <lucide-icon name="arrow-right" size="16"></lucide-icon>
             </button>
             <button (click)="descargarApp()" class="bg-transparent border border-[#333333] text-white px-8 py-5 font-bold text-[12px] uppercase tracking-[.2em] hover:bg-[#111111] transition-all flex items-center justify-center gap-3">
               DESCARGAR APP <lucide-icon name="download" size="16"></lucide-icon>
             </button>
           </div>
         </div>
      </main>

      <!-- CARACTERISTICAS -->
      <section class="border-t border-[#222222] bg-[#0a0a0a] relative overflow-hidden">
        <div class="max-w-[1600px] mx-auto px-6 py-24 lg:py-32" @staggerList>
          <div class="text-center max-w-3xl mx-auto mb-20 stagger-item">
            <span class="font-mono text-[10px] uppercase tracking-[.25em] text-[#FF5733] font-bold block mb-4">¿CÓMO FUNCIONA?</span>
            <h2 class="text-3xl md:text-5xl font-extrabold tracking-tight uppercase text-white">FLUJO DE TRABAJO IMPLACABLE.</h2>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="p-10 border border-[#222222] bg-[#111111] hover:border-[#FF5733]/50 transition-colors stagger-item group">
               <div class="w-14 h-14 bg-[#FF5733]/10 border border-[#FF5733]/30 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform">
                 <lucide-icon name="map-pin" size="24" class="text-[#FF5733]"></lucide-icon>
               </div>
               <h3 class="text-2xl font-bold mb-4 tracking-tight">Geolocalización</h3>
               <p class="text-zinc-400 text-sm leading-relaxed">
                 Tus clientes reportan la emergencia y el sistema captura las coordenadas GPS exactas. Despacha la ayuda sin perder tiempo pidiendo direcciones.
               </p>
            </div>
            
            <div class="p-10 border border-[#222222] bg-[#111111] hover:border-[#FF5733]/50 transition-colors stagger-item group">
               <div class="w-14 h-14 bg-[#FF5733]/10 border border-[#FF5733]/30 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform">
                 <lucide-icon name="cpu" size="24" class="text-[#FF5733]"></lucide-icon>
               </div>
               <h3 class="text-2xl font-bold mb-4 tracking-tight">Asignación IA</h3>
               <p class="text-zinc-400 text-sm leading-relaxed">
                 Nuestro motor analiza la especialidad requerida (ej. Motor, Eléctrico) y asigna al técnico más cercano y disponible de tu flota automáticamente.
               </p>
            </div>

            <div class="p-10 border border-[#222222] bg-[#111111] hover:border-[#FF5733]/50 transition-colors stagger-item group">
               <div class="w-14 h-14 bg-[#FF5733]/10 border border-[#FF5733]/30 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform">
                 <lucide-icon name="shield-check" size="24" class="text-[#FF5733]"></lucide-icon>
               </div>
               <h3 class="text-2xl font-bold mb-4 tracking-tight">Multitenancy</h3>
               <p class="text-zinc-400 text-sm leading-relaxed">
                 Diseñado para empresas. Gestiona múltiples sucursales, técnicos y administradores bajo un mismo entorno aislado y seguro.
               </p>
            </div>
          </div>
        </div>
      </section>

      <!-- PRICING / PLANES -->
      <section class="border-t border-[#222222] bg-[#050505] relative py-24 lg:py-32">
         <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9IiMzMzMiLz48L3N2Zz4=')] opacity-[0.15]"></div>
         
         <div class="max-w-[1600px] mx-auto px-6 relative z-10" @staggerList>
            <div class="text-center max-w-3xl mx-auto mb-20 stagger-item">
              <span class="font-mono text-[10px] uppercase tracking-[.25em] text-[#FF5733] font-bold block mb-4">ESCALABILIDAD</span>
              <h2 class="text-3xl md:text-5xl font-extrabold tracking-tight uppercase text-white">ELIGE TU ARSENAL.</h2>
              <p class="mt-6 text-zinc-400 text-lg">Planes diseñados para talleres de un solo hombre hasta flotas corporativas.</p>
            </div>

            <div class="flex justify-center items-center h-20" *ngIf="cargandoPlanes">
              <div class="w-6 h-6 border-2 border-[#FF5733] border-t-transparent rounded-full animate-spin"></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto" *ngIf="!cargandoPlanes">
               
               <div *ngFor="let plan of planes; let i = index" 
                    [ngClass]="{'border-2 border-[#FF5733] shadow-[0_0_40px_rgba(255,87,51,0.1)]': plan.precio_mensual > 0 && i === 1, 'border border-[#222222] hover:border-[#333333]': plan.precio_mensual === 0 || i !== 1}"
                    class="bg-[#0a0a0a] p-10 flex flex-col hover:-translate-y-2 transition-transform duration-300 relative stagger-item">
                  
                  <div *ngIf="plan.precio_mensual > 0 && i === 1" class="absolute top-0 right-0 bg-[#FF5733] text-white text-[9px] font-bold uppercase tracking-widest px-3 py-1">RECOMENDADO</div>
                  
                  <h3 class="text-xl font-bold text-white uppercase tracking-wider mb-2">{{ plan.nombre }}</h3>
                  <div class="flex items-baseline gap-2 mb-6">
                    <span class="text-4xl font-extrabold">\${{ plan.precio_mensual }}</span>
                    <span class="text-zinc-500 font-mono text-sm">/ mes</span>
                  </div>
                  <p class="text-zinc-400 text-sm mb-8 flex-1">{{ plan.descripcion || 'Plan ideal para potenciar la gestión de tu taller mecáncio y llevarlo al siguiente nivel.' }}</p>
                  
                  <ul class="space-y-4 mb-8 font-mono text-xs text-zinc-300">
                    <li class="flex items-center gap-3">
                      <lucide-icon name="check" size="14" class="text-[#FF5733]"></lucide-icon> 
                      {{ plan.max_sucursales === 9999 ? 'Sucursales Ilimitadas' : 'Hasta ' + plan.max_sucursales + ' Sucursales' }}
                    </li>
                    <li class="flex items-center gap-3">
                      <lucide-icon name="check" size="14" class="text-[#FF5733]"></lucide-icon> 
                      {{ plan.max_tecnicos === 9999 ? 'Técnicos Ilimitados' : 'Hasta ' + plan.max_tecnicos + ' Técnicos' }}
                    </li>
                    <li class="flex items-center gap-3">
                      <lucide-icon name="check" size="14" class="text-[#FF5733]"></lucide-icon> 
                      {{ plan.max_admins_sucursal === 9999 ? 'Administradores Ilimitados' : 'Hasta ' + plan.max_admins_sucursal + ' Administradores' }}
                    </li>
                  </ul>
                  
                  <button (click)="irARegistro(plan.id)" 
                          [ngClass]="{'bg-[#FF5733] text-white hover:bg-[#e04c2c]': plan.precio_mensual > 0 && i === 1, 'bg-transparent border border-[#333333] hover:bg-[#111111] text-white': plan.precio_mensual === 0 || i !== 1}"
                          class="w-full py-4 font-bold text-[10px] uppercase tracking-[.2em] transition-colors shadow-lg">
                    Seleccionar
                  </button>
               </div>

            </div>
         </div>
      </section>

      <!-- PRE-FOOTER / CTA -->
      <footer class="border-t border-[#222222] py-20 px-6 flex flex-col items-center justify-center bg-[#000]">
         <div class="w-3 h-3 bg-[#FF5733] mb-6 animate-pulse"></div>
         <h2 class="text-zinc-500 font-mono text-[10px] tracking-[.3em] uppercase mb-4 text-center">Protocolo Operacional</h2>
         <p class="text-zinc-700 text-xs mb-8 text-center uppercase tracking-widest">SYSTEMS_NOMINAL</p>
         <div class="flex gap-4">
           <button (click)="irALogin()" class="text-zinc-400 border-b border-[#333] pb-1 hover:text-white transition-colors text-[10px] uppercase tracking-[.2em] font-bold">LOGIN</button>
           <button (click)="irARegistro()" class="text-[#FF5733] border-b border-[#FF5733]/30 pb-1 hover:border-[#FF5733] transition-colors text-[10px] uppercase tracking-[.2em] font-bold">CREAR CUENTA</button>
         </div>
      </footer>
    </div>
  `
})
export class HomeComponent implements OnInit {
  private http = inject(HttpClient);
  planes: Plan[] = [];
  cargandoPlanes = true;

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.cargarPlanes();
  }

  cargarPlanes() {
    this.http.get<Plan[]>(`${environment.apiUrl}/auth/planes`).subscribe({
      next: (data) => {
        this.planes = data;
        this.cargandoPlanes = false;
      },
      error: (err) => {
        console.error('Error cargando planes', err);
        this.cargandoPlanes = false;
      }
    });
  }

  irALogin() {
    this.router.navigate(['/auth/login']);
  }

  irARegistro(planId?: number) {
    if(planId) {
       this.router.navigate(['/auth/register'], { queryParams: { plan: planId } });
    } else {
       this.router.navigate(['/auth/register']);
    }
  }

  descargarApp() {
    window.location.href = `${environment.apiUrl}/apps/download/latest`;
  }
}

