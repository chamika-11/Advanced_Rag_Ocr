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
        transforms.Resize((224,224)), 
        transforms.RandomRotation(degrees=5),  
        transforms.ColorJitter(brightness=0.2, contrast=0.2),  
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])  
    ])

    dataset=ImageFolder(data_dir,transform=transform)
    dataloader=DataLoader(dataset,batch_size=32,shuffle=True)  
    num_classes=len(dataset.classes)

    model = nn.Sequential(
        nn.Conv2d(1, 32, kernel_size=3, padding=1),  
        nn.BatchNorm2d(32),  
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, kernel_size=3, padding=1), 
        nn.BatchNorm2d(128),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(128 * 28 * 28, 512), 
        nn.ReLU(),
        nn.Dropout(0.5), 
        nn.Linear(512, 256), 
        nn.ReLU(),
        nn.Dropout(0.3),  
        nn.Linear(256, num_classes)
    )

    criterion=nn.CrossEntropyLoss()
    optimizer=optim.Adam(model.parameters(),lr=0.0001) 

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
        transforms.Resize((224, 224)),  
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]) 
    ])
    
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)

    model = nn.Sequential(
        nn.Conv2d(1, 32, kernel_size=3, padding=1),  
        nn.BatchNorm2d(32),  
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, kernel_size=3, padding=1), 
        nn.BatchNorm2d(64),  
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, kernel_size=3, padding=1),  
        nn.BatchNorm2d(128),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(128 * 28 * 28, 512),  
        nn.ReLU(),
        nn.Dropout(0.5),  
        nn.Linear(512, 256),  
        nn.ReLU(),
        nn.Dropout(0.3), 
        nn.Linear(256, len(class_labels))
    )

    model.load_state_dict(torch.load(model_path))
    model.eval()

    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return class_labels[predicted.item()]