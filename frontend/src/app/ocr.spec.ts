import { TestBed } from '@angular/core/testing';

import { Ocr } from './ocr';

describe('Ocr', () => {
  let service: Ocr;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Ocr);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
