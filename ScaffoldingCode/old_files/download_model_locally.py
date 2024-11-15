import torch
torch.hub.set_dir('./models')
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
