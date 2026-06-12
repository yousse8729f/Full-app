import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Uir } from './uir';

describe('Uir', () => {
  let component: Uir;
  let fixture: ComponentFixture<Uir>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Uir]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Uir);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
