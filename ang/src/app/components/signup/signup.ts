import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../application/Services/auth-service';
import { Router, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatFormField, MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatInput, MatInputModule } from '@angular/material/input';
import { combineLatest, catchError, exhaustMap, Subject, Subscription, of } from 'rxjs';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { User } from '../../Interface/user';
@Component({
  selector: 'app-signup',
  imports: [
    ReactiveFormsModule,
    MatIconModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatFormFieldModule,
    MatInputModule,
    RouterLink,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './signup.html',
  styleUrl: './signup.css',
  standalone: true,
})
export class Signup implements OnInit, OnDestroy {
  ngOnDestroy(): void {
    if (this.Subscribe) {
      this.Subscribe.unsubscribe();
    }
  }
  messageService = inject(MessageService);

  private Fb = inject(FormBuilder);
  private authservice = inject(AuthService);
  router = inject(Router);
  public hide =signal(true);
  public confirm =signal(false);
  public Subscribe!: Subscription;
  public state =signal('');
  public Signup$ = new Subject<void>();
  public FormGr: FormGroup = this.Fb.nonNullable.group({
    name: ['', Validators.required],
    lastname: ['', Validators.required],
    password: ['', Validators.required],
    confirmpassword: [''],
    email: ['', [Validators.required, Validators.email]],
  });
  ngOnInit(): void {
    

    this.FormGr.controls['confirmpassword'].disable();
    this.FormGr.controls['password'].valueChanges.subscribe((res: string) => {
      if (res != '') {
        this.FormGr.controls['confirmpassword'].addValidators(Validators.required);
        this.FormGr.controls['confirmpassword'].enable();
      }
    });
    this.FormGr.statusChanges.subscribe((rss) => {
      this.state.set(rss);
      console.log(rss);
    });
    combineLatest([
      this.FormGr.controls['confirmpassword'].valueChanges,
      this.FormGr.controls['password'].valueChanges,
    ]).subscribe(([confirm, password]) => {
      this.confirm.set(confirm && password && confirm === password);
    });

    this.Subscribe = this.Signup$.pipe(
      exhaustMap(() => {
        const email = this.FormGr.get('email')?.value;
        const name = this.FormGr.get('name')?.value;
        const lastname = this.FormGr.get('lastname')?.value;
        const password = this.FormGr.get('password')?.value;
        const userPayload: Pick<User, "name" | "lastname" | "email"> = {
    name,
    lastname,
    email,
  };
        return this.authservice.Signup(userPayload,password).pipe(
          catchError((err: any) => {
            this.showError('SignupFailed');
            return of(null);
          }),
        );
      }),
    ).subscribe({
      next: (value) => {
        if (value) {
          this.showSuccess(value.message);
          const currentEmail = this.FormGr.get('email')?.value;
          setTimeout(
            () => this.router.navigate(['/verifemail'], { queryParams: { email: currentEmail } }),
            3000,
          );
        }
      },
    });
  }
  OnSignup() {
    if (this.FormGr.valid && this.confirm()) {
      this.Signup$.next();
    }
  }
  Onshow() {
    this.hide.update(prev=>!prev);
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
