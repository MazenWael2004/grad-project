from inference import predict

results = predict(
    r"D:\graduation_project\grad-project\backend\image_model\download.jpg"
)

print("\nTop predictions:")
for name, prob in results:
    print(name, f"{prob:.2f}%")