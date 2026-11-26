"""
Unit tests for AudioService and Database History CRUD
"""
import pytest
from app.services.audio_service import AudioService
from app.database.database import SessionLocal, create_tables
from app.database import crud
from app.database.models import UploadRecord


@pytest.fixture(scope="module")
def db_session():
    create_tables()
    db = SessionLocal()
    yield db
    db.close()


def test_audio_service_initialization():
    service = AudioService()
    # Check binary detection without error
    piper_bin = service._get_piper_binary()
    assert piper_bin is None or isinstance(piper_bin, str)


def test_audio_service_voice_candidate():
    service = AudioService()
    model_path = service._get_voice_model("nonexistent_voice_model_test")
    assert model_path is None


def test_history_crud_lifecycle(db_session):
    # 1. Create upload
    upload = crud.create_upload(
        db_session,
        filename="test_lifecycle.png",
        original_filename="original.png",
        file_type="image",
        mime_type="image/png",
        file_size=1024,
        file_path="storage/uploads/test_lifecycle.png",
    )
    assert upload.id is not None
    upload_id = upload.id

    # 2. Get upload
    fetched = crud.get_upload(db_session, upload_id)
    assert fetched is not None
    assert fetched.original_filename == "original.png"
    assert fetched.status == "uploaded"

    # 3. Update status
    crud.update_upload_status(db_session, upload_id, "completed")
    updated = crud.get_upload(db_session, upload_id)
    assert updated.status == "completed"

    # 4. List history includes it
    items, total = crud.get_history(db_session, page=1, page_size=10)
    assert total >= 1
    ids = [item.id for item in items]
    assert upload_id in ids

    # 5. Delete upload
    deleted = crud.delete_history_item(db_session, upload_id)
    assert deleted is True
    assert crud.get_upload(db_session, upload_id) is None


def test_user_settings_crud(db_session):
    settings = crud.get_settings(db_session)
    assert settings is not None
    assert settings.id == 1

    updated = crud.update_settings(db_session, speech_speed=1.5, text_size="xl")
    assert updated.speech_speed == 1.5
    assert updated.text_size == "xl"

    # Reset
    crud.update_settings(db_session, speech_speed=1.0, text_size="md")
