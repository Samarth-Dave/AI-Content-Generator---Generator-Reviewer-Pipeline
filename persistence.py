from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from schemas_v2 import RunArtifact
from settings import get_settings


class Base(DeclarativeBase):
    pass


class RunArtifactRecord(Base):
    __tablename__ = "run_artifacts"

    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    artifact_json: Mapped[str] = mapped_column(Text, nullable=False)


def get_engine():
    settings = get_settings()
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    return create_engine(settings.database_url, connect_args=connect_args, future=True)


def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)


def persist_artifact(artifact: RunArtifact) -> None:
    init_db()
    session_factory = get_session_factory()
    payload = artifact.model_dump(mode="json", by_alias=True)
    record = RunArtifactRecord(
        run_id=artifact.run_id,
        user_id=artifact.input.user_id,
        status=artifact.final.status,
        started_at=artifact.timestamps.started_at,
        artifact_json=json.dumps(payload),
    )
    with session_factory() as session:
        session.merge(record)
        session.commit()


def load_artifacts(user_id: str | None = None) -> list[RunArtifact]:
    init_db()
    session_factory = get_session_factory()
    statement = select(RunArtifactRecord).order_by(RunArtifactRecord.started_at.desc())
    if user_id:
        statement = statement.where(RunArtifactRecord.user_id == user_id)

    with session_factory() as session:
        records = session.execute(statement).scalars().all()

    return [RunArtifact.model_validate_json(record.artifact_json) for record in records]