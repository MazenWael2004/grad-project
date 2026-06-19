import torch
import open_clip
from PIL import Image
from model import CLIPClassifierV2


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "clip_classifier_v2.pth"



device = "cuda" if torch.cuda.is_available() else "cpu"


checkpoint = torch.load(MODEL_PATH, map_location=device)

class_names = checkpoint["class_names"]
clip_model_name = checkpoint["clip_model"]


clip_model, _, preprocess = open_clip.create_model_and_transforms(
    clip_model_name,
    pretrained="openai"
)
clip_model = clip_model.to(device)

embed_dim = clip_model.visual.output_dim
num_classes = len(class_names)


model = CLIPClassifierV2(clip_model, num_classes, embed_dim).to(device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()


def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    img = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(img)
        probs = logits.softmax(dim=-1)[0]

    topk = torch.topk(probs, 5)

    results = []
    for p, idx in zip(topk.values, topk.indices):
        results.append((class_names[idx], float(p) * 100))

    return results