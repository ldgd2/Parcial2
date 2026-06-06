import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReportesService, KpiResponse } from '../../core/services/reportes.service';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions } from 'chart.js';
import { LucideAngularModule } from 'lucide-angular';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective, LucideAngularModule],
  template: `
    <div class="p-8 lg:p-12 min-h-screen bg-[#050505] text-white">
      <!-- HEADER -->
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 border-b border-zinc-900 pb-8 animate-in fade-in slide-in-from-top-4">
        <div>
          <h1 class="text-4xl font-bold tracking-tight mb-2 uppercase">Inteligencia Operacional</h1>
          <div class="flex items-center gap-3">
             <div class="w-2 h-2 bg-primary"></div>
             <p class="font-mono text-[10px] uppercase tracking-[.3em] text-zinc-500">Analítica de Desempeño</p>
          </div>
        </div>

        <!-- RANGE SELECTOR -->
        <div class="flex items-center gap-px bg-zinc-900 border border-zinc-800 p-1">
          <button (click)="setRange('diario')" 
                  [class]="range === 'diario' ? 'bg-[#050505] text-primary' : 'bg-transparent text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white">
            Diario
          </button>
          <button (click)="setRange('semanal')" 
                  [class]="range === 'semanal' ? 'bg-[#050505] text-primary' : 'bg-transparent text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white">
            Semanal
          </button>
          <button (click)="setRange('mensual')" 
                  [class]="range === 'mensual' ? 'bg-[#050505] text-primary' : 'bg-transparent text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white">
            Mensual
          </button>
        </div>
      </div>

      <div *ngIf="loading" class="flex justify-center p-20 animate-pulse">
         <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>

      <div *ngIf="!loading && data" class="animate-in fade-in duration-700 slide-in-from-bottom-4 space-y-8">
        
        <!-- STATS GRID -->
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-px bg-zinc-900 border border-zinc-800 shadow-2xl">
          
          <div class="bg-[#050505] p-5 flex flex-col hover:bg-zinc-950 transition-colors">
            <span class="font-mono text-[9px] uppercase tracking-[.2em] text-zinc-500 mb-3 flex items-center gap-2">
              <lucide-icon name="radio" size="14" class="text-primary animate-pulse"></lucide-icon> Sol. Activas
            </span>
            <span class="font-mono text-3xl font-bold">{{ data.kpis.total_activas }}</span>
          </div>

          <div class="bg-[#050505] p-5 flex flex-col hover:bg-zinc-950 transition-colors">
            <span class="font-mono text-[9px] uppercase tracking-[.2em] text-zinc-500 mb-3 flex items-center gap-2">
              <lucide-icon name="check-circle" size="14" class="text-emerald-500"></lucide-icon> Atendidas
            </span>
            <span class="font-mono text-3xl font-bold text-emerald-500">{{ data.kpis.total_atendidas }}</span>
          </div>

          <div class="bg-[#050505] p-5 flex flex-col hover:bg-zinc-950 transition-colors">
            <span class="font-mono text-[9px] uppercase tracking-[.2em] text-zinc-500 mb-3 flex items-center gap-2">
              <lucide-icon name="clock" size="14" class="text-amber-500"></lucide-icon> T. Asignación
            </span>
            <span class="font-mono text-3xl font-bold">{{ data.kpis.tiempo_promedio_asignacion }}<span class="text-xs text-zinc-600 font-normal">m</span></span>
          </div>

          <div class="bg-[#050505] p-5 flex flex-col hover:bg-zinc-950 transition-colors">
            <span class="font-mono text-[9px] uppercase tracking-[.2em] text-zinc-500 mb-3 flex items-center gap-2">
              <lucide-icon name="clock" size="14" class="text-orange-500"></lucide-icon> T. Llegada
            </span>
            <span class="font-mono text-3xl font-bold">{{ data.kpis.tiempo_promedio_llegada }}<span class="text-xs text-zinc-600 font-normal">m</span></span>
          </div>

          <div class="bg-[#050505] p-5 flex flex-col hover:bg-zinc-950 transition-colors">
            <span class="font-mono text-[9px] uppercase tracking-[.2em] text-zinc-500 mb-3 flex items-center gap-2">
              <lucide-icon name="clock" size="14" class="text-primary"></lucide-icon> T. Resolución
            </span>
            <span class="font-mono text-3xl font-bold">{{ data.kpis.tiempo_respuesta_minutos }}<span class="text-xs text-zinc-600 font-normal">m</span></span>
          </div>

          <div class="bg-[#050505] p-5 flex flex-col hover:bg-zinc-950 transition-colors">
            <span class="font-mono text-[9px] uppercase tracking-[.2em] text-zinc-500 mb-3 flex items-center gap-2">
              <lucide-icon name="shield-check" size="14" class="text-blue-500"></lucide-icon> Cump. SLA
            </span>
            <span class="font-mono text-3xl font-bold">{{ data.kpis.tasa_cumplimiento_sla }}<span class="text-xs text-zinc-600 font-normal">%</span></span>
          </div>
        </div>

        <!-- CHARTS AREA ROW 1 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 bg-[#050505] border border-zinc-800 p-8 shadow-xl">
            <h3 class="font-mono text-[10px] uppercase tracking-[.3em] text-zinc-400 mb-6 flex items-center gap-2">
              <div class="w-1 h-3 bg-emerald-500"></div> Tendencia de Solicitudes
            </h3>
            <div class="h-[300px]">
              <canvas baseChart
                [data]="lineChartData"
                [options]="lineChartOptions"
                [type]="'line'">
              </canvas>
            </div>
          </div>
          
          <div class="bg-[#050505] border border-zinc-800 p-8 shadow-xl">
            <h3 class="font-mono text-[10px] uppercase tracking-[.3em] text-zinc-400 mb-6 flex items-center gap-2">
              <div class="w-1 h-3 bg-primary"></div> Incidentes por Tipo
            </h3>
            <div class="h-[300px] flex items-center justify-center relative">
              <canvas baseChart
                [data]="polarChartData"
                [options]="polarChartOptions"
                [type]="'polarArea'">
              </canvas>
            </div>
          </div>
        </div>

        <!-- CHARTS AREA ROW 2 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-[#050505] border border-zinc-800 p-8 shadow-xl">
            <h3 class="font-mono text-[10px] uppercase tracking-[.3em] text-zinc-400 mb-6 flex items-center gap-2">
              <div class="w-1 h-3 bg-blue-500"></div> Top 5 Zonas (Incidentes)
            </h3>
            <div class="h-[300px]">
              <canvas baseChart
                [data]="barChartData"
                [options]="barChartOptions"
                [type]="'bar'">
              </canvas>
            </div>
          </div>

          <div class="bg-[#050505] border border-zinc-800 p-8 shadow-xl flex flex-col">
            <h3 class="font-mono text-[10px] uppercase tracking-[.3em] text-zinc-400 mb-6 flex items-center gap-2">
              <div class="w-1 h-3 bg-yellow-500"></div> Ranking de Sucursales (Eficiencia)
            </h3>
            <div class="flex-1 overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="border-b border-zinc-800">
                    <th class="py-3 px-4 font-mono text-[10px] uppercase tracking-widest text-zinc-500">Rank</th>
                    <th class="py-3 px-4 font-mono text-[10px] uppercase tracking-widest text-zinc-500">Sucursal</th>
                    <th class="py-3 px-4 font-mono text-[10px] uppercase tracking-widest text-zinc-500">Atendidas</th>
                    <th class="py-3 px-4 font-mono text-[10px] uppercase tracking-widest text-zinc-500 text-right">T. Promedio</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let item of data.analitica.ranking_sucursales; let i = index" class="border-b border-zinc-900/50 hover:bg-zinc-900/20 transition-colors">
                    <td class="py-3 px-4">
                      <div class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs"
                           [ngClass]="i === 0 ? 'bg-yellow-500/20 text-yellow-500' : (i === 1 ? 'bg-zinc-300/20 text-zinc-300' : (i === 2 ? 'bg-orange-500/20 text-orange-500' : 'text-zinc-600'))">
                        {{ i + 1 }}
                      </div>
                    </td>
                    <td class="py-3 px-4 font-bold text-sm">{{ item.sucursal }}</td>
                    <td class="py-3 px-4 text-zinc-400">{{ item.atendidas }}</td>
                    <td class="py-3 px-4 text-right">
                      <span class="text-primary font-mono font-bold">{{ item.eficiencia_promedio_min | number:'1.0-1' }} m</span>
                    </td>
                  </tr>
                  <tr *ngIf="data.analitica.ranking_sucursales.length === 0">
                    <td colspan="4" class="py-10 text-center text-zinc-600 font-mono text-xs">NO HAY DATA PARA EL PERIODO</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  private reportesService = inject(ReportesService);
  
  range: 'diario' | 'semanal' | 'mensual' = 'mensual';
  data?: KpiResponse;
  loading = true;

  // Line Chart (Tendencia)
  public lineChartData: ChartConfiguration<'line'>['data'] = {
    datasets: [
      { data: [], label: 'Atendidas', borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.05)', fill: true, tension: 0.4, borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#10b981' },
      { data: [], label: 'Activas', borderColor: '#FF5733', backgroundColor: 'transparent', fill: false, tension: 0.4, borderWidth: 2, borderDash: [5, 5], pointRadius: 3, pointBackgroundColor: '#FF5733' }
    ],
    labels: []
  };
  public lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'top', align: 'end', labels: { color: '#a1a1aa', font: { size: 9, family: 'monospace' }, boxWidth: 10 } },
      tooltip: { backgroundColor: '#0a0a0a', titleFont: { size: 12 }, bodyFont: { size: 11 }, padding: 12, cornerRadius: 4, borderColor: '#27272a', borderWidth: 1 }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#52525b', font: { size: 9, family: 'monospace' } } },
      y: { grid: { color: '#18181b' }, ticks: { color: '#52525b', font: { size: 9, family: 'monospace' }, stepSize: 1 } }
    }
  };

  // Polar Area Chart (Categorias)
  public polarChartData: ChartConfiguration<'polarArea'>['data'] = {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: [
        'rgba(16, 185, 129, 0.7)',
        'rgba(59, 130, 246, 0.7)',
        'rgba(245, 158, 11, 0.7)',
        'rgba(239, 68, 68, 0.7)',
        'rgba(139, 92, 246, 0.7)'
      ],
      borderColor: '#050505',
      borderWidth: 2
    }]
  };
  public polarChartOptions: ChartOptions<'polarArea'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'right', labels: { color: '#a1a1aa', font: { size: 9, family: 'monospace' }, padding: 15, boxWidth: 10 } },
      tooltip: { backgroundColor: '#0a0a0a', bodyFont: { size: 11 }, padding: 12, cornerRadius: 4, borderColor: '#27272a', borderWidth: 1 }
    },
    scales: {
      r: {
        grid: { color: '#18181b' },
        ticks: { display: false, backdropColor: 'transparent' }
      }
    }
  };

  // Bar Chart (Zonas)
  public barChartData: ChartConfiguration<'bar'>['data'] = {
    labels: [],
    datasets: [{
      data: [],
      label: 'Incidentes',
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 1,
      borderRadius: 4
    }]
  };
  public barChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: '#0a0a0a', bodyFont: { size: 11 }, padding: 12, cornerRadius: 4, borderColor: '#27272a', borderWidth: 1 }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#a1a1aa', font: { size: 10 } } },
      y: { grid: { color: '#18181b' }, ticks: { color: '#52525b', font: { size: 9, family: 'monospace' }, stepSize: 1 } }
    }
  };

  ngOnInit() {
    this.loadData();
  }

  setRange(newRange: 'diario' | 'semanal' | 'mensual') {
    if (this.range === newRange) return;
    this.range = newRange;
    this.loadData();
  }

  loadData() {
    this.loading = true;
    this.reportesService.getKpis(this.range).subscribe({
      next: (res) => {
        this.data = res;
        this.updateCharts(res);
        this.loading = false;
      },
      error: (e) => {
        console.error('Error loading KPIs', e);
        this.loading = false;
      }
    });
  }

  updateCharts(res: KpiResponse) {
    if (!res) return;

    // 1. Tendencia Line Chart
    if (res.grafica && res.grafica.length > 0) {
      this.lineChartData.labels = res.grafica.map(g => {
        const d = new Date(g.fecha + 'T12:00:00'); // Prevent timezone shift
        return `${d.getDate()}/${d.getMonth() + 1}`;
      });
      this.lineChartData.datasets[0].data = res.grafica.map(g => g.atendidas);
      this.lineChartData.datasets[1].data = res.grafica.map(g => g.activas);
    } else {
      this.lineChartData.labels = [];
      this.lineChartData.datasets[0].data = [];
      this.lineChartData.datasets[1].data = [];
    }

    // 2. Polar Area (Tipos)
    if (res.analitica && res.analitica.incidentes_por_tipo) {
      this.polarChartData.labels = res.analitica.incidentes_por_tipo.map(i => i.tipo);
      this.polarChartData.datasets[0].data = res.analitica.incidentes_por_tipo.map(i => i.cantidad);
    }

    // 3. Bar Chart (Zonas)
    if (res.analitica && res.analitica.zonas_incidentes) {
      this.barChartData.labels = res.analitica.zonas_incidentes.map(z => z.zona);
      this.barChartData.datasets[0].data = res.analitica.zonas_incidentes.map(z => z.cantidad);
    }
  }
}
