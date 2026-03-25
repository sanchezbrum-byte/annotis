"""SQLite-backed session persistence adapter.

Uses WAL journal mode for crash-safe writes (commit survives OS kill) and
JSON serialisation for all structured fields.

Dependency rule: this adapter imports from annotis.domain only; it must
NOT import from annotis.application or annotis.ui.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from annotis.domain.errors import SessionNotFoundError
from annotis.domain.models import (
    Annotation,
    AnnotationStats,
    AnnotationType,
    BoundingBox,
    ImageMetadata,
    ImageRecord,
    QCMetrics,
    Session,
)

logger = logging.getLogger(__name__)

_SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS sessions (
    session_id      TEXT PRIMARY KEY,
    project_name    TEXT NOT NULL DEFAULT '',
    image_folder    TEXT NOT NULL DEFAULT '',
    class_labels    TEXT NOT NULL DEFAULT '[]',
    domain_context  TEXT NOT NULL DEFAULT '',
    imaging_modality TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL,
    last_saved      TEXT
);

CREATE TABLE IF NOT EXISTS image_records (
    image_id        TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL REFERENCES sessions(session_id),
    path            TEXT NOT NULL,
    is_annotated    INTEGER NOT NULL DEFAULT 0,
    last_modified   TEXT NOT NULL,
    metadata        TEXT NOT NULL DEFAULT '{}',
    qc_metrics      TEXT NOT NULL DEFAULT '{}',
    annotations     TEXT NOT NULL DEFAULT '[]',
    annotation_stats TEXT NOT NULL DEFAULT '{}'
);
"""


class SessionStore:
    """Persist and retrieve annotation sessions in a local SQLite database.

    Args:
        db_path: Path to the SQLite database file. Created on first open.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._conn = self._connect()

    def _connect(self) -> sqlite3.Connection:
        """Open the database and ensure the schema exists.  O(1)."""
        conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.executescript(_SCHEMA)
        conn.commit()
        return conn

    def save(self, session: Session) -> None:
        """Upsert the full session and all its image records.  O(n).

        Args:
            session: Session to persist.
        """
        now = datetime.now(timezone.utc).isoformat()
        session.last_saved = datetime.now(timezone.utc)

        with self._conn:
            self._conn.execute(
                """
                INSERT INTO sessions
                  (session_id, project_name, image_folder, class_labels,
                   domain_context, imaging_modality, created_at, last_saved)
                VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(session_id) DO UPDATE SET
                  project_name = excluded.project_name,
                  image_folder = excluded.image_folder,
                  class_labels = excluded.class_labels,
                  domain_context = excluded.domain_context,
                  imaging_modality = excluded.imaging_modality,
                  last_saved = excluded.last_saved
                """,
                (
                    session.session_id,
                    session.project_name,
                    str(session.image_folder),
                    json.dumps(session.class_labels),
                    session.domain_context,
                    session.imaging_modality,
                    session.created_at.isoformat(),
                    now,
                ),
            )
            for record in session.images:
                self._upsert_record(session.session_id, record)

    def load(self, session_id: str) -> Session:
        """Retrieve a Session by its ID.  O(n).

        Args:
            session_id: Primary key of the session to load.

        Returns:
            Fully populated Session instance.

        Raises:
            SessionNotFoundError: If *session_id* does not exist.
        """
        row = self._conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        columns = [d[0] for d in self._conn.execute(
            "SELECT * FROM sessions LIMIT 0"
        ).description or []]
        session_dict = dict(zip(columns, row))

        records = self._load_records(session_id)
        return _session_from_row(session_dict, records)

    def list_sessions(self) -> list[dict[str, str]]:
        """Return lightweight summaries of all sessions.  O(n).

        Returns:
            List of dicts with ``session_id``, ``project_name``, and
            ``last_saved``.
        """
        rows = self._conn.execute(
            "SELECT session_id, project_name, last_saved FROM sessions"
        ).fetchall()
        return [
            {"session_id": r[0], "project_name": r[1], "last_saved": r[2] or ""}
            for r in rows
        ]

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _upsert_record(
        self, session_id: str, record: ImageRecord
    ) -> None:
        """Upsert a single ImageRecord row.  O(1)."""
        self._conn.execute(
            """
            INSERT INTO image_records
              (image_id, session_id, path, is_annotated, last_modified,
               metadata, qc_metrics, annotations, annotation_stats)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(image_id) DO UPDATE SET
              is_annotated = excluded.is_annotated,
              last_modified = excluded.last_modified,
              metadata = excluded.metadata,
              qc_metrics = excluded.qc_metrics,
              annotations = excluded.annotations,
              annotation_stats = excluded.annotation_stats
            """,
            (
                record.image_id,
                session_id,
                str(record.path),
                int(record.is_annotated),
                record.last_modified.isoformat(),
                json.dumps(_metadata_to_dict(record.metadata)),
                json.dumps(_qc_to_dict(record.qc_metrics)),
                json.dumps([_ann_to_dict(a) for a in record.annotations]),
                json.dumps(_stats_to_dict(record.annotation_stats)),
            ),
        )

    def _load_records(self, session_id: str) -> list[ImageRecord]:
        """Retrieve and deserialise all ImageRecords for *session_id*."""
        rows = self._conn.execute(
            "SELECT * FROM image_records WHERE session_id = ?", (session_id,)
        ).fetchall()
        desc = self._conn.execute(
            "SELECT * FROM image_records LIMIT 0"
        ).description or []
        columns = [d[0] for d in desc]
        return [_record_from_row(dict(zip(columns, r))) for r in rows]


# ---------------------------------------------------------------------------
# Serialisation helpers — domain model ↔ plain dicts
# ---------------------------------------------------------------------------


def _metadata_to_dict(m: ImageMetadata) -> dict[str, Any]:
    return {
        "width": m.width, "height": m.height, "channels": m.channels,
        "bit_depth": m.bit_depth, "color_space": m.color_space,
        "file_size_bytes": m.file_size_bytes, "format": m.format,
        "creation_date": m.creation_date.isoformat() if m.creation_date else None,
    }


def _qc_to_dict(q: QCMetrics) -> dict[str, float]:
    return {
        "sharpness": q.sharpness, "brightness_mean": q.brightness_mean,
        "brightness_std": q.brightness_std, "contrast": q.contrast,
        "noise_estimate": q.noise_estimate, "saturation_mean": q.saturation_mean,
    }


def _ann_to_dict(a: Annotation) -> dict[str, Any]:
    return {
        "annotation_id": a.annotation_id,
        "class_label": a.class_label,
        "annotation_type": a.annotation_type.value,
        "bbox": (
            {"x": a.bbox.x, "y": a.bbox.y, "w": a.bbox.width, "h": a.bbox.height}
            if a.bbox else None
        ),
        "polygon": a.polygon,
        "is_crowd": a.is_crowd,
        "created_at": a.created_at.isoformat(),
    }


def _stats_to_dict(s: AnnotationStats) -> dict[str, Any]:
    return {
        "object_count": s.object_count,
        "avg_area_px": s.avg_area_px,
        "avg_area_pct": s.avg_area_pct,
        "class_distribution": s.class_distribution,
        "foreground_ratio": s.foreground_ratio,
    }


def _session_from_row(
    row: dict[str, Any],
    records: list[ImageRecord],
) -> Session:
    """Reconstruct a Session domain object from a db row dict."""
    return Session(
        session_id=row["session_id"],
        project_name=row["project_name"],
        image_folder=Path(row["image_folder"]),
        class_labels=json.loads(row["class_labels"]),
        domain_context=row["domain_context"],
        imaging_modality=row["imaging_modality"],
        created_at=datetime.fromisoformat(row["created_at"]),
        last_saved=(
            datetime.fromisoformat(row["last_saved"])
            if row["last_saved"] else None
        ),
        images=records,
    )


def _record_from_row(row: dict[str, Any]) -> ImageRecord:
    """Reconstruct an ImageRecord domain object from a db row dict."""
    md = json.loads(row["metadata"])
    qc = json.loads(row["qc_metrics"])
    anns_raw: list[dict[str, Any]] = json.loads(row["annotations"])
    stats = json.loads(row["annotation_stats"])

    return ImageRecord(
        image_id=row["image_id"],
        path=Path(row["path"]),
        is_annotated=bool(row["is_annotated"]),
        last_modified=datetime.fromisoformat(row["last_modified"]),
        metadata=ImageMetadata(
            width=md.get("width", 0),
            height=md.get("height", 0),
            channels=md.get("channels", 0),
            bit_depth=md.get("bit_depth", 8),
            color_space=md.get("color_space", "RGB"),
            file_size_bytes=md.get("file_size_bytes", 0),
            format=md.get("format", ""),
            creation_date=(
                datetime.fromisoformat(md["creation_date"])
                if md.get("creation_date") else None
            ),
        ),
        qc_metrics=QCMetrics(
            sharpness=qc.get("sharpness", 0.0),
            brightness_mean=qc.get("brightness_mean", 0.0),
            brightness_std=qc.get("brightness_std", 0.0),
            contrast=qc.get("contrast", 0.0),
            noise_estimate=qc.get("noise_estimate", 0.0),
            saturation_mean=qc.get("saturation_mean", 0.0),
        ),
        annotations=[_ann_from_dict(a) for a in anns_raw],
        annotation_stats=AnnotationStats(
            object_count=stats.get("object_count", 0),
            avg_area_px=stats.get("avg_area_px", 0.0),
            avg_area_pct=stats.get("avg_area_pct", 0.0),
            class_distribution=stats.get("class_distribution", {}),
            foreground_ratio=stats.get("foreground_ratio", 0.0),
        ),
    )


def _ann_from_dict(d: dict[str, Any]) -> Annotation:
    """Reconstruct an Annotation from a plain dict."""
    bbox: BoundingBox | None = None
    if d.get("bbox") is not None:
        b = d["bbox"]
        bbox = BoundingBox(x=b["x"], y=b["y"], width=b["w"], height=b["h"])
    return Annotation(
        annotation_id=d["annotation_id"],
        class_label=d["class_label"],
        annotation_type=AnnotationType(d["annotation_type"]),
        bbox=bbox,
        polygon=[tuple(p) for p in d.get("polygon", [])],  # type: ignore[misc]
        is_crowd=d.get("is_crowd", False),
        created_at=datetime.fromisoformat(d["created_at"]),
    )
