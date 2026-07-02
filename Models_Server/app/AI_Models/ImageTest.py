from ImageClassifier import load_model, predict_image, predict_top_k
from PIL import Image

image_classifier = load_model("app/AI_Models/clip_classifier_v2.pth")
print(f"using device: {image_classifier.device}")
image = Image.open("app/AI_Models/test.jpeg").convert("RGB")
prediction, confidence, probs = predict_image(image_classifier, image)
print(f"Prediction: {prediction}")
print(f"Confidence: {confidence * 100:.2f}%")

# Optional: print top 5 predictions
predictions, _ = predict_top_k(image_classifier, image, top_k=5)

print("\nTop 5 predictions:")
for item in predictions:
    print(f"{item['label']:20} {item['confidence'] * 100:.2f}%")
