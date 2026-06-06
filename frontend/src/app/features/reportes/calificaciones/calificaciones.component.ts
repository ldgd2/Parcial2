import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CalificacionesService, CalificacionModerada } from '../../../core/services/calificaciones.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-calificaciones',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './calificaciones.component.html',
  styleUrls: ['./calificaciones.component.scss']
})
export class CalificacionesComponent implements OnInit {
  calificaciones: CalificacionModerada[] = [];
  loading = false;

  constructor(private calificacionesService: CalificacionesService) {}

  ngOnInit(): void {
    this.cargarCalificaciones();
  }

  cargarCalificaciones(): void {
    this.loading = true;
    this.calificacionesService.obtenerCalificacionesTaller().subscribe({
      next: (data) => {
        this.calificaciones = data;
        this.loading = false;
      },
      error: () => {
        toast.error('Error al cargar las calificaciones');
        this.loading = false;
      }
    });
  }

  toggleModeracion(calif: CalificacionModerada): void {
    const nuevoEstado = calif.estado === 'PUBLICADA' ? 'OCULTADA' : 'PUBLICADA';
    this.calificacionesService.moderarCalificacion(calif.id, nuevoEstado).subscribe({
      next: () => {
        calif.estado = nuevoEstado;
        toast.success(`Calificación ${nuevoEstado.toLowerCase()} correctamente.`);
      },
      error: () => {
        toast.error('Error al cambiar el estado de la calificación');
      }
    });
  }

  getEstrellas(puntuacion: number): number[] {
    return Array(5).fill(0).map((_, i) => i + 1);
  }
}
