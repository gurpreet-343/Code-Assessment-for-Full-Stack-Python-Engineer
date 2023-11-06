import pytest
from fastapi.testclient import TestClient
from main import app
from model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up a test database
engine = create_engine("sqlite:///test_reviews.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


client = TestClient(app)


@pytest.fixture
def db_session():
    with SessionLocal() as session:
        yield session


def test_create_review(db_session):
    data = {
        "text": "Test Review",
        "is_tagged": False
    }
    response = client.post("/reviews", json=data)
    assert response.status_code == 200

    created_review = response.json()
    assert created_review['text'] is not None
    assert created_review['is_tagged'] is not None


def test_create_tag(db_session):
    response = client.post(
        "/tags", json={"name": "TestTag"}, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    tag = response.json()
    assert tag['id'] is not None


def test_create_review_tags(db_session):
    data = {
        "text": "Test Review",
        "is_tagged": False
    }
    response = client.post("/reviews", json=data)
    assert response.status_code == 200

    created_review = response.json()
    response = client.post(
        "/tags", json={"name": "TestTag"}, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    tag = response.json()
    response = client.post(
        f"/reviews/{created_review['id']}/tags", json={"tag_ids": [tag['id']]}, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    review = response.json()
    assert review['id'] is not None


def test_get_reviews(db_session):
    data = {
        "text": "Test Review",
        "is_tagged": False
    }
    response = client.post("/reviews", json=data)
    assert response.status_code == 200
    response = client.get("/reviews")
    assert response.status_code == 200
    reviews = response.json()
    # Ensure you have at least one review in the test database
    assert len(reviews) > 0

def test_delete_tag(db_session):
    # Create a tag for testing
    response = client.post("/tags", json={"name": "TestTag"}, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    tag = response.json()


    response = client.delete(f"/tags/{tag['id']}")
    assert response.status_code == 200
