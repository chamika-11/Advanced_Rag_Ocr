import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentChat } from './document-chat';

describe('DocumentChat', () => {
  let component: DocumentChat;
  let fixture: ComponentFixture<DocumentChat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DocumentChat]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DocumentChat);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
