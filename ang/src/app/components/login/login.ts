import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormGroup, FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../application/Services/auth-service';
import {
  MatFormField,
  MatFormFieldModule,
  MatLabel,
  MatPrefix,
} from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInput, MatInputModule } from '@angular/material/input';
import { catchError, of, Subscription } from 'rxjs';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-login',
  imports: [
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatIconModule,
    MatFormFieldModule,
    MatInput,
    MatInputModule,
    RouterLink,
    ToastModule,
  ],
  templateUrl: './login.html',
  providers: [MessageService],
  styleUrl: './login.css',
})
export class Login implements OnInit, OnDestroy {
  ngOnDestroy(): void {
    this.subs.forEach((c) => c.unsubscribe());
  }
  messageService = inject(MessageService);
  public FormGr!: FormGroup;
  public hide =signal(true);
  private Fb = inject(FormBuilder);
  private authservice = inject(AuthService);
  router = inject(Router);
  subs: Subscription[] = [];
  ngOnInit(): void {
    this.FormGr = this.Fb.nonNullable.group({
      password: ['', Validators.required],
      email: ['', Validators.required],
    });
  }
  OnSumbit() {
    const email = this.FormGr.get('email')?.value;

    const password = this.FormGr.get('password')?.value;

    this.subs.push(
      this.authservice
        .login(password, email)
        .pipe(
          catchError((err) => {
            this.showError(err);
            return of(null);
          }),
        )
        .subscribe({
          next: (value) => {
            if (!value) return;
            if (value.success) {
              this.showSuccess(value.message);
              setTimeout(() => this.router.navigate(['/home']), 3000);
            }
          },
          error: (err) => {
            console.log(err);
          },
        }),
    );
  }
  Onshow() {
    this.hide.update(prev=>!prev);
  }
  showError(e: any) {
    console.log('Showing Success Toast:', e);
    this.messageService.add({
      severity: 'error',
      summary: 'Error',
      detail: `ErrorHappen${e}`,
      life: 4000,
    });
  }
  showSuccess(e: string) {
    console.log('Showing Success Toast:', e);
    this.messageService.add({ severity: 'success', summary: 'Success', detail: e, life: 4000 });
  }
}
