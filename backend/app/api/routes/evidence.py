from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.timeline import TimelineEvent
from app.models.user import User
from app.services.ocr import extract_text_from_file
from app.services.storage import save_upload_file
from app.services.timeline import generate_timeline_entries
from app.utils.file_validation import guess_file_type, is_allowed_filename

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    case = session.get(Case, case_id)
    if not case or case.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not file.filename or not is_allowed_filename(file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    saved_path, stored_filename = await save_upload_file(file, current_user.id, case_id)
    extracted_text = extract_text_from_file(saved_path)
    evidence = Evidence(
        id=str(uuid4()),
        case_id=case_id,
        user_id=current_user.id,
        file_path=str(saved_path),
        file_name=stored_filename,
        file_type=guess_file_type(file.filename, file.content_type or "application/octet-stream"),
        extracted_text=extracted_text,
        metadata_json={"original_filename": file.filename, "content_type": file.content_type},
    )
    session.add(evidence)
    session.commit()
    session.refresh(evidence)

    generated_entries = generate_timeline_entries(extracted_text)
    for entry in generated_entries:
        timeline_event = TimelineEvent(
            id=str(uuid4()),
            case_id=case_id,
            event_text=str(entry["event_text"]),
            event_date=entry["event_date"],
            source_evidence_id=evidence.id,
        )
        session.add(timeline_event)
    session.commit()

    return {
        "detail": "Evidence uploaded",
        "evidence": evidence.model_dump(),
        "timeline_events_created": len(generated_entries),
    }
