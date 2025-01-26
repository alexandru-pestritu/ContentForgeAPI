import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database import Base, get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

# ------------------------------ SETUP & CONFIG ------------------------------ #
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------- FIXTURES & DEPENDENCY OVERRIDES ---------------------- #
@pytest.fixture(scope="module")
def test_db():
    """
    This fixture creates the tables in a fresh database at the beginning of the test session,
    and drops them afterward.
    """
    Base.metadata.create_all(bind=engine)
    try:
        yield TestingSessionLocal()
    finally:
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """
    Overrides the `get_db` dependency to provide a test database session.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class MockUser(User):
    """
    A mock user object.
    """
    def __init__(self, id=1, username="testuser"):
        super().__init__()
        self.id = id
        self.username = username


def mock_get_current_user():
    """
    Overrides the `get_current_user` dependency to always return a mock user.
    """
    return MockUser()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

created_blog_id = None


# ------------------------------ TEST FUNCTIONS ------------------------------- #

def test_create_blog(test_db):
    """
    Test creating a new blog.
    According to BlogCreate, we need:
      - name: str
      - base_url: HttpUrl
      - username: str
      - api_key: str
      - logo_url: Optional[HttpUrl] = None
    """
    payload = {
        "name": "My Test Blog",
        "base_url": "https://testblog.example.com",
        "username": "wpuser",
        "api_key": "wpapppass"
    }

    response = client.post("/api/v1/blogs/", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()

    assert data["name"] == "My Test Blog"
    assert data["base_url"] == "https://testblog.example.com/"
    assert "id" in data

    global created_blog_id
    created_blog_id = data["id"]


def test_read_blogs_list(test_db):
    """
    Test listing blogs (with pagination/filtering).
    """
    response = client.get("/api/v1/blogs/?skip=0&limit=10")
    assert response.status_code == 200

    data = response.json()
    assert "blogs" in data
    assert "total_records" in data
    assert data["total_records"] >= 1
    assert isinstance(data["blogs"], list)


def test_read_blog_by_id(test_db):
    """
    Test reading a specific blog by ID.
    We use the 'created_blog_id' set during creation test.
    """
    global created_blog_id
    response = client.get(f"/api/v1/blogs/{created_blog_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_blog_id
    assert data["name"] == "My Test Blog"


def test_update_blog(test_db):
    """
    Test updating an existing blog.
    According to BlogUpdate, all fields are optional, but must be valid if provided.
    """
    global created_blog_id
    payload = {
        "name": "My Updated Test Blog",
        "base_url": "https://updated.example.com",
    }

    response = client.put(f"/api/v1/blogs/{created_blog_id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_blog_id
    assert data["name"] == "My Updated Test Blog"
    assert data["base_url"] == "https://updated.example.com/"


def test_delete_blog(test_db):
    """
    Test deleting the blog we created.
    """
    global created_blog_id
    response = client.delete(f"/api/v1/blogs/{created_blog_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_blog_id

    response_notfound = client.get(f"/api/v1/blogs/{created_blog_id}")
    assert response_notfound.status_code == 404
