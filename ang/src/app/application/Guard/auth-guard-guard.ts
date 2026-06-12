import { CanActivateFn, Router } from '@angular/router';
import { User } from '../../Interface/user'
import { inject } from '@angular/core';


export const authGuardGuard: CanActivateFn = (route, state) => {
   const router = inject(Router);
  console.log(state)
  console.log(route)
  const data = localStorage.getItem("user")
  if(!data){
    return router.navigate(['/login']);
    
  }
  const user:User =JSON.parse(data)
  if(!user.verified){
     return router.navigate(['/verifemail']);
    

  }
  return true

 
};
