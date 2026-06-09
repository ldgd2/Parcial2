import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent)
  },
  {
    path: 'auth/login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'auth/register',
    loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'app',
    loadComponent: () => import('./shared/layouts/main-layout/main-layout.component').then(m => m.MainLayoutComponent),
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'radar',
        loadComponent: () => import('./features/radar/radar.component').then(m => m.RadarComponent)
      },
      {
        path: 'emergency/:id',
        loadComponent: () => import('./features/emergencias/detalle/emergency-detail.component').then(m => m.EmergencyDetailComponent)
      },
      {
        path: 'talleres',
        loadComponent: () => import('./features/talleres/talleres.component').then(m => m.TalleresComponent)
      },
      {
        path: 'taller/:cod',
        loadComponent: () => import('./features/talleres/detalle/taller-detail.component').then(m => m.TallerDetailComponent)
      },
      // ── Super Admin ────────────────────────────────────────────────────────
      {
        path: 'super/dashboard',
        loadComponent: () => import('./features/super-admin/super-dashboard/super-dashboard.component').then(m => m.SuperDashboardComponent)
      },
      {
        path: 'super/tenants',
        loadComponent: () => import('./features/saas-admin/tenants-list/tenants-list.component').then(m => m.TenantsListComponent)
      },
      {
        path: 'super/planes',
        loadComponent: () => import('./features/super-admin/planes/planes.component').then(m => m.PlanesComponent)
      },
      {
        path: 'super/audit-log',
        loadComponent: () => import('./features/super-admin/audit-log/audit-log.component').then(m => m.AuditLogComponent)
      },
      {
        path: 'super/backups',
        loadComponent: () => import('./features/super-admin/backups/backups.component').then(m => m.BackupsComponent)
      },
      {
        path: 'super/restricciones',
        loadComponent: () => import('./features/super-admin/restricciones/restricciones.component').then(m => m.RestriccionesComponent)
      },
      // Alias legacy
      {
        path: 'saas-admin/tenants',
        redirectTo: 'super/tenants',
        pathMatch: 'full'
      },
      {
        path: 'reportes/historial-vehicular',
        loadComponent: () => import('./features/reportes/historial-vehicular/historial-vehicular.component').then(m => m.HistorialVehicularComponent)
      },
      {
        path: 'calificaciones',
        loadComponent: () => import('./features/reportes/calificaciones/calificaciones.component').then(m => m.CalificacionesComponent)
      },
      {
        path: 'usuarios',
        loadComponent: () => import('./features/admin-tenant/usuarios-tenant/usuarios-tenant.component').then(m => m.UsuariosTenantComponent)
      },
      {
        path: 'tecnicos',
        loadComponent: () => import('./features/tecnicos/tecnicos.component').then(m => m.TecnicosComponent)
      },
      {
        path: 'trabajos',
        loadComponent: () => import('./features/trabajos/trabajos.component').then(m => m.TrabajosComponent)
      },
      {
        path: 'reportes',
        loadComponent: () => import('./features/reportes/reportes.component').then(m => m.WorkshopReportsComponent)
      },
      {
        path: 'suscripcion',
        loadComponent: () => import('./features/suscripcion/suscripcion.component').then(m => m.SuscripcionComponent)
      },
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: 'showcase',
    loadComponent: () => import('./features/showcase/showcase.component').then(m => m.ShowcaseComponent)
  },
  {
    path: 'dashboard',
    redirectTo: 'app/dashboard',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
