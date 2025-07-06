import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class OcrService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  uploadDocument(files: File[], documentType: string): Observable<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('document_type', documentType);
    return this.http.post(`${this.apiUrl}/upload-document/`, formData);
  }

  chat(question: string): Observable<any> {
    const formData = new FormData();
    formData.append('question', question);
    return this.http.post(`${this.apiUrl}/chat/`, formData);
  }
}
