from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from torch.utils.data import DataLoader, Dataset

import app.state as state
from app.AI_Models.ImageClassifier import (
    CLIPClassifierV2,
    _checkpoint_class_names,
    _checkpoint_model_state,
    _normalize_clip_model_name,
)
from app.core.config import (
    ACTIVE_CLASSIFIER_MODEL_PATH,
    CLASSIFIER_INTERNAL_API_KEY,
    CLASSIFIER_MIN_IMAGES_PER_CLASS,
    CLASSIFIER_MODEL_DIR,
    DJANGO_URL,
)

try:
    import clip
except ImportError:  # pragma: no cover - handled by runtime environment
    clip = None


TERMINAL_STATUSES = {"succeeded", "failed"}


class ClassifierTrainingDataset(Dataset):
    def __init__(self, items: list[tuple[str, int]], preprocess):
        self.items = items
        self.preprocess = preprocess

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        path, label = self.items[index]
        image = Image.open(path).convert("RGB")
        return self.preprocess(image), label


def create_training_job(payload: dict[str, Any]) -> dict[str, Any]:
    with state.classifier_training_lock:
        current_job = state.classifier_training_job
        if current_job and current_job.get("status") not in TERMINAL_STATUSES:
            raise RuntimeError("A classifier training job is already running.")

        job_id = f"classifier-run-{payload['run_id']}-{uuid4().hex[:8]}"
        state.classifier_training_job = {
            "job_id": job_id,
            "run_id": payload["run_id"],
            "status": "queued",
            "created_at": _utc_now(),
        }
        return state.classifier_training_job.copy()


def run_training_job(job_id: str, payload: dict[str, Any]) -> None:
    _set_job_state(job_id, status="running", started_at=_utc_now())
    _notify_django(payload["run_id"], {"status": "running", "job_id": job_id})

    try:
        result = train_expanded_classifier(payload)
    except Exception as exc:  # pragma: no cover - exercised through integration
        error_message = str(exc)
        _set_job_state(job_id, status="failed", error_message=error_message, finished_at=_utc_now())
        _notify_django(
            payload["run_id"],
            {
                "status": "failed",
                "job_id": job_id,
                "error_message": error_message,
            },
        )
        return

    _set_job_state(
        job_id,
        status="succeeded",
        finished_at=_utc_now(),
        checkpoint_path=result["checkpoint_path"],
        metrics=result["metrics"],
        version=result["version"],
    )
    _notify_django(
        payload["run_id"],
        {
            "status": "succeeded",
            "job_id": job_id,
            "checkpoint_path": result["checkpoint_path"],
            "class_names": result["class_names"],
            "metrics": result["metrics"],
            "version": result["version"],
        },
    )


def get_training_job(job_id: str) -> dict[str, Any] | None:
    current_job = state.classifier_training_job
    if current_job and current_job.get("job_id") == job_id:
        return current_job.copy()
    return None


def train_expanded_classifier(payload: dict[str, Any]) -> dict[str, Any]:
    if clip is None:
        raise RuntimeError("The CLIP package is not installed in the model server environment.")

    base_checkpoint_path = payload.get("base_checkpoint_path") or ACTIVE_CLASSIFIER_MODEL_PATH
    base_checkpoint = torch.load(base_checkpoint_path, map_location="cpu")
    base_class_names = list(_checkpoint_class_names(base_checkpoint))
    base_state = _checkpoint_model_state(base_checkpoint)
    if not base_class_names or base_state is None:
        raise ValueError("Base checkpoint must include class names and model weights.")

    new_class_names = [item["name"] for item in payload["classes"] if item["name"] not in base_class_names]
    if not new_class_names:
        raise ValueError("Training request does not include any new class names.")

    for class_payload in payload["classes"]:
        image_paths = class_payload.get("image_paths") or []
        if len(image_paths) < CLASSIFIER_MIN_IMAGES_PER_CLASS:
            raise ValueError(
                f"Class '{class_payload['name']}' needs at least "
                f"{CLASSIFIER_MIN_IMAGES_PER_CLASS} images."
            )
        missing_paths = [path for path in image_paths if not Path(path).exists()]
        if missing_paths:
            raise FileNotFoundError(f"Missing training images: {missing_paths[:3]}")

    expanded_class_names = base_class_names + new_class_names
    class_to_index = {name: index for index, name in enumerate(expanded_class_names)}

    device = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model_name = _normalize_clip_model_name(base_checkpoint.get("clip_model"))
    clip_model, preprocess = clip.load(clip_model_name, device=device)
    embed_dim = getattr(clip_model.visual, "output_dim", 768)
    model = CLIPClassifierV2(
        clip_model=clip_model,
        num_classes=len(expanded_class_names),
        embed_dim=embed_dim,
        unfreeze_layers=0,
    ).to(device)
    _load_expanded_state(model, base_state, len(base_class_names))
    _freeze_all_but_new_classifier_rows(model, len(base_class_names))

    train_items, val_items = _build_train_val_items(payload["classes"], class_to_index)
    train_loader = DataLoader(
        ClassifierTrainingDataset(train_items, preprocess),
        batch_size=int(payload.get("config", {}).get("batch_size", 4)),
        shuffle=True,
        num_workers=0,
    )
    val_loader = DataLoader(
        ClassifierTrainingDataset(val_items, preprocess),
        batch_size=int(payload.get("config", {}).get("batch_size", 4)),
        shuffle=False,
        num_workers=0,
    )

    epochs = int(payload.get("config", {}).get("epochs", 8))
    learning_rate = float(payload.get("config", {}).get("lr", 1e-3))
    optimizer = optim.Adam(
        [param for param in model.parameters() if param.requires_grad],
        lr=learning_rate,
    )
    criterion = nn.CrossEntropyLoss()

    history = []
    best_val_accuracy = 0.0
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        val_accuracy = _evaluate_accuracy(model, val_loader, device)
        best_val_accuracy = max(best_val_accuracy, val_accuracy)
        history.append(
            {
                "epoch": epoch + 1,
                "loss": total_loss / max(len(train_loader), 1),
                "val_accuracy": val_accuracy,
            }
        )

    version = f"classifier-run-{payload['run_id']}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    output_dir = Path(CLASSIFIER_MODEL_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / f"{version}.pth"
    metrics = {
        "best_val_accuracy": best_val_accuracy,
        "epochs": len(history),
        "history": history,
        "new_classes": new_class_names,
        "total_classes": len(expanded_class_names),
    }

    torch.save(
        {
            "schema_version": 2,
            "version": version,
            "model_version": version,
            "model_state_dict": model.state_dict(),
            "class_names": expanded_class_names,
            "clip_model": clip_model_name,
            "base_checkpoint_path": str(base_checkpoint_path),
            "base_model_version_id": payload.get("base_model_version_id"),
            "training_config": payload.get("config", {}),
            "metrics": metrics,
        },
        checkpoint_path,
    )

    return {
        "version": version,
        "checkpoint_path": str(checkpoint_path),
        "class_names": expanded_class_names,
        "metrics": metrics,
    }


def _load_expanded_state(model: CLIPClassifierV2, base_state: dict, old_class_count: int) -> None:
    expanded_state = model.state_dict()
    for key, value in base_state.items():
        if key in expanded_state and expanded_state[key].shape == value.shape:
            expanded_state[key] = value.to(expanded_state[key].device)

    final_weight_key = "classifier.5.weight"
    final_bias_key = "classifier.5.bias"
    if final_weight_key in base_state and final_weight_key in expanded_state:
        expanded_state[final_weight_key][:old_class_count] = base_state[final_weight_key].to(
            expanded_state[final_weight_key].device
        )
    if final_bias_key in base_state and final_bias_key in expanded_state:
        expanded_state[final_bias_key][:old_class_count] = base_state[final_bias_key].to(
            expanded_state[final_bias_key].device
        )

    model.load_state_dict(expanded_state)


def _freeze_all_but_new_classifier_rows(model: CLIPClassifierV2, old_class_count: int) -> None:
    for parameter in model.parameters():
        parameter.requires_grad = False

    final_layer = model.classifier[-1]
    final_layer.weight.requires_grad = True
    final_layer.bias.requires_grad = True

    def zero_old_weight_rows(gradient):
        gradient = gradient.clone()
        gradient[:old_class_count] = 0
        return gradient

    def zero_old_bias_rows(gradient):
        gradient = gradient.clone()
        gradient[:old_class_count] = 0
        return gradient

    final_layer.weight.register_hook(zero_old_weight_rows)
    final_layer.bias.register_hook(zero_old_bias_rows)


def _build_train_val_items(
    classes: list[dict[str, Any]],
    class_to_index: dict[str, int],
) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    train_items = []
    val_items = []

    for class_payload in classes:
        label = class_to_index[class_payload["name"]]
        paths = sorted(class_payload["image_paths"])
        val_count = max(1, int(len(paths) * 0.2))
        val_paths = paths[:val_count]
        train_paths = paths[val_count:]
        train_items.extend((path, label) for path in train_paths)
        val_items.extend((path, label) for path in val_paths)

    return train_items, val_items


@torch.no_grad()
def _evaluate_accuracy(model: CLIPClassifierV2, data_loader: DataLoader, device: str) -> float:
    model.eval()
    correct = 0
    total = 0
    for images, labels in data_loader:
        images = images.to(device)
        labels = labels.to(device)
        logits = model(images)
        predictions = logits.argmax(dim=1)
        correct += predictions.eq(labels).sum().item()
        total += labels.size(0)
    return 100.0 * correct / total if total else 0.0


def _set_job_state(job_id: str, **updates) -> None:
    with state.classifier_training_lock:
        if not state.classifier_training_job or state.classifier_training_job.get("job_id") != job_id:
            return
        state.classifier_training_job.update(updates)


def _notify_django(run_id: int, payload: dict[str, Any]) -> None:
    url = f"{DJANGO_URL.rstrip('/')}/api/classifier/internal/training-runs/{run_id}/status/"
    try:
        with httpx.Client(timeout=10) as client:
            client.post(
                url,
                json=payload,
                headers={"X-Internal-API-Key": CLASSIFIER_INTERNAL_API_KEY},
            )
    except httpx.HTTPError as exc:
        print(f"Failed to notify Django about classifier training run {run_id}: {exc}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
