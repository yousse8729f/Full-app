import { Injectable, signal,untracked } from '@angular/core';
import { interval, Observable, Subject, Subscription, timer } from 'rxjs';
import { retry, tap, delayWhen, delay } from 'rxjs/operators';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Injectable({
  providedIn: 'root',
})
export class WebsocketService {
  private socket$!: WebSocketSubject<any>;
  private messagesSubject$ = new Subject<any>();
  public messages$ = this.messagesSubject$.asObservable();
  public connectweb = signal<Boolean>(false);
  private subscription?: Subscription;
  constructor() {}
  connect(url: string) {
    if (this.socket$) {
    
      this.socket$.complete();
      this.connectweb.set(false);
    }
    if (url) {
      this.socket$ = webSocket({
        url,
        openObserver: {
          next: () => {
            console.log('websocket connected');
            this.connectweb.set(true);
          },
        },
        closeObserver: {
          next: () => {
            console.log('websocket disconnected');
            this.connectweb.set(false);
          },
        },
      });
    this.socket$
        .pipe(
          retry({
            delay: (error, retryCount) => {
              this.connectweb.set(false); // Ensure status reflects connection issues
            return timer(3000);
            },
          }),
          tap({
            error: (error) => console.error(error),
          }),
        )
        .subscribe({
          next: (message) => {
            this.messagesSubject$.next(message);
          },
          error: (err) => {
            console.error('websocket error :', err);
          },
        });
    }
  }
  sendMessage(message: any): void {
    if (this.socket$) {
      this.socket$.next(message);
    }
  }
  disconnect(): void {
    if (this.socket$) {
      this.socket$.complete();
    }
  }
}
