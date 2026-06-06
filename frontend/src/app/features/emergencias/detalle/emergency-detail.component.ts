import { Component, OnInit, AfterViewInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ApiService } from '../../../core/api/api.service';
import { toast } from 'ngx-sonner';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../../environments/environment';
import { SocketService } from '../../../core/services/socket.service';
import { Subscription } from 'rxjs';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import * as L from 'leaflet';
import { 
  LucideAngularModule, 
  Home, Menu, User, Settings, AlertTriangle, Hammer, Users, 
  History, ClipboardList, LogOut, ArrowLeft, Clock, MapPin, 
  Wrench, ShieldAlert, Send, Sun, Moon, ChevronsLeft, ChevronsRight,
  LayoutDashboard, Briefcase, Factory, Eye, Globe, Plus, Bell,
  ArrowRight, Camera, Mail, KeyRound, Loader2, CheckSquare, Check, Image as ImageIcon, Tag, X, Radio, Video, Info, MessageSquare,
  TrendingUp, DollarSign, FileText, Calendar, Calculator
} from 'lucide-angular';

import { ConfigService } from '../../../core/config/config.service';
import { ReportesService, HistorialVehicularItem } from '../../../core/services/reportes.service';

@Component({
  selector: 'app-emergency-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule, FormsModule],
  template: `
    <div class="min-h-full flex flex-col bg-[#050505] text-white animate-in fade-in duration-500 pb-20 font-sans">
      
      <!-- TOP NAVIGATION BAR -->
      <div class="h-20 bg-[#050505] border-b border-zinc-900 px-8 flex items-center justify-between sticky top-0 z-50 backdrop-blur-xl bg-opacity-80">
        <div class="flex items-center gap-6">
          <button (click)="goBack()" class="w-10 h-10 border border-zinc-800 flex items-center justify-center hover:bg-zinc-900 transition-all group">
            <lucide-icon name="arrow-left" class="text-zinc-600 group-hover:text-white" size="16"></lucide-icon>
          </button>
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-lg font-bold tracking-tight uppercase">{{ emergency?.descripcion }}</h1>
              <span class="px-2 py-0.5 font-mono text-[8px] font-bold uppercase tracking-[.2em] border border-primary text-primary">
                {{ emergency?.estado_actual }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex gap-4">
            <button *ngIf="!emergency?.idTaller && emergency?.estado_actual !== 'CANCELADO'"
                    (click)="openAssignModal()"
                    class="bg-red-600 text-white px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all hover:bg-red-500 shadow-[0_0_20px_rgba(220,38,38,0.4)] flex items-center gap-2">
              <lucide-icon name="shield-alert" size="14"></lucide-icon>
              Asignar Misión
            </button>
            <button *ngIf="emergency?.idTaller === currentWorkshop && emergency?.estado_actual !== 'CANCELADO' && emergency?.estado_actual !== 'FINALIZADA'"
                   (click)="openChat()"
                   class="border border-blue-700 text-blue-400 hover:bg-blue-900/20 px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all flex items-center gap-2">
              <lucide-icon name="message-square" size="14"></lucide-icon>
              Chat Directo
            </button>
            <button *ngIf="emergency?.idTaller === currentWorkshop && emergency?.estado_actual !== 'CANCELADO'"
                    (click)="openFichaModal()"
                    class="border border-zinc-700 text-zinc-300 hover:text-primary hover:border-primary px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all">
              Editar Ficha
            </button>
            <button *ngIf="emergency?.idTaller === currentWorkshop && (emergency?.estado_actual === 'ASIGNADO' || emergency?.estado_actual === 'EN_PROCESO')"
                    (click)="showPagoModal = true"
                    class="bg-emerald-600 text-white px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all hover:bg-emerald-500 shadow-lg">
              Finalizar
            </button>
            <button *ngIf="emergency?.idTaller === currentWorkshop && emergency?.estado_actual !== 'FINALIZADA' && emergency?.estado_actual !== 'CANCELADO'"
                    (click)="openCotizacionModal()"
                    class="bg-orange-600 text-white px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all hover:bg-orange-500 flex items-center gap-2">
              <lucide-icon name="calculator" size="14"></lucide-icon>
              Cotizar
            </button>

            <button *ngIf="(emergency?.estado_actual === 'ATENDIDO' || emergency?.estado_actual === 'FINALIZADA') && emergency?.pago"
                    (click)="downloadFactura()"
                    class="bg-blue-600 text-white px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all hover:bg-blue-500 flex items-center gap-2">
              <lucide-icon name="arrow-down-to-line" size="14"></lucide-icon>
              Factura PDF
            </button>
        </div>
      </div>

      <!-- LOADING STATE -->
      <div *ngIf="loading" class="flex-1 flex flex-col items-center justify-center gap-6 py-40">
        <div class="w-16 h-16 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p class="font-mono text-[10px] uppercase tracking-[.4em] text-zinc-600">Sincronizando Telemetría...</p>
      </div>

      <ng-container *ngIf="!loading && emergency">
         <!-- MAP SECTION -->
         <div class="relative w-full h-[400px] border-b border-zinc-900 overflow-hidden">
            <div id="emergency-map" class="absolute inset-0 z-0 bg-black"></div>
            <div class="absolute inset-x-0 bottom-0 p-8 flex justify-between items-end z-10 pointer-events-none">
               <div class="bg-black/80 backdrop-blur-md border border-zinc-800 p-6 pointer-events-auto flex items-center gap-6">
                  <div>
                    <div class="flex items-center gap-3 mb-2">
                      <lucide-icon name="map-pin" class="text-primary" size="14"></lucide-icon>
                      <span class="font-bold text-[10px] uppercase tracking-widest text-white">{{ emergency.direccion }}</span>
                    </div>
                  </div>
                  
                  <div class="border-l border-zinc-800 pl-6 flex gap-6" *ngIf="telemetry.distance">
                     <div>
                        <div class="text-[8px] uppercase tracking-[.2em] text-zinc-500 mb-1">Distancia</div>
                        <div class="font-mono text-sm text-primary">{{ telemetry.distance }} km</div>
                     </div>
                     <div>
                        <div class="text-[8px] uppercase tracking-[.2em] text-zinc-500 mb-1">ETA</div>
                        <div class="font-mono text-sm text-primary">{{ telemetry.eta || telemetry.duration + ' min' }}</div>
                     </div>
                  </div>
               </div>
            </div>
         </div>

        <!-- CONTENT -->
        <div class="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-px bg-zinc-900">
          <div class="lg:col-span-8 bg-[#050505] p-10 lg:p-14 space-y-12">
            <div class="space-y-4">
               <h2 class="text-2xl font-light italic text-zinc-200">"{{ emergency.resumen_ia?.resumen }}"</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 pt-8 border-t border-zinc-900">
              <div class="space-y-4">
                <h3 class="font-bold text-[9px] uppercase tracking-widest text-primary">Diagnóstico Probable</h3>
                <p class="text-xs text-zinc-400 font-mono">{{ getFichaField('diagnostico_probable')[0] }}</p>
              </div>
              <div class="space-y-4">
                <h3 class="font-bold text-[9px] uppercase tracking-widest text-zinc-400">Piezas Necesarias</h3>
                <p class="text-xs text-zinc-400 font-mono">{{ getFichaField('piezas_necesarias').join(', ') }}</p>
              </div>
            </div>
          </div>
          <div class="lg:col-span-4 bg-[#080808] p-10 space-y-10">
               <section class="space-y-4">
                 <h3 class="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Vehículo</h3>
                 <div class="bg-zinc-950 border border-zinc-900 p-6">
                    <div class="text-sm font-bold">{{ emergency.vehiculo?.marca }} {{ emergency.vehiculo?.modelo }}</div>
                    <div class="text-[10px] font-mono text-zinc-500 mt-1">{{ emergency.vehiculo?.placa }}</div>
                 </div>
              </section>

              <!-- Historial Vehicular -->
              <section class="space-y-4">
                 <h3 class="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Historial del Vehículo</h3>
                 <div *ngIf="loadingHistorial" class="flex justify-center py-4">
                   <lucide-icon name="loader-2" class="animate-spin text-primary" size="16"></lucide-icon>
                 </div>
                 <div *ngIf="!loadingHistorial && historialVehicular.length === 0" class="bg-zinc-950 border border-zinc-900 p-4 text-center">
                   <p class="text-[9px] font-mono text-zinc-500 uppercase">Sin atenciones previas.</p>
                 </div>
                 <div *ngIf="!loadingHistorial && historialVehicular.length > 0" class="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                   <div *ngFor="let hist of historialVehicular" class="bg-zinc-950 border border-zinc-900 p-4 hover:border-primary transition-colors cursor-default">
                     <div class="flex justify-between items-start mb-2">
                       <span class="text-[10px] font-bold uppercase tracking-wider text-white">Emg #{{ hist.id_emergencia }}</span>
                       <span class="text-[8px] font-mono text-zinc-500">{{ hist.fecha | date:'shortDate' }}</span>
                     </div>
                     <p class="text-[10px] text-zinc-400 font-mono line-clamp-2 leading-relaxed mb-2">{{ hist.diagnostico_final || hist.diagnostico_inicial }}</p>
                     <div class="mt-2 flex justify-between items-center border-t border-zinc-900 pt-2">
                        <span class="text-[8px] font-bold px-2 py-0.5 border border-emerald-900/50 bg-emerald-900/20 text-emerald-500 uppercase">{{ hist.estado_final }}</span>
                        <span class="text-[10px] font-mono font-bold text-white">{{ hist.monto_total ? (hist.monto_total | currency:'USD') : '-' }}</span>
                     </div>
                   </div>
                 </div>
              </section>

              <!-- Seccion Cotizaciones -->
              <section class="space-y-4" *ngIf="cotizaciones.length > 0">
                 <h3 class="text-[9px] font-bold uppercase tracking-widest text-orange-500">Cotizaciones Emitidas</h3>
                 <div class="space-y-3">
                   <div *ngFor="let cot of cotizaciones" class="bg-zinc-950 border border-orange-900/50 p-4 relative">
                     <div class="flex justify-between items-start mb-2">
                       <span class="text-[10px] font-bold uppercase tracking-wider text-white">#{{ cot.id }}</span>
                       <span class="text-[8px] px-2 py-0.5 border uppercase font-bold"
                             [ngClass]="{'border-yellow-500 text-yellow-500': cot.estado === 'PENDIENTE', 'border-emerald-500 text-emerald-500': cot.estado === 'ACEPTADA', 'border-red-500 text-red-500': cot.estado === 'RECHAZADA'}">
                         {{ cot.estado }}
                       </span>
                     </div>
                     <p class="text-[11px] text-zinc-400 mb-2">{{ cot.descripcion_servicio }}</p>
                     <div class="text-xs font-mono text-orange-400 font-bold flex justify-between">
                       <span>Total:</span>
                       <span>$ {{ (cot.costo_mano_obra + cot.costo_repuestos) | number:'1.2-2' }}</span>
                     </div>
                     <div *ngIf="cot.estado === 'PENDIENTE' && !emergency.idTaller" class="mt-4 pt-3 border-t border-zinc-900 flex justify-end">
                       <button (click)="aceptarCotizacion(cot.id)" class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 text-[9px] font-bold uppercase tracking-widest transition-colors">
                         Aceptar Cotización
                       </button>
                     </div>
                   </div>
                 </div>
              </section>
           </div>

        </div>
      </ng-container>

      <!-- MODALS -->
      <div *ngIf="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
         <div class="bg-zinc-950 border border-zinc-800 w-full max-w-xl">
            <div class="p-6 border-b border-zinc-900 flex justify-between items-center">
               <h2 class="font-bold text-xs uppercase tracking-widest">Asignación</h2>
               <button (click)="showModal = false"><lucide-icon name="x" size="18"></lucide-icon></button>
            </div>
            <div class="p-8 space-y-8">
               <div class="space-y-2">
                 <h3 class="text-[10px] font-bold uppercase tracking-[.3em] text-zinc-500">Seleccionar Personal Operativo</h3>
                 <p class="text-[11px] text-zinc-400 font-mono italic">Seleccione uno o más técnicos para esta intervención.</p>
               </div>

               <div *ngIf="loadingTechs" class="py-12 flex justify-center">
                  <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
               </div>

               <div *ngIf="!loadingTechs" class="grid grid-cols-1 gap-3 max-h-[40vh] overflow-y-auto pr-2 custom-scrollbar">
                  <div *ngFor="let tech of availableTechs" 
                       (click)="toggleTech(tech.id)"
                       [class]="selectedTechs.includes(tech.id) ? 'border-primary bg-primary/10' : 'border-zinc-800 bg-zinc-900/30'"
                       class="p-4 border cursor-pointer transition-all hover:bg-zinc-900 flex justify-between items-center group">
                    <div>
                      <div class="text-xs font-bold uppercase tracking-tight" [class.text-primary]="selectedTechs.includes(tech.id)">{{ tech.nombre }}</div>
                      <div class="flex gap-2 mt-1">
                        <span *ngFor="let esp of tech.especialidades" class="text-[8px] uppercase tracking-tighter text-zinc-500">
                          #{{ esp.nombre }}
                        </span>
                      </div>
                    </div>
                    <div class="w-5 h-5 border flex items-center justify-center transition-colors"
                         [class]="selectedTechs.includes(tech.id) ? 'bg-primary border-primary' : 'border-zinc-700'">
                       <lucide-icon *ngIf="selectedTechs.includes(tech.id)" name="check" size="12" class="text-black"></lucide-icon>
                    </div>
                  </div>
               </div>

               <div class="pt-6 border-t border-zinc-900 flex flex-col gap-4">
                  <div class="flex justify-between items-center text-[10px] font-mono">
                     <span class="text-zinc-500 uppercase">Técnicos Seleccionados</span>
                     <span class="text-white font-bold">{{ selectedTechs.length }}</span>
                  </div>
                  <button (click)="confirmAssignment()" 
                          [disabled]="selectedTechs.length === 0"
                          class="w-full bg-primary disabled:bg-zinc-800 disabled:text-zinc-600 text-black py-4 font-bold text-[10px] uppercase tracking-[.3em] transition-all hover:bg-white active:scale-[0.98]">
                    Confirmar Misión
                  </button>
               </div>
            </div>
         </div>
      </div>

      <div *ngIf="showPagoModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm overflow-y-auto">
         <div class="bg-zinc-950 border border-emerald-900 w-full max-w-2xl my-8">
            <div class="p-6 border-b border-zinc-900 flex justify-between items-center">
               <h2 class="font-bold text-xs uppercase tracking-widest text-emerald-400">Generar Factura y Finalizar</h2>
               <button (click)="showPagoModal = false"><lucide-icon name="x" size="18"></lucide-icon></button>
            </div>
            <div class="p-6 space-y-6">
               <!-- Header -->
               <div class="flex justify-between items-end border-b border-zinc-900 pb-4">
                  <div class="text-[11px] text-zinc-400">Items de Facturación</div>
                  <button (click)="addFacturaItem()" class="px-4 py-2 bg-zinc-900 hover:bg-zinc-800 text-white text-[10px] uppercase tracking-widest font-bold">
                    + Añadir Ítem
                  </button>
               </div>
               
               <!-- Items List -->
               <div class="space-y-3 max-h-[40vh] overflow-y-auto pr-2">
                 <div *ngFor="let item of facturaItems; let i = index" class="flex gap-2 items-center p-3 border border-zinc-900 bg-black/50">
                   <div class="flex-1 space-y-2">
                     <input [(ngModel)]="item.descripcion" placeholder="Descripción (Ej. Cambio Aceite)" class="w-full bg-transparent border-b border-zinc-800 p-2 text-sm outline-none focus:border-emerald-500">
                     <div class="flex gap-2">
                       <select [(ngModel)]="item.tipo" class="bg-zinc-900 border border-zinc-800 p-2 text-xs outline-none text-white w-1/3">
                         <option value="servicio">Servicio</option>
                         <option value="repuesto">Repuesto</option>
                       </select>
                       <input [(ngModel)]="item.cantidad" (ngModelChange)="calcItemTotal(item)" type="number" min="1" placeholder="Cant." class="w-1/4 bg-zinc-900 border border-zinc-800 p-2 text-xs outline-none text-center">
                       <input [(ngModel)]="item.precio_unitario" (ngModelChange)="calcItemTotal(item)" type="number" min="0" placeholder="Precio Un." class="w-1/3 bg-zinc-900 border border-zinc-800 p-2 text-xs outline-none text-right">
                     </div>
                   </div>
                   <div class="w-24 text-right font-mono text-emerald-400 font-bold p-2">
                     $ {{ item.total | number:'1.2-2' }}
                   </div>
                   <button (click)="removeFacturaItem(i)" class="p-2 text-zinc-500 hover:text-red-500 transition-colors">
                     <lucide-icon name="trash-2" size="16"></lucide-icon>
                   </button>
                 </div>
               </div>

               <!-- Totals -->
               <div class="bg-black border border-zinc-900 p-4 space-y-2 font-mono text-xs">
                 <div class="flex justify-between text-zinc-400">
                   <span>Subtotal:</span>
                   <span>$ {{ facturaSubtotal | number:'1.2-2' }}</span>
                 </div>
                 <div class="flex justify-between text-zinc-400">
                   <span>Impuestos (Opcional):</span>
                   <input [(ngModel)]="facturaImpuestos" (ngModelChange)="calcFacturaTotal()" type="number" class="w-24 bg-transparent border-b border-zinc-800 text-right outline-none">
                 </div>
                 <div class="flex justify-between font-bold text-emerald-400 text-lg border-t border-zinc-900 pt-2 mt-2">
                   <span>Total General:</span>
                   <span>$ {{ facturaTotalGeneral | number:'1.2-2' }}</span>
                 </div>
               </div>
               
               <button (click)="registrarPago()" [disabled]="facturaItems.length === 0" class="w-full bg-emerald-700 disabled:bg-zinc-800 disabled:text-zinc-500 py-4 font-bold text-[10px] uppercase tracking-widest transition-colors hover:bg-emerald-600">Emitir Factura y Finalizar</button>
            </div>
         </div>
      </div>

      <div *ngIf="showChatModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
         <div class="bg-zinc-950 border border-zinc-800 w-full max-w-lg h-[70vh] flex flex-col">
            <div class="p-4 border-b border-zinc-900 flex justify-between items-center bg-zinc-900/50">
               <h2 class="font-bold text-[10px] uppercase tracking-widest">Chat Operativo</h2>
               <button (click)="closeChat()"><lucide-icon name="x" size="18"></lucide-icon></button>
            </div>
            <div #chatContainer class="flex-1 overflow-y-auto p-6 space-y-4">
               <div *ngFor="let msg of chatMessages" class="flex flex-col" [ngClass]="msg.rol_remitente === 'cliente' ? 'items-start' : 'items-end'">
                  <div class="max-w-[85%] p-3 border text-[11px] rounded-lg shadow-sm" [ngClass]="msg.rol_remitente === 'cliente' ? 'bg-zinc-900 border-zinc-800' : 'bg-blue-900/20 border-blue-800/50'">
                     <img *ngIf="msg.imagen_url" [src]="getImageUrl(msg.imagen_url)" class="w-full rounded mb-2 cursor-pointer hover:opacity-90 transition-opacity" (click)="fullScreenImage = msg.imagen_url">
                     <audio *ngIf="msg.audio_url" controls [src]="getImageUrl(msg.audio_url)" class="w-[240px] h-[40px] mt-1 bg-zinc-100 rounded-full"></audio>
                     <p *ngIf="msg.contenido" class="mt-1 text-[13px]">{{ msg.contenido }}</p>
                  </div>
               </div>
            </div>
            <div class="p-3 bg-zinc-900/30 border-t border-zinc-900 flex gap-2 items-center">
               <button (click)="fileInput.click()" class="text-zinc-400 hover:text-white p-2 transition-colors" title="Subir archivo">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
               </button>
               <input type="file" #fileInput (change)="onChatFileSelected($event)" class="hidden" accept="image/*,audio/*">
               
               <input [(ngModel)]="newChatMessage" (keyup.enter)="sendChatMessage()" placeholder="Escribe..." class="flex-1 bg-black border border-zinc-800 p-3 text-[11px] outline-none">
               
               <button (pointerdown)="onMicPointerDown($event)" (pointerup)="onMicPointerUp($event)" (pointerleave)="onMicPointerUp($event)"
                       [ngClass]="isRecording ? 'text-red-500 animate-pulse' : 'text-zinc-400 hover:text-white'" 
                       class="p-2 transition-colors cursor-pointer" title="Grabar (Clic o Mantener)">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
               </button>
               
               <button (click)="sendChatMessage()" class="bg-blue-600 p-3 text-white flex items-center justify-center hover:bg-blue-500 transition-colors">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
               </button>
            </div>
         </div>
      </div>

      <!-- Modal Pantalla Completa Imagen (Chat) -->
      <div *ngIf="fullScreenImage" class="fixed inset-0 z-[200] flex items-center justify-center bg-black/95 p-4 backdrop-blur-md" (click)="fullScreenImage = null">
         <button class="absolute top-6 right-6 text-zinc-400 hover:text-white transition-colors bg-zinc-900/50 rounded-full p-2" (click)="fullScreenImage = null">
            <lucide-icon name="x" size="24"></lucide-icon>
         </button>
         <img [src]="getImageUrl(fullScreenImage)" class="max-w-full max-h-[90vh] object-contain rounded-md" (click)="$event.stopPropagation()">
      </div>

      <div *ngIf="showFichaModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
         <div class="bg-zinc-950 border border-zinc-800 w-full max-w-xl">
            <div class="p-6 border-b border-zinc-900 flex justify-between items-center">
               <h2 class="font-bold text-xs uppercase tracking-widest">Ficha Técnica</h2>
               <button (click)="showFichaModal = false"><lucide-icon name="x" size="18"></lucide-icon></button>
            </div>
            <div class="p-6 space-y-4">
               <textarea [(ngModel)]="fichaEdit.resumen" rows="3" class="w-full bg-black border border-zinc-800 p-3 text-[11px]"></textarea>
               <button (click)="saveFicha()" class="w-full bg-primary py-4 font-bold text-[10px] uppercase">Guardar</button>
            </div>
         </div>
      </div>

      <!-- Modal Cotizacion -->
      <div *ngIf="showCotizacionModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm overflow-y-auto">
         <div class="bg-zinc-950 border border-orange-900 w-full max-w-xl my-8">
            <div class="p-6 border-b border-zinc-900 flex justify-between items-center">
               <h2 class="font-bold text-xs uppercase tracking-widest text-orange-500">Generar Cotización</h2>
               <button (click)="showCotizacionModal = false"><lucide-icon name="x" size="18"></lucide-icon></button>
            </div>
            <div class="p-6 space-y-4">
               <div>
                  <label class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1 block">Descripción del Servicio</label>
                  <textarea [(ngModel)]="newCotizacion.descripcion_servicio" rows="3" class="w-full bg-black border border-zinc-800 p-3 text-[12px] text-white outline-none focus:border-orange-500"></textarea>
               </div>
               <div class="grid grid-cols-2 gap-4">
                 <div>
                    <label class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1 block">Mano de Obra ($)</label>
                    <input type="number" [(ngModel)]="newCotizacion.costo_mano_obra" class="w-full bg-black border border-zinc-800 p-3 text-[12px] text-white outline-none focus:border-orange-500">
                 </div>
                 <div>
                    <label class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1 block">Repuestos ($)</label>
                    <input type="number" [(ngModel)]="newCotizacion.costo_repuestos" class="w-full bg-black border border-zinc-800 p-3 text-[12px] text-white outline-none focus:border-orange-500">
                 </div>
               </div>
               <div class="grid grid-cols-2 gap-4">
                 <div>
                    <label class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1 block">Tiempo Est. (Horas)</label>
                    <input type="number" [(ngModel)]="newCotizacion.tiempo_estimado_horas" class="w-full bg-black border border-zinc-800 p-3 text-[12px] text-white outline-none focus:border-orange-500">
                 </div>
               </div>
               <div>
                  <label class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1 block">Condiciones / Notas (Opcional)</label>
                  <textarea [(ngModel)]="newCotizacion.condiciones" rows="2" class="w-full bg-black border border-zinc-800 p-3 text-[12px] text-white outline-none focus:border-orange-500"></textarea>
               </div>
               
               <div class="pt-4 border-t border-zinc-900 mt-6 flex flex-col gap-4">
                  <div class="flex justify-between items-center text-[11px] font-mono font-bold text-orange-400">
                     <span>TOTAL ESTIMADO:</span>
                     <span class="text-lg">$ {{ (newCotizacion.costo_mano_obra + newCotizacion.costo_repuestos) | number:'1.2-2' }}</span>
                  </div>
                  <button (click)="enviarCotizacion()" class="w-full bg-orange-700 py-4 font-bold text-[10px] uppercase tracking-widest transition-colors hover:bg-orange-600 text-white">
                    Enviar al Cliente
                  </button>
               </div>
            </div>
         </div>
      </div>

    </div>

  `,
  styles: [`
    #emergency-map { height: 100%; width: 100%; transition: opacity 0.5s; background: #000; }
    .leaflet-container { background: #000 !important; }
    .leaflet-tile-pane { filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%); }
    .leaflet-routing-container { display: none !important; }
  `]
})
export class EmergencyDetailComponent implements OnInit, OnDestroy {
  emergency: any = null;
  loading = true;
  showModal = false;
  availableTechs: any[] = [];
  selectedTechs: number[] = [];
  loadingTechs = false;
  currentWorkshop = localStorage.getItem('cod_taller') || 'TALLER_01';
  
  // Workshop Coords (Dynamic)
  private workshopCoords: [number, number] = [-16.5, -68.15];
  private techCoords: [number, number] | null = null;
  
  telemetry = {
    distance: '',
    duration: '',
    eta: ''
  };

  historialVehicular: HistorialVehicularItem[] = [];
  loadingHistorial = false;

  // CU05 — Pago
  showPagoModal = false;
  pagoMonto: number | null = null;
  pagoExistente: any = null;

  // CU10 — Ficha técnica editable
  showFichaModal = false;
  fichaEdit = {
    resumen: '',
    ficha_tecnica: {
      diagnostico_probable: '',
      piezas_necesarias: '',
      repuestos_sugeridos: '',
      acciones_inmediatas: ''
    }
  };

  private map: L.Map | null = null;
  private routeLayer: L.GeoJSON | null = null;
  private emgMarker: L.Marker | null = null;
  private dynamicMarker: L.Marker | null = null;

  // Cotizaciones
  cotizaciones: any[] = [];
  showCotizacionModal = false;
  newCotizacion = {
    descripcion_servicio: '',
    costo_mano_obra: 0,
    costo_repuestos: 0,
    tiempo_estimado_horas: 1,
    condiciones: ''
  };

  // Chat logic
  showChatModal = false;
  chatMessages: any[] = [];
  newChatMessage = '';
  chatFile: File | null = null;
  fullScreenImage: string | null = null;

  private socketSub?: Subscription;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService,
    private socketService: SocketService,
    private sanitizer: DomSanitizer,
    private configService: ConfigService,
    private reportesService: ReportesService
  ) {}

  ngOnInit() {
    this.loadDetail();
    this.initSocket();
  }

  private initSocket() {
    const workshopId = localStorage.getItem('cod_taller') || 'anonymous';
    this.socketService.connect(workshopId);

    if (this.socketSub) this.socketSub.unsubscribe();
    this.socketSub = this.socketService.getMessages().subscribe(msg => {
      // Chat message
      if (msg.type === 'chat_message' && msg.idEmergencia == this.emergency?.id) {
        const exists = this.chatMessages.some(m => m.id === msg.id);
        if (!exists) {
          this.chatMessages.push(msg);
          this.scrollToBottom();
          if (!this.showChatModal) {
            toast.info('Nuevo mensaje del cliente');
          }
        }
      }
      
      // GPS Update (Tracking del técnico)
      if (msg.type === 'gps_update' && this.emergency?.estado_actual === 'EN_CAMINO') {
        const lat = parseFloat(msg.lat);
        const lng = parseFloat(msg.lng);
        if (!isNaN(lat) && !isNaN(lng)) {
          this.techCoords = [lat, lng];
          this.telemetry.eta = msg.eta;
          this.telemetry.distance = msg.distance_km ? msg.distance_km.toString() : this.telemetry.distance;
          
          this.updateMapMarker();
          this.calculateRoute(); // Recalcular ruta desde técnico
        }
      }
      
      // Status Update
      if (msg.type === 'status_update') {
         toast.info(`El estado ha cambiado a: ${msg.estado}`);
         this.loadDetail();
      }
    });
  }

  private scrollToBottom() {
    setTimeout(() => {
      const container = document.querySelector('.overflow-y-auto');
      if (container) container.scrollTop = container.scrollHeight;
    }, 100);
  }

  ngOnDestroy() {
    if (this.socketSub) this.socketSub.unsubscribe();
    if (this.map) this.map.remove();
  }

  loadDetail() {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) return;
    
    this.loading = true;
    this.emergency = null;
    this.pagoExistente = null;
    
    // 1. Cargar detalle de emergencia
    this.api.get<any>(`/gestion-emergencia/${id}`).subscribe({
      next: (res) => {
        this.emergency = res;
        this.cargarPago(); // CU05 — Cargar pago si ya existe
        this.cargarCotizaciones();
        this.cargarHistorialVehicular();
        
        // 2. Cargar coordenadas del taller para el HUD/Mapa
        this.api.get<any>(`/talleres/${this.currentWorkshop}`).subscribe({
           next: (tlr) => {
              if (tlr.latitud && tlr.longitud) {
                this.workshopCoords = [tlr.latitud, tlr.longitud];
              }
              this.loading = false;
              setTimeout(() => {
                this.initMap();
                this.calculateRoute();
              }, 300);
           },
           error: () => {
              // Si falla usamos default, pero no bloqueamos la vista
              this.loading = false;
              setTimeout(() => { this.initMap(); this.calculateRoute(); }, 300);
           }
        });
      },
      error: () => {
        this.loading = false;
        toast.error('Error al sincronizar con el satélite');
      }
    });
  }

  private initMap() {
    if (!this.emergency || !this.emergency.latitud) return;

    if (this.map) this.map.remove();

    try {
      this.map = L.map('emergency-map', {
        zoomControl: false,
        attributionControl: false
      }).setView([this.emergency.latitud, this.emergency.longitud], 13);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd',
        maxZoom: 20
      }).addTo(this.map);

      // Emergency Icon
      const emgIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #FF5733; width: 14px; height: 14px; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 20px #FF5733;"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });

      // Workshop Icon
      const tlrIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #3b82f6; width: 14px; height: 14px; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 20px #3b82f6;"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });

      // Technician Icon
      const techIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #10b981; width: 14px; height: 14px; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 20px #10b981;"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });

      this.emgMarker = L.marker([this.emergency.latitud, this.emergency.longitud], { icon: emgIcon }).addTo(this.map);
      
      // Mostrar Taller o Técnico según estado
      if (this.emergency.estado_actual === 'EN_CAMINO' && this.techCoords) {
         this.dynamicMarker = L.marker(this.techCoords, { icon: techIcon }).addTo(this.map);
         const bounds = L.latLngBounds([this.techCoords, [this.emergency.latitud, this.emergency.longitud]]);
         this.map.fitBounds(bounds, { padding: [100, 100] });
      } else {
         this.dynamicMarker = L.marker(this.workshopCoords, { icon: tlrIcon }).addTo(this.map);
         const bounds = L.latLngBounds([this.workshopCoords, [this.emergency.latitud, this.emergency.longitud]]);
         this.map.fitBounds(bounds, { padding: [100, 100] });
      }

    } catch (e) {
      console.error("Map initialization failed", e);
    }
  }

  private updateMapMarker() {
      if (!this.map || !this.dynamicMarker || !this.techCoords) return;
      this.dynamicMarker.setLatLng(this.techCoords);
  }

  private calculateRoute() {
    if (!this.emergency || !this.map) return;

    let start = `${this.workshopCoords[1]},${this.workshopCoords[0]}`;
    if (this.emergency.estado_actual === 'EN_CAMINO' && this.techCoords) {
      start = `${this.techCoords[1]},${this.techCoords[0]}`;
    }

    const end = `${this.emergency.longitud},${this.emergency.latitud}`;
    const url = `https://router.project-osrm.org/route/v1/driving/${start};${end}?overview=full&geometries=geojson`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.code === 'Ok' && data.routes.length > 0 && this.map) {
          const route = data.routes[0];
          
          // Draw Route
          if (this.routeLayer) this.map.removeLayer(this.routeLayer);
          this.routeLayer = L.geoJSON(route.geometry, {
            style: { color: '#FF5733', weight: 4, opacity: 0.8 }
          }).addTo(this.map);

          // Update Telemetry
          this.telemetry.distance = (route.distance / 1000).toFixed(1);
          this.telemetry.duration = Math.ceil(route.duration / 60).toString();
        }
      })
      .catch(err => console.error("OSRM Route failure", err));
  }

  getFichaField(key: string): string[] {
    const field = this.emergency?.resumen_ia?.ficha_tecnica?.[key];
    if (Array.isArray(field)) return field;
    if (typeof field === 'string') return [field];
    return ['SIN_DATA_DETECTED'];
  }

  getImageUrl(path: string): SafeUrl | string {
    if (!path) return '';
    let finalUrl = path;
    
    if (!path.startsWith('http')) {
      const cleanPath = path.startsWith('uploads/') ? path : `uploads/${path}`;
      const serverUrl = this.configService.apiUrl.replace('/api/v1', '');
      const base = serverUrl.endsWith('/') ? serverUrl.slice(0, -1) : serverUrl;
      finalUrl = `${base}/${cleanPath}`;
    }
    
    return this.sanitizer.bypassSecurityTrustUrl(finalUrl);
  }

  openAssignModal() {
    if (!this.emergency.is_locked) {
      this.api.post(`/gestion-emergencia/${this.emergency.id}/analizar`, {}).subscribe({
        next: () => { this.loadTechs(); this.showModal = true; },
        error: () => toast.error('Fallo en el protocolo de bloqueo')
      });
    } else {
      this.loadTechs();
      this.showModal = true;
    }
  }

  loadTechs() {
    this.loadingTechs = true;
    this.api.get<any[]>(`/tecnicos/taller/${this.currentWorkshop}`).subscribe({
      next: (res) => { this.availableTechs = res; this.loadingTechs = false; },
      error: () => { this.loadingTechs = false; toast.error('Error al cargar personal'); }
    });
  }

  toggleTech(id: number) {
    if (this.selectedTechs.includes(id)) {
      this.selectedTechs = this.selectedTechs.filter(i => i !== id);
    } else {
      this.selectedTechs.push(id);
    }
  }

  confirmAssignment() {
    this.api.post(`/gestion-emergencia/${this.emergency.id}/asignar`, {
      tecnicos_ids: this.selectedTechs
    }).subscribe({
      next: () => {
        toast.success('Protocolo de Asignación Completado');
        this.showModal = false;
        this.router.navigate(['/app/trabajos']);
      },
      error: () => toast.error('Fallo en la confirmación de misión')
    });
  }

  goBack() { this.router.navigate(['/app/dashboard']); }

  // ─── CU10: Ficha Técnica ─────────────────────────────────────────
  openFichaModal() {
    const ficha = this.emergency?.resumen_ia?.ficha_tecnica || {};
    this.fichaEdit = {
      resumen: this.emergency?.resumen_ia?.resumen || '',
      ficha_tecnica: {
        diagnostico_probable: Array.isArray(ficha.diagnostico_probable) ? ficha.diagnostico_probable.join(', ') : (ficha.diagnostico_probable || ''),
        piezas_necesarias: Array.isArray(ficha.piezas_necesarias) ? ficha.piezas_necesarias.join(', ') : (ficha.piezas_necesarias || ''),
        repuestos_sugeridos: Array.isArray(ficha.repuestos_sugeridos) ? ficha.repuestos_sugeridos.join(', ') : (ficha.repuestos_sugeridos || ''),
        acciones_inmediatas: Array.isArray(ficha.acciones_inmediatas) ? ficha.acciones_inmediatas.join(', ') : (ficha.acciones_inmediatas || '')
      }
    };
    this.showFichaModal = true;
  }

  saveFicha() {
    const payload = {
      resumen: this.fichaEdit.resumen,
      ficha_tecnica: {
        diagnostico_probable: this.fichaEdit.ficha_tecnica.diagnostico_probable.split(',').map((s: string) => s.trim()).filter(Boolean),
        piezas_necesarias: this.fichaEdit.ficha_tecnica.piezas_necesarias.split(',').map((s: string) => s.trim()).filter(Boolean),
        repuestos_sugeridos: this.fichaEdit.ficha_tecnica.repuestos_sugeridos.split(',').map((s: string) => s.trim()).filter(Boolean),
        acciones_inmediatas: this.fichaEdit.ficha_tecnica.acciones_inmediatas.split(',').map((s: string) => s.trim()).filter(Boolean),
      }
    };
    this.api.patch(`/talleres/${this.emergency.id}/ficha-tecnica`, payload).subscribe({
      next: () => {
        toast.success('Ficha técnica actualizada');
        this.showFichaModal = false;
        this.loadDetail();
      },
      error: () => toast.error('Error al actualizar ficha técnica')
    });
  }

  // ─── CU05: Gestionar Tipo de Pago ────────────────────────────────
  cargarPago() {
    if (!this.emergency || !this.emergency.id) return;
    this.api.get<any>(`/pagos/${this.emergency.id}`).subscribe({
      next: (res) => { this.pagoExistente = res; },
      error: () => { 
        this.pagoExistente = null; 
      }
    });
  }

  cargarHistorialVehicular() {
    if (!this.emergency?.vehiculo?.placa) return;
    this.loadingHistorial = true;
    this.reportesService.obtenerHistorialVehiculo(this.emergency.vehiculo.placa).subscribe({
      next: (res) => {
        this.historialVehicular = res.filter(h => h.id_emergencia !== this.emergency.id);
        this.loadingHistorial = false;
      },
      error: () => {
        this.loadingHistorial = false;
      }
    });
  }

  // ─── CU17: Gestionar Cotizaciones ────────────────────────────────
  cargarCotizaciones() {
    if (!this.emergency || !this.emergency.id) return;
    this.api.get<any[]>(`/cotizaciones/emergencia/${this.emergency.id}`).subscribe({
      next: (res) => {
        this.cotizaciones = res;
      },
      error: () => {
        console.warn('No se pudieron cargar las cotizaciones');
      }
    });
  }

  openCotizacionModal() {
    this.newCotizacion = {
      descripcion_servicio: '',
      costo_mano_obra: 0,
      costo_repuestos: 0,
      tiempo_estimado_horas: 1,
      condiciones: ''
    };
    this.showCotizacionModal = true;
  }

  enviarCotizacion() {
    if (!this.newCotizacion.descripcion_servicio || this.newCotizacion.costo_mano_obra < 0) {
      toast.error('Complete la descripción y asigne un costo válido.');
      return;
    }
    
    this.api.post(`/cotizaciones/${this.emergency.id}`, this.newCotizacion).subscribe({
      next: (res) => {
        toast.success('Cotización enviada al cliente.');
        this.showCotizacionModal = false;
        this.cargarCotizaciones();
      },
      error: (err) => toast.error('Error al enviar cotización', { description: err.error?.detail })
    });
  }

  aceptarCotizacion(cotizacionId: number) {
    this.api.put(`/cotizaciones/${cotizacionId}/estado`, { estado: 'ACEPTADA' }).subscribe({
      next: () => {
        toast.success('Cotización Aceptada. El taller ha sido asignado.');
        this.loadDetail(); // Recarga todo para actualizar estado a ASIGNADO y ocultar botones
      },
      error: (err) => toast.error('Error al aceptar cotización', { description: err.error?.detail })
    });
  }

  // ─── INVOICE LOGIC ───────────────────────────────────────────────
  facturaItems: any[] = [];
  facturaSubtotal = 0;
  facturaImpuestos = 0;
  facturaTotalGeneral = 0;

  addFacturaItem() {
    this.facturaItems.push({
      descripcion: '',
      tipo: 'servicio',
      cantidad: 1,
      precio_unitario: 0,
      total: 0
    });
  }

  removeFacturaItem(index: number) {
    this.facturaItems.splice(index, 1);
    this.calcFacturaTotal();
  }

  calcItemTotal(item: any) {
    item.total = item.cantidad * item.precio_unitario;
    this.calcFacturaTotal();
  }

  calcFacturaTotal() {
    this.facturaSubtotal = this.facturaItems.reduce((acc, item) => acc + item.total, 0);
    this.facturaTotalGeneral = this.facturaSubtotal + (this.facturaImpuestos || 0);
  }

  registrarPago() {
    if (this.facturaItems.length === 0) {
      toast.error('Agrega al menos un ítem a la factura');
      return;
    }
    
    // Validar items
    for (let item of this.facturaItems) {
      if (!item.descripcion || item.precio_unitario < 0) {
        toast.error('Completa todos los campos de la factura correctamente');
        return;
      }
    }

    const payload = {
      monto_total: this.facturaTotalGeneral,
      factura: {
        items: this.facturaItems,
        subtotal: this.facturaSubtotal,
        impuestos: this.facturaImpuestos,
        total_general: this.facturaTotalGeneral
      }
    };
    
    this.api.post(`/talleres/solicitudes/${this.emergency.id}/finalizar`, payload).subscribe({
      next: (res) => {
        toast.success(`Factura emitida y notificada al cliente.`);
        this.showPagoModal = false;
        this.loadDetail();
      },
      error: (err) => toast.error('Error al emitir factura', { description: err.error?.detail })
    });
  }

  downloadFactura() {
    const url = this.configService.apiUrl ? this.configService.apiUrl.replace('/api/v1', '') : 'http://localhost:8000';
    window.open(`${url}/api/v1/facturacion/${this.emergency.id}/pdf`, '_blank');
  }

  // ─── CHAT METHODS ───────────────────────────────────────────────
  openChat() {
    this.showChatModal = true;
    this.loadChatHistory();
  }

  closeChat() {
    this.showChatModal = false;
  }

  loadChatHistory() {
    if (!this.emergency) return;
    this.api.get<any[]>(`/chat/${this.emergency.id}`).subscribe(res => {
      this.chatMessages = res;
      this.scrollToBottom();
    });
  }

  sendChatMessage() {
    if (!this.newChatMessage.trim() && !this.chatFile) return;

    if (this.chatFile) {
       this.uploadChatFile();
       return;
    }

    const payload = { contenido: this.newChatMessage };
    this.newChatMessage = ''; // Vaciar instantáneamente para mejor UX
    this.api.post(`/chat/${this.emergency.id}`, payload).subscribe(res => {
       // El mensaje llegará por WebSocket o ya lo añadimos localmente si queremos
    });
  }

  onChatFileSelected(event: any) {
    this.chatFile = event.target.files[0];
    if (this.chatFile) this.uploadChatFile();
  }

  uploadChatFile() {
    if (!this.chatFile) return;
    const formData = new FormData();
    formData.append('file', this.chatFile);

    this.api.post(`/chat/${this.emergency.id}/upload_media`, formData).subscribe(res => {
       this.chatFile = null;
       this.newChatMessage = '';
    });
  }

  // ─── AUDIO RECORDING ─────────────────────────────────────────────
  isRecording = false;
  mediaRecorder: MediaRecorder | null = null;
  audioChunks: Blob[] = [];
  
  private recordingTimer: any;
  private isLongPress = false;

  onMicPointerDown(event: PointerEvent) {
    // Si ya está grabando, significa que lo activó con un clic anterior. Detenemos y enviamos.
    if (this.isRecording) {
      this.stopRecording();
      return;
    }
    
    // Iniciar grabación
    this.startRecording();
    this.isLongPress = false;
    
    // Después de 300ms, lo consideramos "mantener presionado"
    this.recordingTimer = setTimeout(() => {
      this.isLongPress = true;
    }, 300);
  }

  onMicPointerUp(event: PointerEvent) {
    clearTimeout(this.recordingTimer);
    // Solo detenemos si fue un "mantener presionado" prolongado. Si fue un clic rápido, lo ignoramos y dejamos grabando.
    if (this.isLongPress && this.isRecording) {
      this.stopRecording();
    }
  }

  async startRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      toast.error('Tu navegador no soporta grabación de audio.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.chatFile = new File([audioBlob], `audio_${Date.now()}.webm`, { type: 'audio/webm' });
        this.uploadChatFile();
        
        // Detener los tracks del micrófono
        stream.getTracks().forEach(track => track.stop());
      };

      this.mediaRecorder.start();
      this.isRecording = true;
    } catch (err) {
      console.error('Error al acceder al micrófono:', err);
      toast.error('No se pudo acceder al micrófono.');
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
    }
  }
}
