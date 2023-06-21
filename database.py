import datetime
import os
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
DB_PATH = os.path.join("db", "database.db")

# Create the folder if it doesn't exist
folder_path = os.path.dirname(DB_PATH)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


class User(Base):
    """Class representing a user in the system."""

    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True, nullable=True)

    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")


class Upload(Base):
    """Class representing an uploaded file in the system."""

    __tablename__ = 'uploads'

    id = mapped_column(Integer, primary_key=True)
    uid = mapped_column(String(36), unique=True, nullable=False, default='')  # default empty uid
    filename = mapped_column(String(255), nullable=False)
    upload_time = mapped_column(DateTime, nullable=False, default=datetime.now)
    finish_time = mapped_column(DateTime)
    status = mapped_column(String(50), nullable=False)
    user_id = mapped_column(Integer, ForeignKey("users.id"), default="Not Registered", nullable=True)

    user = relationship("User", back_populates="uploads")

    def upload_path(self) -> str:
        """Get the path of the uploaded file."""
        return os.path.join("uploads", self.filename)

    def set_finish_time(self) -> None:
        """Set the finish time of the upload to the current datetime."""
        self.finish_time = datetime.now()  # finish_time


# Create the database and tables
engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

