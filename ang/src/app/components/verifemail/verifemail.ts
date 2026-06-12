import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { AuthService } from '../../application/Services/auth-service';
import { User } from '../../Interface/user';
import { Router, RouterLink } from '@angular/router';
import { catchError, of, Subscription, takeUntil } from 'rxjs';
import { ToastModule, ToastItem } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { MatIconModule } from '@angular/material/icon';
@Component({
  selector: 'app-verifemail',
  imports: [RouterLink, ToastModule, ToastItem, MatIconModule],
  templateUrl: './verifemail.html',
  styleUrl: './verifemail.css',
  standalone: true,
  providers: [MessageService],
})
export class Verifemail implements  OnDestroy {
  public subs: Subscription[] = [];
  public messageService = inject(MessageService);
  public routes = inject(Router);
  ngOnDestroy(): void {
    this.subs.forEach((e) => e.unsubscribe());
  }
  onlyNumbers(event: any) {
    const pattern = /[0-9]/;
    let inputChar = String.fromCharCode(event.charCode);
    if (!pattern.test(inputChar)) {
      event.preventDefault();
    }
  }

  auth = inject(AuthService);
  user=signal<User|null>(this.auth.UserData())
  clicker() {
    if (this.user() == null) return;
    const email = this.user()?.email;
    this.subs.push(
      this.auth.Resend(email!).subscribe((res) => {
        this.showError('send');
      }),
    );
  }
  Verif_email(code: string) {
    if (!this.user) {
      this.showError('No user found in local storage!');
      return;
    }

    this.subs.push(
      this.auth
        .verifier(this.user()?.email!, code)
        .pipe(
          catchError((err) => {
            this.showError('error happen');
            return of(null);
          }),
        )
        .subscribe({
          next: (value) => {
            if (!value) return;
            this.showSuccess(value.message);
            this.routes.navigate(['/home']);
          },
        }),
    );
  }
  showError(e: any) {
    this.messageService.add({
      severity: 'error',
      summary: 'Error',
      detail: `ErrorHappen${e}`,
      life: 4000,
    });
  }
  showSuccess(e: string) {
    this.messageService.add({ severity: 'success', summary: 'Success', detail: e, life: 4000 });
  }
}
