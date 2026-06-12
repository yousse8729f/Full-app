import { inject, DestroyRef } from '@angular/core';
import { signalStore, withState, patchState, withMethods } from '@ngrx/signals';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs/operators';
import { Graphql } from '../application/Services/graphql';
import { ConversationMessage } from '../Interface/Conversation-messages';
import { UserStore } from './userStore';

type ConversationState = {
  all_conversation: ConversationMessage[];
  isLoading: boolean;
};

const initialState: ConversationState = {
  all_conversation: [],
  isLoading: false,
};

export const conversationStore = signalStore(
  withState(initialState),

  withMethods((store,userStore=inject(UserStore) ,graphqlConv = inject(Graphql), destroyRef = inject(DestroyRef)) => ({
    loadconv() {
      const user = userStore.user()
      patchState(store, { isLoading: true });

      graphqlConv
        .getAllconv(user.id)
        .pipe(
          filter((result) => !result.loading),
          map((res) => (res.data?.allConvsByUserId as ConversationMessage[]) || []),
          takeUntilDestroyed(destroyRef),
        )
        .subscribe({
          next: (data) => {
            patchState(store, {
              all_conversation: data,
              isLoading: false,
            });
          },
          error: (err) => {
            console.error('Failed to load conversations', err);
            patchState(store, { isLoading: false });
          },
        });
    },

    createConv(txt: string) {
        const user = userStore.user()
      graphqlConv
        .createnewConv(user.id, txt)
        .pipe(takeUntilDestroyed(destroyRef))
        .subscribe({
          next: (value) => {
            if (value) {
                return true
            }
            return false
          },
          error: (err) => {
            console.error('Failed to create conversation', err);
            return false
          },
        });
    },
  })),
);
