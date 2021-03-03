import { Component, OnInit } from '@angular/core';
import tsrData from '../assets/tsr_crunch_data.json';

export interface Card {
  name: string;
  image: string;
}
export interface Gap {
  gap: number;
  cards: Card[];
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title : string = 'TimeSpiralRemasteredNumberCrunch';
  in: Card[] = [];
  out : Card[] = [];
  possible : Gap[] = [];
  tableColumns : string[] = ['name','image'];

  ngOnInit() : void {
    this.in = tsrData.in as Card[];
    this.out = tsrData.out as Card[];
    this.possible = tsrData.possible as Gap[];

  }
}
