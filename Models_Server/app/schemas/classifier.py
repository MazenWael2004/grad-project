from pydantic import BaseModel, Field


class TrainingClassPayload(BaseModel):
    id: int
    name: str
    image_paths: list[str] = Field(default_factory=list)


class TrainingStartRequest(BaseModel):
    run_id: int
    classes: list[TrainingClassPayload]
    base_model_version_id: int | None = None
    base_checkpoint_path: str | None = None
    config: dict = Field(default_factory=dict)


class ReloadModelRequest(BaseModel):
    model_version_id: int
    checkpoint_path: str
