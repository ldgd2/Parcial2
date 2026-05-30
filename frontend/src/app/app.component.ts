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
      <router-outlet></router-outlet>
    </main>
  `,
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'frontend';

  constructor(
    private router: Router,
    private socketService: SocketService,
    private offlineSync: OfflineSyncService
  ) {}
}
