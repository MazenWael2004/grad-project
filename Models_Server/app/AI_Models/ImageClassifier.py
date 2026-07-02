from PIL import Image
import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import Any

from app.core.config import ACTIVE_CLASSIFIER_MODEL_PATH

try:
    import clip
except ImportError:  # pragma: no cover - depends on runtime model environment
    clip = None


@dataclass
class ImageClassifier:
    model: Any
    preprocess: Any
    class_names: list[str]
    device: str
    checkpoint_path: str
    model_version: str | None = None


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


def _checkpoint_model_state(checkpoint: dict):
    return checkpoint.get("model_state_dict") or checkpoint.get("model")


def _checkpoint_class_names(checkpoint: dict):
    return checkpoint.get("class_names") or checkpoint.get("classes") or []


def _normalize_clip_model_name(name: str | None) -> str:
    if not name:
        return "ViT-L/14"
    if name == "ViT-L-14":
        return "ViT-L/14"
    return name


def load_model(model_path: str | None = None, model_version: str | None = None):
    if clip is None:
        raise RuntimeError("The CLIP package is not installed in the model server environment.")

    model_path = model_path or ACTIVE_CLASSIFIER_MODEL_PATH
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Load checkpoint
    checkpoint = torch.load(
        model_path,
        map_location=device,
    )

    class_names = _checkpoint_class_names(checkpoint)
    num_classes = len(class_names)
    model_state = _checkpoint_model_state(checkpoint)
    if not class_names or model_state is None:
        raise ValueError("Classifier checkpoint must include class_names and model_state_dict.")

    clip_model_name = _normalize_clip_model_name(checkpoint.get("clip_model"))
    clip_model, preprocess = clip.load(
        clip_model_name,
        device=device,
    )
    embed_dim = getattr(clip_model.visual, "output_dim", 768)

    # Recreate classifier
    model = CLIPClassifierV2(
        clip_model=clip_model,
        num_classes=num_classes,
        embed_dim=embed_dim,
        unfreeze_layers=4,
    ).to(device)
    model.load_state_dict(model_state)
    model.eval()
    model.float()
    image_classifier = ImageClassifier(
        model=model,
        preprocess=preprocess,
        class_names=class_names,
        device=device,
        checkpoint_path=str(model_path),
        model_version=model_version or checkpoint.get("model_version") or checkpoint.get("version"),
    )
    return image_classifier


def predict_top_k(image_classifier: ImageClassifier, image: Image.Image, top_k: int = 5):
    image = image_classifier.preprocess(image)
    image = image.unsqueeze(0).to(image_classifier.device)
    with torch.no_grad():
        logits = image_classifier.model(image)
        probs = torch.softmax(logits, dim=1)
    values, indices = torch.topk(probs[0], k=min(top_k, len(image_classifier.class_names)))
    return [
        {
            "label": image_classifier.class_names[index.item()],
            "confidence": value.item(),
        }
        for value, index in zip(values, indices)
    ], probs


def predict_image(image_classifier: ImageClassifier, image: Image.Image):
    predictions, probs = predict_top_k(image_classifier, image, top_k=1)
    best_prediction = predictions[0]
    return best_prediction["label"], best_prediction["confidence"], probs
