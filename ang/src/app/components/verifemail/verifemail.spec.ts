import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Verifemail } from './verifemail';

describe('Verifemail', () => {
  let component: Verifemail;
  let fixture: ComponentFixture<Verifemail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Verifemail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Verifemail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
