import { ChangeDetectorRef, Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { User } from '../../Interface/user';
import { AuthService } from '../../application/Services/auth-service';
import { Router, RouterLink } from '@angular/router';
import {
  MatList,
  MatListItem,
  MatListItemLine,
  MatListModule,
  MatNavList,
} from '@angular/material/list';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { Navbar } from '../navbar/navbar';
import { interval, map, Subscription, take, window } from 'rxjs';
import { MarqueeI } from '../marquee-i/marquee-i';
import { Cards } from '../cards/cards';

@Component({
  selector: 'app-home',
  imports: [RouterLink, MatListModule, MatIconModule, MatFormFieldModule, Navbar, MarqueeI, Cards],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit, OnDestroy {
  ngOnDestroy(): void {
    this.subs.forEach((s) => s.unsubscribe());
  }
  public User!: User | null;
  private authService = inject(AuthService);
  private subs: Subscription[] = [];
  route = inject(Router);
  cmptask=signal(0);
  usedapp=signal(0);
  rate = signal(0);

  ngOnInit(): void {
    this.User = this.authService.UserData();
    console.log(this.User);
    this.OnCount('cmptask', 100, 2500);
    this.OnCount('usedapp', 5, 2600);
    this.OnCount('rate', 98, 2000);
  }
  LogOUTUser() {
    this.authService.logout();
    globalThis.location.reload();
  }
  cdr = inject(ChangeDetectorRef);
  OnCount(key: 'cmptask' | 'usedapp' | 'rate', target: number, duration: number) {
    const stepTime = duration / target;
    this.subs.push(
      interval(stepTime)
        .pipe(
          take(target + 1),
          map((val) => val),
        )
        .subscribe((val) => {
          this[key].set(val);
          this.cdr.detectChanges();
        }),
    );
  }
}
