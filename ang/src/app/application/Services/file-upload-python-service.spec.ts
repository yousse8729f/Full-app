import { TestBed } from '@angular/core/testing';

import { FileUploadPythonService } from '../file-upload-python-service';

describe('FileUploadPythonService', () => {
  let service: FileUploadPythonService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FileUploadPythonService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
