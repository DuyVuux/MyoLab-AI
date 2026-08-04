from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator

class RegistryStateEnum(str, Enum):
    DRAFT = "DRAFT"
    AUTHORIZED = "AUTHORIZED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

class RerunStatusEnum(str, Enum):
    EXACT_MATCH = "EXACT_MATCH"
    MATCH_WITHIN_TOLERANCE = "MATCH_WITHIN_TOLERANCE"
    MISMATCH = "MISMATCH"
    NONCOMPARABLE = "NONCOMPARABLE"
    BLOCKED = "BLOCKED"

class RandomSeeds(BaseModel):
    split_seed: int
    model_seed: int
    bootstrap_seed: Optional[int] = None
    calibration_seed: Optional[int] = None
    fewshot_seed: Optional[int] = None
    domain_classifier_seed: Optional[int] = None

class RunManifest(BaseModel):
    run_id: str = Field(..., description="Unique identifier for the run")
    created_at_utc: str = Field(..., description="ISO 8601 UTC timestamp")
    git_commit: str = Field(..., description="Git commit hash")
    environment_lock_sha256: str = Field(..., description="SHA-256 of the uv.lock file")
    dataset_ids: List[str] = Field(..., description="List of dataset IDs used")
    data_manifest_sha256: str = Field(..., description="SHA-256 of the data manifest")
    split_manifest_sha256: str = Field(..., description="SHA-256 of the split manifest")
    feature_contract_sha256: str = Field(..., description="SHA-256 of the feature contract")
    model_config_sha256: str = Field(..., description="SHA-256 of the model config")
    random_seeds: RandomSeeds = Field(..., description="Seeds used for randomness")
    command: List[str] = Field(..., description="The command used to execute the run")
    sealed_test_opened: bool = Field(False, description="Whether sealed test data was opened")
    pooled_training: bool = Field(..., description="Whether data was pooled across datasets")
    registry_state: RegistryStateEnum = Field(..., description="Current state of the run in the registry")

class RerunComparison(BaseModel):
    metric_name: str
    absolute_delta: float
    within_tolerance: bool
    tolerance_applied: float

class RerunResult(BaseModel):
    schema_version: str = Field("1.0.0")
    original_run_id: str
    rerun_id: str
    status: RerunStatusEnum
    comparisons: List[RerunComparison]
    prediction_mismatch_count: Optional[int] = None
