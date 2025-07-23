from PIL import Image 
import torch
import torchvision
import torchvision.transforms as transforms
from torch import nn,optim
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import os

def train_document_classifier(data_dir="data/classification", save_path='models/doc_classifier.pth'):
    
    if os.path.exists(save_path):
        print(f"Model already exists as {save_path}.Skipping training")
        return
    
    transform=transforms.Compose([
        transforms.Resize((224,224)),  # Increased from 128x128
        transforms.RandomRotation(degrees=5),  # Data augmentation
        transforms.ColorJitter(brightness=0.2, contrast=0.2),  # More augmentation
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])  # Added normalization
    ])

    dataset=ImageFolder(data_dir,transform=transform)
    dataloader=DataLoader(dataset,batch_size=32,shuffle=True)  # Increased batch size from 8
    num_classes=len(dataset.classes)

    model = nn.Sequential(
        nn.Conv2d(1, 32, kernel_size=3, padding=1),  # Increased from 16 to 32
        nn.BatchNorm2d(32),  # Added batch normalization
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, kernel_size=3, padding=1),  # Increased from 32 to 64
        nn.BatchNorm2d(64),  # Added batch normalization
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, kernel_size=3, padding=1),  # Added third conv layer
        nn.BatchNorm2d(128),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(128 * 28 * 28, 512),  # Adjusted for 224x224 input and added layer
        nn.ReLU(),
        nn.Dropout(0.5),  # Added dropout
        nn.Linear(512, 256),  # Added intermediate layer
        nn.ReLU(),
        nn.Dropout(0.3),  # Added dropout
        nn.Linear(256, num_classes)
    )

    criterion=nn.CrossEntropyLoss()
    optimizer=optim.Adam(model.parameters(),lr=0.0001)  # Reduced learning rate from 0.001

    #training loop
    for epoch in range(20): 
        for images,labels in dataloader:
            outputs=model(images)
            loss=criterion(outputs,labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch+1}: loss={loss.item()}")

    torch.save(model.state_dict(),save_path)
    print(f"Model saved, path of {save_path}")




#predict with the model
def predict_document_type(image_path, model_path='models/doc_classifier.pth', class_labels=None):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Increased from 128x128 to match training
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])  # Added normalization to match training
    ])
    
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)

    model = nn.Sequential(
        nn.Conv2d(1, 32, kernel_size=3, padding=1),  # Increased from 16 to 32
        nn.BatchNorm2d(32),  # Added batch normalization
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, kernel_size=3, padding=1),  # Increased from 32 to 64
        nn.BatchNorm2d(64),  # Added batch normalization
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, kernel_size=3, padding=1),  # Added third conv layer
        nn.BatchNorm2d(128),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(128 * 28 * 28, 512),  # Adjusted for 224x224 input and added layer
        nn.ReLU(),
        nn.Dropout(0.5),  # Added dropout
        nn.Linear(512, 256),  # Added intermediate layer
        nn.ReLU(),
        nn.Dropout(0.3),  # Added dropout
        nn.Linear(256, len(class_labels))
    )

    model.load_state_dict(torch.load(model_path))
    model.eval()

    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return class_labels[predicted.item()]