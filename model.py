from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# Database ORM models

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(2048))
    is_tagged = Column(Boolean)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class ReviewTag(Base):
    __tablename__ = 'review_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_ai_tag = Column(Boolean, nullable=False, default=False)
    tag_id = Column(Integer, ForeignKey('tags.id'))
    review_id = Column(Integer, ForeignKey('reviews.id'))

class ReviewReviewTag(Base):
    __tablename__ = 'review_review_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey('reviews.id'))
    review_tag_id = Column(Integer, ForeignKey('review_tags.id'))


# Request and response models

class TagCreate(BaseModel):
    name: str


class ReviewTagCreate(BaseModel):
    tag_ids: list[int]


class TagResponse(BaseModel):
    id: int
    name: str


class ReviewResponse(BaseModel):
    id: int
    text: str
    is_tagged: bool

class ReviewCreate(BaseModel):
    text: str
    is_tagged: bool