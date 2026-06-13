from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.tag import Tag
from schemas.tagSchema import TagCreate, TagResponse

router = APIRouter(prefix="/tag", tags=["Tags"])


@router.post("/", response_model=TagResponse)
def create_tag(request: TagCreate, db: Session = Depends(get_db)):
    db_tag = Tag(**request.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/", response_model=list[TagResponse])
def get_all_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag
