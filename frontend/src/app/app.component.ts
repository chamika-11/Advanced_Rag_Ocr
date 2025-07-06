import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OcrService } from './ocr.service';
import { UploadComponent } from "./components/upload/upload";
import { ChatComponent } from "./document-chat/document-chat";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, UploadComponent, ChatComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  files: File[] = [];
  documentType = '';
  uploadResult: any;
  question = '';
  answer = '';

  constructor(private ocrService: OcrService) {}

  onFileChange(event: any) {
    this.files = Array.from(event.target.files);
  }

  upload() {
    this.ocrService.uploadDocument(this.files, this.documentType).subscribe(res => {
      this.uploadResult = res;
    });
  }

  ask() {
    this.ocrService.chat(this.question).subscribe(res => {
      this.answer = res.answer;
    });
  }
}
