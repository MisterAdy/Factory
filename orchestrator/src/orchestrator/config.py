"""Runtime configuration objects for the orchestrator."""

from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BudgetSettings(BaseModel):
    """Budget configuration thresholds."""

    warn_threshold: float = Field(
        0.9,
        ge=0.0,
        le=1.0,
        description="Fraction of total budget that triggers a warning thread.",
    )


class OrchestratorSettings(BaseModel):
    """Core orchestrator loop configuration."""

    loop_interval_seconds: float = Field(default=10.0, gt=0)
    project_root: Path = Field(default=Path("../projects"))
    inbox_glob: str = Field(default=".mail/inbox/*.md")
    outbox_dir_name: str = Field(default=".mail/outbox")
    log_level: str = Field(default="INFO")


class Settings(BaseSettings):
    """Application settings loaded from TOML or environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="ORCH_",
        env_file=Path(__file__).resolve().parents[2] / "config" / "settings.toml",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    orchestrator: OrchestratorSettings = OrchestratorSettings()
    budgets: BudgetSettings = BudgetSettings()
    projects: List[str] = Field(default_factory=lambda: ["glp1-companion"])


def load_settings() -> Settings:
    """Load orchestrator configuration from files and environment variables."""

    return Settings()  # type: ignore[call-arg]
