import { ApplicationConfig, importProvidersFrom, APP_INITIALIZER, isDevMode } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { ConfigService } from './core/config/config.service';
import { 
  LucideAngularModule, 
  Home, Menu, User, Settings, AlertTriangle, Hammer, Users, 
  History, ClipboardList, LogOut, ArrowLeft, Clock, MapPin, 
  Wrench, ShieldAlert, Send, Sun, Moon, ChevronsLeft, ChevronsRight,
  LayoutDashboard, Briefcase, Factory, Eye, Globe, Plus, Bell,
  ArrowRight, Camera, Mail, KeyRound, Loader2, CheckSquare, Check, Image as ImageIcon, Tag, X, Radio, Video, Info, MessageSquare,
  TrendingUp, DollarSign, FileText, Calendar
} from 'lucide-angular';

import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { offlineInterceptor } from './core/interceptors/offline.interceptor';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';
import { provideServiceWorker } from '@angular/service-worker';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor, offlineInterceptor])),
    {
        provide: APP_INITIALIZER,
        useFactory: (configService: ConfigService) => () => configService.loadConfig(),
        deps: [ConfigService],
        multi: true
    },
    provideCharts(withDefaultRegisterables()),
    importProvidersFrom(LucideAngularModule.pick({
        Home, Menu, User, Settings, AlertTriangle, Hammer, Users,
        History, ClipboardList, LogOut, ArrowLeft, Clock, MapPin,
        Wrench, ShieldAlert, Send, Sun, Moon, ChevronsLeft, ChevronsRight,
        LayoutDashboard, Briefcase, Factory, Eye, Globe, Plus, Bell,
        ArrowRight, Camera, Mail, KeyRound, Loader2, CheckSquare, Check, Image: ImageIcon, Tag, X, Radio, Video, Info, MessageSquare,
        TrendingUp, DollarSign, FileText, Calendar
    })),
    provideServiceWorker('ngsw-worker.js', {
        enabled: !isDevMode(),
        registrationStrategy: 'registerWhenStable:30000'
    })
]
};
