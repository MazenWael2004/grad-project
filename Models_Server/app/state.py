from app.AI_Models.ImageClassifier import ImageClassifier
import threading


image_classifier: ImageClassifier | None = None
classifier_training_lock = threading.Lock()
classifier_training_job: dict | None = None
