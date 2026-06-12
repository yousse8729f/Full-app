import { TestBed } from '@angular/core/testing';

import { Graphql } from './graphql';

describe('Graphql', () => {
  let service: Graphql;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Graphql);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
