import { Component, computed, DestroyRef, effect, inject, OnInit, signal, untracked } from '@angular/core';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { SplitterModule } from 'primeng/splitter';
import { MenuModule, MenuItemContent } from 'primeng/menu';
import { MenuItem, MessageService } from 'primeng/api';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { Graphql } from '../../application/Services/graphql';
import { User } from '../../Interface/user';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { filter, finalize, map } from 'rxjs';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { WebsocketService } from '../../application/Services/websocket-service';
import { FormsModule, ɵInternalFormsSharedModule } from '@angular/forms';
import { MarkdownComponent } from 'ngx-markdown';
import { FileUploadPythonService } from '../../application/Services/file-upload-python-service';
import { Toast } from 'primeng/toast';
import { ProgressBarModule } from 'primeng/progressbar';
import { HttpEventType } from '@angular/common/http';
import { ConversationMessage } from '../../Interface/Conversation-messages';

@Component({
  selector: 'app-aichat',
  imports: [
    ScrollPanelModule,
    SplitterModule,
    MenuModule,
    InputTextModule,
    MenuItemContent,
    IconFieldModule,
    InputIconModule,
    RouterLink,
    DialogModule,
    ButtonModule,
    ɵInternalFormsSharedModule,
    FormsModule,
    MarkdownComponent,
    Toast,
    ProgressBarModule,
  ],
  templateUrl: './aichat.html',
  styleUrl: './aichat.css',
  providers: [MessageService],
})
export class Aichat implements OnInit {
  messageService = inject(MessageService);
  visible = signal<boolean>(false);
  
  user = signal<User>(this.userdata);
  destroy = inject(DestroyRef);
  graphService = inject(Graphql);
  
  userid = computed(() => this.user()?.id);
  
  filesList = signal<any>([]);
  uploadProgress = signal<number>(0);

  localMessages = signal<any[]>([]);
  newMessage!: string;
  activeRoute = inject(ActivatedRoute);
  websocketService = inject(WebsocketService);
  FileUpload = inject(FileUploadPythonService);

  activeConvId = toSignal(
    this.activeRoute.queryParamMap.pipe(map((params) => params.get('convId'))),{ initialValue: null}
  );
  listMessages = computed<any>(() => {
    const data = this.allData();
    const activeId = this.activeConvId();
    const local = this.localMessages();
    let history = [];
    if (!data) return [];

    if (activeId) {
      history = data.find((c: any) => c.convId === activeId)?.messages || [];
    } else {
      history = data[data.length - 1]?.messages || [];
    }
    return [...history, ...local];
  });
  URL=computed(()=>`ws://127.0.0.1:8001/conversation/ws/${this.userid()}/${this.activeConvId()}`)
  // ... inside Aichat Component ...
private currentConnectedUrl = '';

constructor() {
  // Effect 1: Handle connection management cleanly when URL dependencies settle
  effect(() => {
    const id = this.activeConvId();
    const uId = this.userid();
    const url = this.URL(); 

    if (id && uId && url !== this.currentConnectedUrl) {
      console.log('Establishing connection for:', { userId: uId, convId: id });
      this.currentConnectedUrl = url;
      this.localMessages.set([]);
      this.websocketService.connect(url);
    }
  });

  // Effect 2: Watch connection status state change asynchronously
  effect(() => {
    const isConnected = this.websocketService.connectweb();
    if (isConnected) {
      // Use untracked just in case to avoid any potential side-effects cycles 
      untracked(() => this.showInfo("Connected to chat agent successfully"));
    }
  });
}
  private msgai=''
  
  ngOnInit(): void {

    

    this.websocketService.messages$.pipe(takeUntilDestroyed(this.destroy)).subscribe({
      next: (value) => {
      
        const type = value.type;
        const text = value.text;

        this.localMessages.update((prev) => {
          if (prev.length === 0) return prev;
          const messages = [...prev];
          const last = { ...messages[messages.length - 1] };

          if (type === 'tool') {
            last.message = text;
          } else if (type === 'message') {
            console.log(this.msgai);
            this.msgai += text;
            last.message = this.msgai;
          }

          messages[messages.length - 1] = last;
          return messages;
        });
      },
    });
  }
  onFileChange($event: any) {
    const files: FileList = $event.target?.files;
    if (files.length > 3) {
      this.showError('3 fichier max');
      return;
    }
    for (let f of files) {
      if (f.type !== 'application/pdf') {
        this.showError('pdf uniquement');
        return;
      }
    }
    this.filesList.set([files]);
    this.FileUpload.Upload(1, 1, files)
      .pipe(
        takeUntilDestroyed(this.destroy),
        finalize(() => this.reset()),
      )
      .subscribe((event: any) => {
        if (event.type == HttpEventType.UploadProgress) {
          this.uploadProgress.set(Math.round(100 * (event.loaded / event.total)));
        }
      });
  }
  reset(): void {
    this.uploadProgress.set(0);
    this.filesList.set([]);
    this.showInfo('files Uploaded');
  }
  showInfo(msg: string) {
    this.messageService.add({ severity: 'info', summary: 'Info', detail: msg });
  }
  showError(err: any) {
    this.messageService.add({ severity: 'error', summary: 'Error', detail: err });
  }
  Created(txt: string) {
    if (txt.trim() == '') {
      this.showError('pas de titre');
      return;
    }
    this.visible.set(false);
    this.graphService
      .createnewConv(this.userid(), txt)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (value) => {
          if (value) {
            this.showInfo('conversation created');
          }
        },
        error: (err) => {
          this.showError("il y'a un erreur");
        },
      });
  }
  showDialog() {
    this.visible.set(true);
  }
  get userdata() {
    const data = localStorage.getItem('user');

    return JSON.parse(data!);
  }

  allData = toSignal(
    this.graphService.getAllconv(this.userid()).pipe(
      filter((result) => !result.loading),
      map((res) => res.data?.allConvsByUserId),
    ),
  );

  items = computed<MenuItem[]>(() => {
    const dataconv = this.allData();
    console.log(dataconv);
    const menu: MenuItem[] = [
      {
        items: [
          {
            label: 'home',
            icon: 'pi pi-home',
             routerLink: '/aichat',
          },
          {
            label: 'new chat',
            icon: 'pi pi-plus',
            command: () => this.showDialog(),
          },
        ],
      },
    ];
    if (dataconv) {
      const historyitems: MenuItem[] = dataconv.map((conv ) => ({
        label: conv.name,
        icon: 'pi pi-comment',
        routerLink: '/aichat',
        queryParams: { convId: conv.convId },
      }));
      menu.push({
        label: 'Chat History',
        items: historyitems,
      });
    } else {
      menu.push({
        label: 'Chat History',
        items: [{ label: 'No history yet', disabled: true }],
      });
    }

    return menu;
  });

  sendMessage() {
    if(!this.websocketService.connectweb()){
      this.showInfo('we are connecting ,wait a few second')
      return
    }
    
    if (!this.newMessage) return;

    const msg = { text: this.newMessage };
    this.msgai=""
    this.websocketService.sendMessage(msg);

    this.localMessages.update((prev) => [
      ...prev,
      { role: 'HUMAN', message: this.newMessage },
      { role: 'AI', message: '' },
    ]);
    this.newMessage = '';

   
  }
}
