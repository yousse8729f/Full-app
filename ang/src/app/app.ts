import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Signup } from './components/signup/signup';
import { Home } from './components/home/home';

import { PrimeNG } from 'primeng/config';
import { Aichat } from "./components/aichat/aichat";
import { Login } from "./components/login/login";
import { Uir } from "./uir/uir";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Signup, Home, Aichat, Login, Uir],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
   constructor(private primeng: PrimeNG) {}
 ngOnInit() {
        this.primeng.ripple.set(true);
    }
  protected readonly title = signal('ang');
}
