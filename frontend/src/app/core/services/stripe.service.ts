import { Injectable } from '@angular/core';
import { loadStripe, Stripe } from '@stripe/stripe-js';
import { ApiService } from '../api/api.service';
import { Observable, from } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class StripeService {
  private stripePromise: Promise<Stripe | null> | null = null;

  constructor(private api: ApiService) {}

  async getStripe(): Promise<Stripe | null> {
    if (!this.stripePromise) {
      this.stripePromise = new Promise((resolve, reject) => {
        this.api.get<{ publishableKey: string }>('/stripe/config').subscribe({
          next: async (res) => {
            if (res.publishableKey) {
              const stripeInstance = await loadStripe(res.publishableKey);
              resolve(stripeInstance);
            } else {
              console.warn("No Stripe publishable key found from backend.");
              resolve(null);
            }
          },
          error: (err) => {
            console.error('Error fetching Stripe config:', err);
            resolve(null);
          }
        });
      });
    }
    return this.stripePromise;
  }

  createPaymentIntent(planId: number): Observable<{ clientSecret: string | null, message?: string }> {
    return this.api.post<{ clientSecret: string | null, message?: string }>('/stripe/create-payment-intent', { plan_id: planId });
  }
}
