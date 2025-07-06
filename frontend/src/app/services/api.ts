import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000'; // FastAPI running locally

  constructor(private http: HttpClient) {}

  uploadDocuments(files: File[], documentType: string): Observable<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('document_type', documentType);

    return this.http.post(`${this.baseUrl}/upload-document/`, formData);
  }

  askQuestion(question: string): Observable<any> {
    const formData = new FormData();
    formData.append('question', question);

    return this.http.post(`${this.baseUrl}/chat/`, formData);
  }
}
