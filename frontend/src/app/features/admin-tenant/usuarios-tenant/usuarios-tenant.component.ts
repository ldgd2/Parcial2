import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { UsuariosTenantService, UsuarioTenant, RolOut } from '../../../core/services/usuarios-tenant.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-usuarios-tenant',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './usuarios-tenant.component.html',
  styleUrls: ['./usuarios-tenant.component.scss']
})
export class UsuariosTenantComponent implements OnInit {
  usuarios: UsuarioTenant[] = [];
  roles: RolOut[] = [];
  
  showModal = false;
  usuarioForm: FormGroup;
  isSubmitting = false;

  constructor(
    private usuariosService: UsuariosTenantService,
    private fb: FormBuilder
  ) {
    this.usuarioForm = this.fb.group({
      nombre: ['', Validators.required],
      apellido: [''],
      correo: ['', [Validators.required, Validators.email]],
      contrasena: ['', [Validators.required, Validators.minLength(6)]],
      rol_id: ['', Validators.required],
      telefono: ['']
    });
  }

  ngOnInit(): void {
    this.cargarUsuarios();
    this.cargarRoles();

    // Requerir telefono solo si el rol es tecnico
    this.usuarioForm.get('rol_id')?.valueChanges.subscribe(rolId => {
      const selectedRol = this.roles.find(r => r.id === parseInt(rolId, 10));
      const isTecnico = selectedRol?.nombre === 'MECANICO' || selectedRol?.nombre === 'TECNICO';
      
      if (isTecnico) {
        this.usuarioForm.get('telefono')?.setValidators([Validators.required]);
      } else {
        this.usuarioForm.get('telefono')?.clearValidators();
      }
      this.usuarioForm.get('telefono')?.updateValueAndValidity();
    });
  }

  cargarUsuarios(): void {
    this.usuariosService.listarUsuarios().subscribe({
      next: (data) => this.usuarios = data,
      error: () => toast.error('Error al cargar usuarios')
    });
  }

  cargarRoles(): void {
    this.usuariosService.obtenerRoles().subscribe({
      next: (data) => this.roles = data,
      error: () => toast.error('Error al cargar roles')
    });
  }

  openCreateModal(): void {
    this.usuarioForm.reset();
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
  }

  onSubmit(): void {
    if (this.usuarioForm.invalid) return;

    this.isSubmitting = true;
    const data = this.usuarioForm.value;
    
    this.usuariosService.crearUsuario(data).subscribe({
      next: () => {
        toast.success('Usuario creado con éxito');
        this.cargarUsuarios();
        this.closeModal();
        this.isSubmitting = false;
      },
      error: (err) => {
        toast.error(err.error?.detail || 'Error al crear usuario');
        this.isSubmitting = false;
      }
    });
  }

  toggleEstado(u: UsuarioTenant): void {
    const nuevoEstado = u.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    this.usuariosService.cambiarEstado(u.tipo, u.id, nuevoEstado).subscribe({
      next: () => {
        u.estado = nuevoEstado;
        toast.success('Estado actualizado');
      },
      error: () => toast.error('Error al actualizar estado')
    });
  }
}
