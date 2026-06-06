import { Directive, Input, TemplateRef, ViewContainerRef, inject, effect } from '@angular/core';
import { AuthService } from '../services/auth.service';

@Directive({
  selector: '[appHasPermission]',
  standalone: true
})
export class HasPermissionDirective {
  private auth = inject(AuthService);
  private templateRef = inject(TemplateRef);
  private vcr = inject(ViewContainerRef);
  private permission: string = '';
  private hasView = false;

  @Input() set appHasPermission(permissionCode: string) {
    this.permission = permissionCode;
    this.updateView();
  }

  constructor() {
    effect(() => {
      // Re-evaluate when the currentUser signal changes
      this.auth.currentUser(); 
      this.updateView();
    });
  }

  private updateView() {
    let hasPerm = true;
    if (this.permission && this.permission !== '') {
      hasPerm = this.auth.hasPermission(this.permission);
    }
    
    if (hasPerm && !this.hasView) {
      this.vcr.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (!hasPerm && this.hasView) {
      this.vcr.clear();
      this.hasView = false;
    }
  }
}
