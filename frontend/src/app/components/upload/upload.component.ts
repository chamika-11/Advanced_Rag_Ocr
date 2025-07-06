// src/app/components/upload/upload.component.ts
import { Component } from '@angular/core';
import { DocumentService, DocumentResult } from '../../services/document.service';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  selectedFiles: File[] = [];
  documentType: string = '';
  isUploading: boolean = false;
  uploadResults: DocumentResult[] = [];
  message: string = '';

  constructor(private documentService: DocumentService) {}

  onFileSelect(event: any) {
    const files = event.target.files;
    this.selectedFiles = Array.from(files);
  }

  onDragOver(event: any) {
    event.preventDefault();
    event.stopPropagation();
  }

  onDragLeave(event: any) {
    event.preventDefault();
    event.stopPropagation();
  }

  onDrop(event: any) {
    event.preventDefault();
    event.stopPropagation();
    
    const files = event.dataTransfer.files;
    this.selectedFiles = Array.from(files);
  }

  removeFile(index: number) {
    this.selectedFiles.splice(index, 1);
  }

  uploadDocuments() {
    if (this.selectedFiles.length === 0 || !this.documentType) {
      alert('Please select files and document type');
      return;
    }

    this.isUploading = true;
    this.message = '';
    this.uploadResults = [];

    this.documentService.uploadDocuments(this.selectedFiles, this.documentType)
      .subscribe({
        next: (response) => {
          this.message = response.message;
          this.uploadResults = response.results;
          this.isUploading = false;
          
          // Reset form
          this.selectedFiles = [];
          this.documentType = '';
        },
        error: (error) => {
          console.error('Upload failed:', error);
          this.message = 'Upload failed. Please try again.';
          this.isUploading = false;
        }
      });
  }

  getFileSize(file: File): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (file.size === 0) return '0 Bytes';
    const i = Math.floor(Math.log(file.size) / Math.log(1024));
    return Math.round(file.size / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
}