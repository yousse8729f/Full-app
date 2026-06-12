import { HttpErrorResponse, HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../Services/auth-service';
import { tap } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authservice = inject(AuthService);
  const token = authservice.getToken();

  const publicUrls = ['/api/login', '/api/register', '/api/emailverif', '/api/resend'];
  const isPublic = publicUrls.some((url) => req.url.includes(url));
  if (isPublic) return next(req);
  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }


  return next(req).pipe(
    tap({
      error: (err: HttpErrorResponse) => {
       
        if (err.status === 401) {
          console.error('Session expired or invalid token.');
          authservice.logout(); // Ensure your AuthService has a logout method
          alert('Your session has expired. Please log in again.');
        }

        // 4. DEBUG 403: Add a log for 403 to see what's happening in dev
        if (err.status === 403) {
          console.error('403 Forbidden: You do not have the ROLE_USER permission.');
        }
      },
    }),
  );
};
