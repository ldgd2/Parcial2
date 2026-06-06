import { Component, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { trigger, transition, style, animate } from '@angular/animations';
import { LucideAngularModule } from 'lucide-angular';

import { CardComponent } from '../../../shared/ui/card/card.component';
import { InputComponent } from '../../../shared/ui/input/input.component';
import { ButtonComponent } from '../../../shared/ui/button/button.component';
import { MapPickerComponent } from '../../../shared/ui/map-picker/map-picker.component';

import { ApiService } from '../../../core/api/api.service';
import { StripeService } from '../../../core/services/stripe.service';
import { StripeElements, Stripe } from '@stripe/stripe-js';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule, 
    RouterModule, 
    InputComponent, 
    MapPickerComponent,
    LucideAngularModule
  ],
  animations: [
    trigger('slideAnimation', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateX(20px)' }),
        animate('0.4s ease-out', style({ opacity: 1, transform: 'translateX(0)' }))
      ]),
      transition(':leave', [
        animate('0.4s ease-in', style({ opacity: 0, transform: 'translateX(-20px)' }))
      ])
    ])
  ],
  template: `
    <div class="min-h-screen bg-[#050505] text-white flex flex-col font-sans overflow-x-hidden">
      <!-- Top Nav -->
      <nav class="border-b border-[#222222] bg-[#050505] h-16 flex items-center px-6">
        <a routerLink="/" class="flex items-center gap-3">
          <div class="w-2 h-2 bg-[#FF5733]"></div>
          <span class="font-mono text-[10px] font-bold tracking-widest uppercase">FIELDWORK <span class="text-zinc-600">_OS</span></span>
        </a>
      </nav>

      <div class="flex-1 flex flex-col items-center py-12 px-4 max-w-4xl mx-auto w-full">
        <!-- Progress Bar -->
        <div class="w-full flex justify-between items-center mb-12 relative">
          <div class="absolute top-1/2 left-0 w-full h-px bg-[#222222] -z-10"></div>
          <div class="absolute top-1/2 left-0 h-px bg-[#FF5733] transition-all duration-500 -z-10" [style.width]="(step - 1) * 33.33 + '%'"></div>
          
          <div *ngFor="let s of [1,2,3,4]" class="flex flex-col items-center gap-2 bg-[#050505] px-2">
            <div class="w-8 h-8 rounded-full border-2 flex items-center justify-center font-mono text-xs font-bold transition-colors"
                 [ngClass]="{
                   'border-[#FF5733] bg-[#FF5733]/10 text-[#FF5733]': step === s,
                   'border-[#FF5733] bg-[#FF5733] text-white': step > s,
                   'border-[#333333] text-zinc-600': step < s
                 }">
              <lucide-icon *ngIf="step > s" name="check" size="14"></lucide-icon>
              <span *ngIf="step <= s">{{ s }}</span>
            </div>
            <span class="text-[9px] uppercase tracking-widest font-bold" [ngClass]="step >= s ? 'text-[#FF5733]' : 'text-zinc-600'">
              {{ getStepName(s) }}
            </span>
          </div>
        </div>

        <div class="w-full relative min-h-[500px]">
          <!-- STEP 1: PLAN -->
          <div *ngIf="step === 1" @slideAnimation class="w-full">
            <h2 class="text-3xl font-extrabold uppercase mb-8 text-center">SELECCIONA TU PLAN OPERATIVO</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <!-- Free -->
              <div class="border border-[#222222] bg-[#0a0a0a] p-6 cursor-pointer hover:border-[#FF5733] transition-colors"
                   [class.border-[#FF5733]]="formData.plan_id === 1"
                   [class.bg-[#111111]]="formData.plan_id === 1"
                   (click)="selectPlan(1, 0)">
                <h3 class="font-bold text-lg mb-2">GRATUITO</h3>
                <div class="text-3xl font-extrabold mb-4">$0 <span class="text-xs text-zinc-500 font-normal">/mes</span></div>
                <ul class="space-y-2 text-xs text-zinc-400 mb-6 font-mono">
                  <li>- 1 Sucursal</li>
                  <li>- 3 Técnicos</li>
                </ul>
              </div>
              <!-- Pro -->
              <div class="border border-[#222222] bg-[#0a0a0a] p-6 cursor-pointer hover:border-[#FF5733] transition-colors relative"
                   [class.border-[#FF5733]]="formData.plan_id === 2"
                   [class.bg-[#111111]]="formData.plan_id === 2"
                   (click)="selectPlan(2, 49)">
                <div class="absolute top-0 right-0 bg-[#FF5733] text-white text-[8px] font-bold px-2 py-0.5 uppercase tracking-widest">PRO</div>
                <h3 class="font-bold text-lg mb-2">PROFESIONAL</h3>
                <div class="text-3xl font-extrabold mb-4">$49 <span class="text-xs text-zinc-500 font-normal">/mes</span></div>
                <ul class="space-y-2 text-xs text-zinc-400 mb-6 font-mono">
                  <li>- 3 Sucursales</li>
                  <li>- 15 Técnicos</li>
                  <li>- Reportes Avanzados</li>
                </ul>
              </div>
              <!-- Enterprise -->
              <div class="border border-[#222222] bg-[#0a0a0a] p-6 cursor-pointer hover:border-[#FF5733] transition-colors"
                   [class.border-[#FF5733]]="formData.plan_id === 3"
                   [class.bg-[#111111]]="formData.plan_id === 3"
                   (click)="selectPlan(3, 149)">
                <h3 class="font-bold text-lg mb-2">CORPORATIVO</h3>
                <div class="text-3xl font-extrabold mb-4">$149 <span class="text-xs text-zinc-500 font-normal">/mes</span></div>
                <ul class="space-y-2 text-xs text-zinc-400 mb-6 font-mono">
                  <li>- Sucursales Ilimitadas</li>
                  <li>- Técnicos Ilimitados</li>
                  <li>- API Access</li>
                </ul>
              </div>
            </div>
            <div class="mt-8 flex justify-end">
              <button [disabled]="!formData.plan_id" (click)="nextStep()" class="bg-[#FF5733] disabled:opacity-50 text-white px-8 py-3 text-[10px] uppercase font-bold tracking-[.2em] hover:bg-[#e04c2c]">CONTINUAR -></button>
            </div>
          </div>

          <!-- STEP 2: USUARIO -->
          <div *ngIf="step === 2" @slideAnimation class="w-full max-w-xl mx-auto">
            <h2 class="text-2xl font-extrabold uppercase mb-6 text-center">CREDENCIALES DE COMANDANTE</h2>
            <div class="space-y-4">
              <div class="flex gap-4">
                <app-input class="flex-1" label="Nombre" [(ngModel)]="formData.nombre" placeholder="Ej: Juan" icon="las la-user"></app-input>
                <app-input class="flex-1" label="Apellido" [(ngModel)]="formData.apellido" placeholder="Ej: Pérez" icon="las la-user"></app-input>
              </div>
              <app-input label="Correo Electrónico" type="email" [(ngModel)]="formData.correo" placeholder="admin@taller.com" icon="las la-envelope"></app-input>
              <div class="flex gap-4">
                <app-input class="flex-1" label="Contraseña" type="password" [(ngModel)]="formData.contrasena" placeholder="********" icon="las la-lock"></app-input>
                <app-input class="flex-1" label="Confirmar" type="password" [(ngModel)]="confirmPassword" placeholder="********" icon="las la-lock"></app-input>
              </div>
            </div>
            
            <div class="mt-8 flex justify-between">
              <button (click)="prevStep()" class="text-zinc-400 text-[10px] uppercase font-bold tracking-widest hover:text-white"><- VOLVER</button>
              <button [disabled]="!isStep2Valid()" (click)="nextStep()" class="bg-[#FF5733] disabled:opacity-50 text-white px-8 py-3 text-[10px] uppercase font-bold tracking-[.2em] hover:bg-[#e04c2c]">CONTINUAR -></button>
            </div>
          </div>

          <!-- STEP 3: UBICACIÓN -->
          <div *ngIf="step === 3" @slideAnimation class="w-full">
            <h2 class="text-2xl font-extrabold uppercase mb-6 text-center">CUARTEL GENERAL (TALLER)</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <p class="text-xs text-zinc-400 mb-4 font-mono">Selecciona el punto exacto de tus operaciones. Los técnicos se despacharán desde aquí.</p>
                <div class="border border-[#333333] h-[350px]">
                  <app-map-picker (locationSelected)="onLocationSelected($event)"></app-map-picker>
                </div>
              </div>
              <div class="flex flex-col justify-center space-y-6">
                <app-input label="Nombre del Taller" [(ngModel)]="formData.nombre_taller" placeholder="Ej: Motors Pro Center" icon="las la-tools"></app-input>
                
                <div class="bg-[#111111] border border-[#222222] p-4">
                  <span class="text-[9px] uppercase tracking-widest font-bold text-[#FF5733] mb-2 block">Ubicación Detectada</span>
                  <p class="text-sm text-zinc-300 min-h-[40px]">{{ formData.direccion_taller || 'Esperando coordenadas...' }}</p>
                  <div class="flex gap-4 mt-2 font-mono text-[10px] text-zinc-500">
                    <span>LAT: {{ formData.latitud_taller || '0.00' }}</span>
                    <span>LNG: {{ formData.longitud_taller || '0.00' }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-8 flex justify-between">
              <button (click)="prevStep()" class="text-zinc-400 text-[10px] uppercase font-bold tracking-widest hover:text-white"><- VOLVER</button>
              <button [disabled]="!isStep3Valid()" (click)="nextStep()" class="bg-[#FF5733] disabled:opacity-50 text-white px-8 py-3 text-[10px] uppercase font-bold tracking-[.2em] hover:bg-[#e04c2c]">CONTINUAR -></button>
            </div>
          </div>

          <!-- STEP 4: PAGO STRIPE -->
          <div *ngIf="step === 4" @slideAnimation class="w-full max-w-md mx-auto">
            <h2 class="text-2xl font-extrabold uppercase mb-6 text-center">AUTORIZACIÓN DE ENLACE</h2>
            
            <div *ngIf="isFreePlan" class="bg-[#111111] border border-[#222222] p-8 text-center mb-8">
              <lucide-icon name="check-circle" size="48" class="text-green-500 mx-auto mb-4"></lucide-icon>
              <h3 class="text-xl font-bold mb-2">PLAN GRATUITO</h3>
              <p class="text-sm text-zinc-400">No se requiere método de pago. Estás listo para operar.</p>
            </div>

            <div *ngIf="!isFreePlan" class="bg-[#111111] border border-[#222222] p-6 mb-8">
               <div class="flex justify-between items-center mb-6 border-b border-[#222222] pb-4">
                 <span class="text-xs uppercase font-bold text-zinc-400 tracking-widest">TOTAL A PAGAR</span>
                 <span class="text-2xl font-extrabold">$ {{ selectedPlanPrice }}<span class="text-xs text-zinc-500">/mes</span></span>
               </div>

               <div *ngIf="loadingStripe" class="flex flex-col items-center justify-center py-8 gap-4">
                 <lucide-icon name="loader-2" class="animate-spin text-[#FF5733]" size="32"></lucide-icon>
                 <span class="text-xs font-mono text-zinc-500">Conectando con pasarela segura...</span>
               </div>

               <!-- CONTENEDOR DE STRIPE ELEMENTS -->
               <div [class.hidden]="loadingStripe">
                 <div id="payment-element" class="mb-4"></div>
                 <div id="payment-message" class="text-red-500 text-xs mb-4"></div>
               </div>
            </div>

            <div class="error-panel text-center text-red-500 text-sm mb-4" *ngIf="errorMessage">{{ errorMessage }}</div>

            <div class="mt-4 flex flex-col gap-4">
              <button (click)="onSubmit()" [disabled]="loading" class="bg-[#FF5733] w-full disabled:opacity-50 text-white px-8 py-4 text-[12px] uppercase font-bold tracking-[.2em] hover:bg-[#e04c2c] flex items-center justify-center gap-2">
                <lucide-icon *ngIf="loading" name="loader-2" class="animate-spin" size="16"></lucide-icon>
                {{ loading ? 'INICIALIZANDO...' : 'FINALIZAR REGISTRO' }}
              </button>
              <button (click)="prevStep()" [disabled]="loading" class="text-zinc-400 text-[10px] uppercase font-bold tracking-widest hover:text-white text-center">CANCELAR Y VOLVER</button>
            </div>
          </div>

        </div>
      </div>
    </div>
  `
})
export class RegisterComponent implements OnInit {
  step = 1;
  
  formData = {
    nombre: '',
    apellido: '',
    correo: '',
    contrasena: '',
    nombre_taller: '',
    direccion_taller: '',
    latitud_taller: null as number | null,
    longitud_taller: null as number | null,
    plan_id: null as number | null
  };
  confirmPassword = '';
  
  selectedPlanPrice = 0;
  get isFreePlan(): boolean { return this.selectedPlanPrice === 0; }

  loading = false;
  loadingStripe = false;
  errorMessage = '';

  stripe: Stripe | null = null;
  elements: StripeElements | null = null;

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private stripeService: StripeService,
    private router: Router
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if(params['plan']) {
        const pId = parseInt(params['plan'], 10);
        if([1,2,3].includes(pId)) {
          this.selectPlan(pId, pId === 1 ? 0 : (pId === 2 ? 49 : 149));
        }
      }
    });
  }

  getStepName(s: number): string {
    return ['PLAN', 'COMANDANTE', 'UBICACIÓN', 'ENLACE'][s - 1];
  }

  selectPlan(id: number, price: number) {
    this.formData.plan_id = id;
    this.selectedPlanPrice = price;
  }

  nextStep() {
    if(this.step < 4) {
      this.step++;
      if(this.step === 4) {
        this.initStripe();
      }
    }
  }

  prevStep() {
    if(this.step > 1) {
      this.step--;
    }
  }

  isStep2Valid(): boolean {
    return !!(this.formData.nombre && this.formData.apellido && 
             this.formData.correo && this.formData.contrasena && 
             this.formData.contrasena === this.confirmPassword);
  }

  isStep3Valid(): boolean {
    return !!(this.formData.nombre_taller && this.formData.direccion_taller);
  }

  onLocationSelected(loc: {lat: number, lng: number, address: string}) {
    this.formData.latitud_taller = loc.lat;
    this.formData.longitud_taller = loc.lng;
    this.formData.direccion_taller = loc.address;
  }

  async initStripe() {
    if (this.isFreePlan) return;
    
    this.loadingStripe = true;
    this.errorMessage = '';

    try {
      this.stripe = await this.stripeService.getStripe();
      if (!this.stripe) throw new Error("Stripe falló al inicializar.");

      this.stripeService.createPaymentIntent(this.formData.plan_id!).subscribe({
        next: (res) => {
          if (res.clientSecret) {
            const appearance = { theme: 'night' as const };
            this.elements = this.stripe!.elements({ clientSecret: res.clientSecret, appearance });
            const paymentElement = this.elements.create('payment');
            paymentElement.mount('#payment-element');
          }
          this.loadingStripe = false;
        },
        error: (err) => {
          this.errorMessage = "Error al obtener pasarela de pago: " + (err.error?.detail || err.message);
          this.loadingStripe = false;
        }
      });
    } catch (e: any) {
      this.errorMessage = e.message;
      this.loadingStripe = false;
    }
  }

  async onSubmit() {
    this.errorMessage = '';
    this.loading = true;

    if (!this.isFreePlan && this.stripe && this.elements) {
      // Confirm payment with Stripe Elements
      const { error } = await this.stripe.confirmPayment({
        elements: this.elements,
        redirect: 'if_required' // We will handle success manually
      });

      if (error) {
        this.errorMessage = error.message || 'Error al procesar pago.';
        this.loading = false;
        return;
      }
    }

    // Payment success or Free Plan -> Register Backend
    this.api.post<any>('/auth/register', this.formData).subscribe({
      next: (res) => {
        this.loading = false;
        // Success -> redirect
        this.router.navigate(['/auth/login'], { queryParams: { registered: true, email: this.formData.correo } });
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.detail || 'Error al crear la cuenta en el sistema.';
      }
    });
  }
}
