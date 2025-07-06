// src/app/components/chat/chat.component.ts
import { Component } from '@angular/core';
import { DocumentService } from '../../services/document.service';

interface ChatMessage {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  messages: ChatMessage[] = [];
  currentQuestion: string = '';
  isLoading: boolean = false;

  constructor(private documentService: DocumentService) {
    // Add welcome message
    this.messages.push({
      text: 'Hello! I can help you search and answer questions about your uploaded documents. What would you like to know?',
      isUser: false,
      timestamp: new Date()
    });
  }

  askQuestion() {
    if (!this.currentQuestion.trim()) {
      return;
    }

    // Add user message
    this.messages.push({
      text: this.currentQuestion,
      isUser: true,
      timestamp: new Date()
    });

    const question = this.currentQuestion;
    this.currentQuestion = '';
    this.isLoading = true;

    this.documentService.askQuestion(question).subscribe({
      next: (response) => {
        this.messages.push({
          text: response.answer,
          isUser: false,
          timestamp: new Date()
        });
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Chat error:', error);
        this.messages.push({
          text: 'Sorry, I encountered an error while processing your question. Please try again.',
          isUser: false,
          timestamp: new Date()
        });
        this.isLoading = false;
      }
    });
  }

  onKeyPress(event: any) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.askQuestion();
    }
  }

  clearChat() {
    this.messages = [{
      text: 'Hello! I can help you search and answer questions about your uploaded documents. What would you like to know?',
      isUser: false,
      timestamp: new Date()
    }];
  }
}