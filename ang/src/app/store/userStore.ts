import { signalStore, withState, withProps, withMethods, patchState } from '@ngrx/signals';
import { User } from '../Interface/user';
import { inject } from '@angular/core';
import { AuthService } from '../application/Services/auth-service';


type initUser={
    user:User
}

const state: initUser = {user:new User()};

export const UserStore = signalStore(
  withState(state),
  withProps(() => ({
    UserService :inject(AuthService)
  })),
  withMethods(({UserService,...store})=>({
    loadUser(){
        const user_data = UserService.UserData()
        if(user_data){
            patchState(store,{user:user_data})
            
        }
        else{
            patchState(store,{user:new User})

        }
    }

  }))
);
