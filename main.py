from fastapi import Depends, FastAPI, HTTPException, Query, Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from model import Review, Tag, ReviewTag, ReviewReviewTag, Base, ReviewResponse, ReviewTagCreate, ReviewCreate, TagResponse, TagCreate

app = FastAPI(title="Reviews Rest APIs")

engine = create_engine("sqlite:///reviews.db")
Base.metadata.create_all(bind=engine, checkfirst=True)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/reviews/{review_id}/tags", response_model=ReviewResponse)
async def add_tags_to_review(
    review_id: int,
    review_tags: ReviewTagCreate,
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for tag_id in review_tags.tag_ids:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag:
            review_tag = ReviewTag(review_id=review_id, tag_id=tag_id)
            db.add(review_tag)

    db.commit()
    db.refresh(review)
    return review


@app.get("/reviews", response_model=list[ReviewResponse])
async def get_reviews(skip: int = Query(0, title="Skip records"),
                      limit: int = Query(10, title="Limit records"),
                      tag_ids: list[int] = Query([], title="Filter by tag IDs"),
                      db: Session = Depends(get_db)):
    query = db.query(Review)

    if tag_ids:
        query = query.join(ReviewReviewTag).filter(
            ReviewReviewTag.review_tag_id.in_(tag_ids))

    reviews = query.offset(skip).limit(limit).all()

    return reviews


@app.post("/reviews", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    db_review = Review(**review.model_dump())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@app.post("/tags", response_model=TagResponse)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = Tag(**tag.model_dump())
    db.add(new_tag)
    db.commit()
    return new_tag


@app.delete("/tags/{tag_id}", response_model=TagResponse)
async def delete_tag(tag_id: int = Path(..., title="Tag ID"), db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.query(ReviewTag).filter(ReviewTag.tag_id == tag_id).delete()
    db.delete(tag)
    db.commit()
    return tag


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
