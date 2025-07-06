import { Component } from '@angular/core';
import { ApiService } from '../services/api';

@Component({
  selector: 'app-chat',
  templateUrl: './document-chat.html'
})
export class ChatComponent {
  question = '';
  answer = '';

  constructor(private apiService: ApiService) {}

  ask() {
    this.apiService.askQuestion(this.question)
      .subscribe(res => this.answer = res.answer, err => console.error(err));
  }
}
