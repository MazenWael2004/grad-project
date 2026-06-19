import torch.nn as nn

class CLIPClassifierV2(nn.Module):
    def __init__(self, clip_model, num_classes, embed_dim):
        super().__init__()
        self.visual = clip_model.visual

        self.classifier = nn.Sequential(
            nn.LayerNorm(embed_dim),
            nn.Dropout(0.2),
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(embed_dim // 2, num_classes)
        )

    def forward(self, images):
        features = self.visual(images)
        features = features / features.norm(dim=-1, keepdim=True)
        return self.classifier(features)