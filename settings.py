from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


def _as_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None
    groq_model: str
    database_url: str
    generator_temperature: float
    reviewer_temperature: float
    demo_mode: bool


def get_settings() -> Settings:
    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./part2_runs.db"),
        generator_temperature=float(os.getenv("GROQ_TEMPERATURE_GENERATOR", "0.2")),
        reviewer_temperature=float(os.getenv("GROQ_TEMPERATURE_REVIEWER", "0.0")),
        demo_mode=_as_bool(os.getenv("DEMO_MODE", "0")),
    )
