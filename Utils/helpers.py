import re
import uuid
import hashlib


def generate_uuid():
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def hash_string(value: str) -> str:
    """SHA-256 hash of a string."""
    return hashlib.sha256(value.encode()).hexdigest()


def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def paginate_query(query, page: int, per_page: int):
    """Apply pagination to a SQLAlchemy query and return items + total."""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total
