// src/app/services/document.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DocumentResult {
  file: string;
  document_type: string;
  structured_data: any;
}

export interface UploadResponse {
  message: string;
  results: DocumentResult[];
}

export interface ChatResponse {
  answer: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private apiUrl = 'http://localhost:8000'; // Your FastAPI backend URL

  constructor(private http: HttpClient) {}

  uploadDocuments(files: File[], documentType: string): Observable<UploadResponse> {
    const formData = new FormData();
    
    // Append all files
    files.forEach(file => {
      formData.append('files', file);
    });
    
    // Append document type
    formData.append('document_type', documentType);

    return this.http.post<UploadResponse>(`${this.apiUrl}/upload-document/`, formData);
  }

  askQuestion(question: string): Observable<ChatResponse> {
    const formData = new FormData();
    formData.append('question', question);

    return this.http.post<ChatResponse>(`${this.apiUrl}/chat/`, formData);
  }
}