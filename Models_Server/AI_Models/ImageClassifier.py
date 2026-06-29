from PIL import Image
import torch
import torch.nn as nn
import clip


# Model architecture (must match training)
class CLIPClassifierV2(nn.Module):
    def __init__(self, clip_model, num_classes, embed_dim, unfreeze_layers=4):
        super().__init__()
        self.visual = clip_model.visual

        # Freeze all layers first
        for param in self.visual.parameters():
            param.requires_grad = False

        # Unfreeze last N transformer blocks
        if hasattr(self.visual, "transformer"):
            num_blocks = len(self.visual.transformer.resblocks)
            for i in range(num_blocks - unfreeze_layers, num_blocks):
                for param in self.visual.transformer.resblocks[i].parameters():
                    param.requires_grad = True

        # Always unfreeze final layers
        for name, param in self.visual.named_parameters():
            if any(x in name for x in ["ln_post", "proj"]):
                param.requires_grad = True

        # Trainable classification head
        self.classifier = nn.Sequential(
            nn.LayerNorm(embed_dim),
            nn.Dropout(0.2),
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(embed_dim // 2, num_classes),
        )

    def forward(self, images):
        features = self.visual(images)
        features = features / features.norm(dim=-1, keepdim=True)
        return self.classifier(features)


def load_model(model_path="AI_Models/clip_classifier_v2.pth"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Load checkpoint
    checkpoint = torch.load(
        model_path,
        map_location=device,
    )

    class_names = checkpoint["class_names"]
    num_classes = len(class_names)

    clip_model, preprocess = clip.load(
        "ViT-L/14",
        device=device,
    )

    # Recreate classifier
    model = CLIPClassifierV2(
        clip_model=clip_model,
        num_classes=num_classes,
        embed_dim=768,  # ViT-L/14 embedding size
        unfreeze_layers=4,
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    model.float()
    return model, preprocess, class_names, device


def predict_image(model, preprocess, class_names, device, image_path):
    image = preprocess(Image.open("AI_Models/test.jpeg").convert("RGB"))
    image = image.unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(image)
        probs = torch.softmax(logits, dim=1)
    confidence, pred = torch.max(probs, dim=1)
    predicted_class = class_names[pred.item()]
    return predicted_class, confidence.item(), probs
