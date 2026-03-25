"""Unit tests for the SQLite session store adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from annotis.adapters.session_store import SessionStore
from annotis.domain.errors import SessionNotFoundError
from annotis.domain.models import (
    Annotation,
    BoundingBox,
    ImageMetadata,
    ImageRecord,
    Session,
)


def _make_store(tmp_path: Path) -> SessionStore:
    return SessionStore(tmp_path / "test.db")


def _make_session() -> Session:
    record = ImageRecord(
        path=Path("/tmp/img.jpg"),
        metadata=ImageMetadata(width=800, height=600, channels=3),
        is_annotated=True,
        annotations=[
            Annotation(
                class_label="cat",
                bbox=BoundingBox(x=10.0, y=20.0, width=100.0, height=80.0),
            )
        ],
    )
    return Session(
        project_name="my project",
        image_folder=Path("/tmp/images"),
        class_labels=["cat", "dog"],
        images=[record],
    )


class TestSessionStoreSave:
    def test_save_does_not_raise_for_valid_session(
        self, tmp_path: Path
    ) -> None:
        store = _make_store(tmp_path)
        session = _make_session()

        store.save(session)  # must not raise

        store.close()

    def test_save_is_idempotent_when_called_twice(
        self, tmp_path: Path
    ) -> None:
        store = _make_store(tmp_path)
        session = _make_session()
        store.save(session)

        store.save(session)  # second call must not raise or duplicate

        sessions = store.list_sessions()
        assert len(sessions) == 1
        store.close()


class TestSessionStoreLoad:
    def test_load_restores_project_name(self, tmp_path: Path) -> None:
        store = _make_store(tmp_path)
        original = _make_session()
        store.save(original)

        restored = store.load(original.session_id)

        assert restored.project_name == "my project"
        store.close()

    def test_load_restores_class_labels(self, tmp_path: Path) -> None:
        store = _make_store(tmp_path)
        original = _make_session()
        store.save(original)

        restored = store.load(original.session_id)

        assert restored.class_labels == ["cat", "dog"]
        store.close()

    def test_load_restores_image_count(self, tmp_path: Path) -> None:
        store = _make_store(tmp_path)
        original = _make_session()
        store.save(original)

        restored = store.load(original.session_id)

        assert len(restored.images) == 1
        store.close()

    def test_load_restores_annotation_class_label(
        self, tmp_path: Path
    ) -> None:
        store = _make_store(tmp_path)
        original = _make_session()
        store.save(original)

        restored = store.load(original.session_id)

        assert restored.images[0].annotations[0].class_label == "cat"
        store.close()

    def test_load_restores_bounding_box(self, tmp_path: Path) -> None:
        store = _make_store(tmp_path)
        original = _make_session()
        store.save(original)

        restored = store.load(original.session_id)
        bbox = restored.images[0].annotations[0].bbox

        assert bbox is not None
        assert bbox.x == 10.0
        assert bbox.width == 100.0
        store.close()

    def test_load_raises_session_not_found_for_unknown_id(
        self, tmp_path: Path
    ) -> None:
        store = _make_store(tmp_path)

        with pytest.raises(SessionNotFoundError):
            store.load("nonexistent-id")

        store.close()


class TestSessionStoreListSessions:
    def test_empty_store_returns_empty_list(self, tmp_path: Path) -> None:
        store = _make_store(tmp_path)

        assert store.list_sessions() == []
        store.close()

    def test_returns_one_entry_per_saved_session(
        self, tmp_path: Path
    ) -> None:
        store = _make_store(tmp_path)
        store.save(_make_session())
        store.save(_make_session())

        summaries = store.list_sessions()

        assert len(summaries) == 2
        store.close()

    def test_summary_contains_required_keys(self, tmp_path: Path) -> None:
        store = _make_store(tmp_path)
        store.save(_make_session())

        summary = store.list_sessions()[0]

        assert {"session_id", "project_name", "last_saved"} <= set(summary)
        store.close()
