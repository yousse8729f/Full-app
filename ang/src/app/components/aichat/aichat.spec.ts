import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Aichat } from './aichat';

describe('Aichat', () => {
  let component: Aichat;
  let fixture: ComponentFixture<Aichat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Aichat]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Aichat);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
