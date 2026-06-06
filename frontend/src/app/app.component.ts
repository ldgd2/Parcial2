import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { SocketService } from './core/services/socket.service';
import { OfflineSyncService } from './core/services/offline-sync.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <main class="app-layout">
      <!-- Indicador Offline PWA -->
      <div *ngIf="!isOnline" class="bg-red-500 text-white text-center py-1 font-semibold text-sm w-full fixed top-0 z-50 shadow-md">
        Fuera de conexión
      </div>
      <div [class.mt-6]="!isOnline">
        <router-outlet></router-outlet>
      </div>
    </main>
  `,
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'frontend';
  isOnline: boolean = navigator.onLine;

  constructor(
    private router: Router,
    private socketService: SocketService,
    private offlineSync: OfflineSyncService
  ) {
    window.addEventListener('online', () => this.isOnline = true);
    window.addEventListener('offline', () => this.isOnline = false);
  }
}
