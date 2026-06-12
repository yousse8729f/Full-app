import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Signup } from './components/signup/signup';
import { Login } from './components/login/login';
import { Verifemail } from './components/verifemail/verifemail';
import { authGuardGuard } from './application/Guard/auth-guard-guard';
import { Aichat } from './components/aichat/aichat';


export const routes: Routes = [
  { path: 'home', title: 'home', component: Home },
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'signup', title: 'signup', component: Signup },
  
  { path: 'login', title: 'login', component: Login },
  { path: 'verifemail', title: 'verifemail', component: Verifemail },
  {path:'aichat',title:'aichat',component:Aichat},
  {path:'aichat/:convId',title:'aichat',component:Aichat}
 


];
