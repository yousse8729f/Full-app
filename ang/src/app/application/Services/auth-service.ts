import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, tap, Subject } from 'rxjs';
import { User } from '../../Interface/user';
import { jwtDecode } from 'jwt-decode';
import { JwtUserPayload } from '../../Interface/jwt-user-payload';
import { Router } from '@angular/router';

const url_Signup = 'http://localhost:8090/api/register';
const url_login = 'http://localhost:8090/api/login';
const url_verfiemail = 'http://localhost:8090/api/resend';
const url_email = 'http://localhost:8090/api/emailverif';

interface AuthResponse {
  success: boolean;
  message: string;
  jwt: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly httpclientservice = inject(HttpClient);
  private route = inject(Router);
  public logout$ = new Subject<void>();

  Signup(
   user:Pick<User,"name"|"lastname"|"email">,password:string
  ): Observable<AuthResponse> {
   
    const body = { 
      email: user.email, 
      password: password, 
      lastname: user.lastname, 
      name: user.name
  };
  console.log(body)
    return this.httpclientservice
      .post<AuthResponse>(`${url_Signup}`, body, { responseType: 'json' })
      .pipe(
        tap((res) => {
          if (res && res.success) {
            this.saveToken(res.jwt);
          }
          console.log(res);
        }),
      );
  }
  private saveToken(token: string): void {
    localStorage.setItem('token', token);
  }
  getToken(): string | null {
    return localStorage.getItem('token');
  }
  login(password: string, email: string): Observable<AuthResponse> {
    const body = { password, email };
    return this.httpclientservice
      .post<AuthResponse>(url_login, body, { responseType: 'json' })
      .pipe(
        tap((res) => {
          if (res && res.success) {
            this.saveToken(res.jwt);
            const user = this.UserData();
            if (user) localStorage.setItem('user', JSON.stringify(user));
          }
        }),
      );
  }
  logout(): void {
    localStorage.clear();
    this.logout$.next();
  }
  UserData(): User | null {
    const token = this.getToken();
    if (!token) return null;

    const decoded = jwtDecode<JwtUserPayload>(token);
    console.log(decoded);
    return {
      id: decoded.id,
      verified: decoded.verified,
      email: decoded.sub!,
      name: decoded.name,
      lastname: decoded.lastname,
    };
  }
  Resend(email: string) {
    return this.httpclientservice.post(`${url_verfiemail}?email=${email}`, {});
  }
  verifier(email: string, code: string): Observable<AuthResponse> {
    const body = { email: email.trim(), code: code.trim() };
    console.log(body);
    return this.httpclientservice.post<AuthResponse>(url_email, body).pipe(
      tap((res) => {
        if (res?.success) {
          this.saveToken(res.jwt);
          const user = this.UserData();
          if (user) localStorage.setItem('user', JSON.stringify(user));
        }
      }),
    );
  }
}
