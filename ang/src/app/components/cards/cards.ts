import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
@Component({
  selector: 'app-cards',
  imports: [MatCardModule,MatIconModule],
  templateUrl: './cards.html',
  styleUrl: './cards.css',
})
export class Cards {

}
