from PIL import Image 
import torch
import torchvision
import torchvision.transforms as transforms
from torch import nn, optim
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, random_split
import os

def train_document_classifier(data_dir="data/classification", save_path='models/doc_classifier.pth'):
    
    if os.path.exists(save_path):
        print(f"Model already exists as {save_path}. Skipping training")
        return
    
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(degrees=10), 
        transforms.RandomHorizontalFlip(p=0.3), 
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)), 
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])
    
    # Validation transform without augmentation
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])
    
    # Load dataset and split into train/validation
    full_dataset = ImageFolder(data_dir, transform=train_transform)
    num_classes = len(full_dataset.classes)
    print(f"Found {len(full_dataset)} images across {num_classes} classes: {full_dataset.classes}")
    
    # Split dataset (80% train, 20% validation)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    # Apply validation transform to validation set
    val_dataset.dataset.transform = val_transform
    
    # Smaller batch size for small dataset
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False, num_workers=2)
    
    print(f"Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")

    # Simplified model architecture for small dataset
    model = nn.Sequential(
        # First conv block
        nn.Conv2d(1, 16, kernel_size=3, padding=1),
        nn.BatchNorm2d(16),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Dropout2d(0.1),
        
        # Second conv block
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.BatchNorm2d(32),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Dropout2d(0.15),
        
        # Third conv block
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Dropout2d(0.2),
        
        # Classifier
        nn.Flatten(),
        nn.Linear(64 * 28 * 28, 128),  
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(64, num_classes)
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    # Training loop with validation
    best_val_acc = 0.0
    patience = 15
    no_improve_count = 0
    
    for epoch in range(50):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for images, labels in train_loader:
            outputs = model(images)
            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        # Calculate metrics
        train_acc = 100 * train_correct / train_total
        val_acc = 100 * val_correct / val_total
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        
        print(f"Epoch {epoch+1:2d}: "
              f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model and early stopping
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'classes': full_dataset.classes,
                'epoch': epoch,
                'val_acc': val_acc
            }, save_path)
            no_improve_count = 0
        else:
            no_improve_count += 1
            
        if no_improve_count >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break
            
        scheduler.step()

    print(f"Training completed. Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to {save_path}")


def predict_document_type(image_path, model_path='models/doc_classifier.pth'):
    # Load model and classes
    checkpoint = torch.load(model_path)
    class_labels = checkpoint['classes']
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])
    
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)

    # Recreate model architecture (should match training)
    num_classes = len(class_labels)
    model = nn.Sequential(
        nn.Conv2d(1, 16, kernel_size=3, padding=1),
        nn.BatchNorm2d(16),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Dropout2d(0.1),
        
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.BatchNorm2d(32),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Dropout2d(0.15),
        
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Dropout2d(0.2),
        
        nn.Flatten(),
        nn.Linear(64 * 28 * 28, 128),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(64, num_classes)
    )

    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    predicted_class = class_labels[predicted.item()]
    confidence_score = confidence.item()
    
    return predicted_class, confidence_score


# Example usage
if __name__ == "__main__":
    # Train the model
    train_document_classifier()
    