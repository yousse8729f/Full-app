import { Component, ElementRef, viewChild, effect } from '@angular/core';
import { gsap } from "gsap";
@Component({
  selector: 'app-uir',
  imports: [],
  templateUrl: './uir.html',
  styleUrl: './uir.css',
})
export class Uir {
private cuve = viewChild<ElementRef<SVGPathElement>>('l')
  private cir = viewChild<ElementRef<SVGCircleElement>>('c')
  constructor(){
    effect(()=>{
      const rawCu = this.cuve()?.nativeElement
      const rawcir = this.cir()?.nativeElement
      if (!rawCu || !rawcir) return
      // gsap.to(rawCu,{
      //   x:500,
      //   y:300,
        
      // })
    })
  }
}
