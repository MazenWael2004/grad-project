import unittest

import torch
import torch.nn as nn

import app.state as state
from app.services.classifier_training import (
    _freeze_all_but_new_classifier_rows,
    _load_expanded_state,
    create_training_job,
)


class DummyExpandedClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.LayerNorm(4),
            nn.Dropout(0.0),
            nn.Linear(4, 2),
            nn.GELU(),
            nn.Dropout(0.0),
            nn.Linear(2, 3),
        )


class ClassifierTrainingServiceTests(unittest.TestCase):
    def setUp(self):
        state.classifier_training_job = None

    def test_create_training_job_rejects_concurrent_job(self):
        first_job = create_training_job({"run_id": 1})

        self.assertEqual(first_job["status"], "queued")
        with self.assertRaises(RuntimeError):
            create_training_job({"run_id": 2})

    def test_load_expanded_state_copies_old_classifier_rows(self):
        model = DummyExpandedClassifier()
        old_weight = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        old_bias = torch.tensor([0.5, 0.75])
        base_state = {
            "classifier.5.weight": old_weight,
            "classifier.5.bias": old_bias,
        }

        _load_expanded_state(model, base_state, old_class_count=2)

        self.assertTrue(torch.equal(model.classifier[-1].weight[:2].detach(), old_weight))
        self.assertTrue(torch.equal(model.classifier[-1].bias[:2].detach(), old_bias))

    def test_freeze_all_but_new_classifier_rows_zeroes_old_gradients(self):
        model = DummyExpandedClassifier()

        _freeze_all_but_new_classifier_rows(model, old_class_count=2)
        model.classifier[-1].weight.sum().backward()

        gradient = model.classifier[-1].weight.grad
        self.assertTrue(torch.equal(gradient[:2], torch.zeros_like(gradient[:2])))
        self.assertTrue(torch.equal(gradient[2], torch.ones_like(gradient[2])))
        self.assertFalse(model.classifier[2].weight.requires_grad)


if __name__ == "__main__":
    unittest.main()
