import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str
    pagination_column: str


class APIConfig(BaseModel):
    token: str


class Config:
    """Application configuration."""

    def __init__(self):
        self.db = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "warehouse"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            pagination_column=os.getenv("PAGINATION_COLUMN", "id"),
        )

        self.api = APIConfig(token=os.getenv("API_TOKEN", ""))

    def get_db_url(self) -> str:
        """Get the database URL for SQLAlchemy."""
        return f"postgresql://{self.db.user}:{self.db.password}@{self.db.host}:{self.db.port}/{self.db.name}"


# Create a global config instance
config = Config()
