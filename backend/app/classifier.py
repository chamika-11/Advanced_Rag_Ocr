#build a model to classify scanned documents into types using image based features
from PIL import Image 
import torch
import torchvision
import torchvision.transforms as transforms
from torch import nn,optim
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

def train_document_classifier(data_dir="data/classification", save_path='models/doc_classifier.pth'):
    transform=transforms.Compose([
        transforms.Resize((128,128)),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor()
    ])

    dataset=ImageFolder(data_dir,transform=transform)
    dataloader=DataLoader(dataset,batch_size=8,shuffle=True)
    num_classes=len(dataset.classes)

    model = nn.Sequential(
        nn.Conv2d(1, 16, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(32 * 32 * 32, 100),
        nn.ReLU(),
        nn.Linear(100, num_classes)
    )

    criterion=nn.CrossEntropyLoss()
    optimizer=optim.Adam(model.parameters(),lr=0.001)

    #training loop
    for epoch in range(8):
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
        transforms.Resize((128, 128)),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor()
    ])
    
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)

    model = nn.Sequential(
        nn.Conv2d(1, 16, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(32 * 32 * 32, 100),
        nn.ReLU(),
        nn.Linear(100, len(class_labels))
    )

    model.load_state_dict(torch.load(model_path))
    model.eval()

    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return class_labels[predicted.item()]

