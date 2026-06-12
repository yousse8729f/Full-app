import { ApplicationConfig, provideBrowserGlobalErrorListeners, inject } from '@angular/core';
import { provideRouter, withDebugTracing } from '@angular/router';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeuix/themes/aura';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './application/Interceptors/auth-interceptor';
import { provideApollo } from 'apollo-angular';
import { HttpLink } from 'apollo-angular/http';
import { InMemoryCache } from '@apollo/client';
import { provideMarkdown } from 'ngx-markdown';

const uri = 'http://localhost:8090/graphql';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes,),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideMarkdown(),
    
  
   providePrimeNG({
    ripple: true,
            theme: {
                preset: Aura,
               
            }
        }),
         provideHttpClient(), provideApollo(() => {
      const httpLink = inject(HttpLink);

      return {
        link: httpLink.create({
          uri,
        }),
        cache: new InMemoryCache(),
      };
    })
  ],
};
