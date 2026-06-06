import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe, CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReportesService, VehiculoOut, HistorialVehicularItem } from '../../../core/services/reportes.service';
import { toast } from 'ngx-sonner';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

@Component({
  selector: 'app-historial-vehicular',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [DatePipe, CurrencyPipe],
  templateUrl: './historial-vehicular.component.html',
  styleUrls: ['./historial-vehicular.component.scss']
})
export class HistorialVehicularComponent implements OnInit {
  vehiculos: VehiculoOut[] = [];
  vehiculosFiltrados: VehiculoOut[] = [];
  busqueda: string = '';
  
  vehiculoSeleccionado: VehiculoOut | null = null;
  historial: HistorialVehicularItem[] = [];
  loading = false;
  loadingHistorial = false;

  constructor(
    private reportesService: ReportesService,
    private datePipe: DatePipe,
    private currencyPipe: CurrencyPipe
  ) {}

  ngOnInit(): void {
    this.cargarVehiculos();
  }

  cargarVehiculos(): void {
    this.loading = true;
    this.reportesService.obtenerVehiculosAtendidos().subscribe({
      next: (data) => {
        this.vehiculos = data;
        this.vehiculosFiltrados = data;
        this.loading = false;
      },
      error: () => {
        toast.error('Error al cargar la lista de vehículos');
        this.loading = false;
      }
    });
  }

  filtrarVehiculos(): void {
    const q = this.busqueda.toLowerCase();
    this.vehiculosFiltrados = this.vehiculos.filter(v => 
      v.placa.toLowerCase().includes(q) || 
      v.marca.toLowerCase().includes(q) || 
      v.modelo.toLowerCase().includes(q)
    );
  }

  seleccionarVehiculo(v: VehiculoOut): void {
    this.vehiculoSeleccionado = v;
    this.loadingHistorial = true;
    this.historial = [];
    this.reportesService.obtenerHistorialVehiculo(v.placa).subscribe({
      next: (data) => {
        this.historial = data;
        this.loadingHistorial = false;
        if (data.length === 0) {
          toast.info('Este vehículo no tiene atenciones registradas.');
        }
      },
      error: () => {
        toast.error('Error al cargar el historial del vehículo');
        this.loadingHistorial = false;
      }
    });
  }

  exportarCSV(): void {
    if (!this.historial.length) return;
    
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "ID,Fecha,Estado,Tipo,Diagnóstico Inicial,Diagnóstico Final,Servicios Realizados,Monto,Calif. Taller,Calif. Técnico\n";
    
    this.historial.forEach(h => {
      const fila = [
        h.id_emergencia,
        this.datePipe.transform(h.fecha, 'short') || '',
        h.estado_final,
        h.tipo_emergencia,
        `"${(h.diagnostico_inicial || '').replace(/"/g, '""')}"`,
        `"${(h.diagnostico_final || '').replace(/"/g, '""')}"`,
        `"${(h.servicios_realizados || '').replace(/"/g, '""')}"`,
        h.monto_total || 0,
        h.calificacion_taller || 'N/A',
        h.calificacion_tecnico || 'N/A'
      ];
      csvContent += fila.join(",") + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `historial_${this.vehiculoSeleccionado?.placa}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  exportarPDF(): void {
    if (!this.historial.length || !this.vehiculoSeleccionado) return;
    
    const doc = new jsPDF('landscape');
    
    doc.setFontSize(18);
    doc.text(`Historial Vehicular: ${this.vehiculoSeleccionado.placa}`, 14, 22);
    doc.setFontSize(11);
    doc.text(`Vehículo: ${this.vehiculoSeleccionado.marca} ${this.vehiculoSeleccionado.modelo} (${this.vehiculoSeleccionado.anio})`, 14, 30);
    
    const head = [['ID', 'Fecha', 'Tipo', 'Estado', 'Servicios', 'Monto']];
    const body = this.historial.map(h => [
      h.id_emergencia,
      this.datePipe.transform(h.fecha, 'short') || '',
      h.tipo_emergencia,
      h.estado_final,
      h.servicios_realizados || 'N/A',
      this.currencyPipe.transform(h.monto_total || 0, 'USD') || '$0.00'
    ]);

    autoTable(doc, {
      startY: 35,
      head: head,
      body: body,
      styles: { fontSize: 9 },
      headStyles: { fillColor: [41, 128, 185] }
    });

    doc.save(`historial_${this.vehiculoSeleccionado.placa}.pdf`);
  }
}
