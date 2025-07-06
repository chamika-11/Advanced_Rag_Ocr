import { Component, Inject } from '@angular/core';
import { ApiService } from '../../services/api';
@Component({
  selector: 'app-upload',
  templateUrl: './upload.html',
  providers: [ApiService]
})
export class UploadComponent {
  selectedFiles: File[] = [];
  documentType = '';
  result: any;

  constructor(@Inject(ApiService) private apiService: ApiService) {}

  onFileChange(event: any) {
    this.selectedFiles = Array.from(event.target.files);
  }

  upload() {
    this.apiService.uploadDocuments(this.selectedFiles, this.documentType)
      .subscribe((res: any) => this.result = res, (err: any) => console.error(err));
  }
}
