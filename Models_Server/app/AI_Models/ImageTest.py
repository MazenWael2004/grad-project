import torch
from ImageClassifier import load_model, predict_image
from PIL import Image
model, preprocess, class_names, device = load_model("app/AI_Models/clip_classifier_v2.pth")
print(f"using device: {device}")
image = Image.open("app/AI_Models/test.jpeg").convert("RGB")
prediction, confidence, probs = predict_image(model, preprocess, class_names, device, image)
print(f"Prediction: {prediction}")
print(f"Confidence: {confidence * 100:.2f}%")

# Optional: print top 5 predictions
top_probs, top_indices = torch.topk(probs, 5)

print("\nTop 5 predictions:")
for p, idx in zip(top_probs[0], top_indices[0]):
    print(f"{class_names[idx.item()]:20} {p.item()*100:.2f}%")
