import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { filter, map } from 'rxjs/operators';
import { toObservable } from '@angular/core/rxjs-interop';

export const permissionGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  
  const requirePermission = route.data['requirePermission'] as string;
  if (!requirePermission) return true;

  // We need to wait until auth isReady
  const isReady$ = toObservable(auth.isReady).pipe(
    filter(ready => ready)
  );

  return isReady$.pipe(
    map(() => {
      if (auth.hasPermission(requirePermission)) {
        return true;
      }
      
      // If not permitted, redirect to dashboard
      return router.createUrlTree(['/app/dashboard']);
    })
  );
};
