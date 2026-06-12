import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MarqueeI } from './marquee-i';

describe('MarqueeI', () => {
  let component: MarqueeI;
  let fixture: ComponentFixture<MarqueeI>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MarqueeI]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MarqueeI);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
