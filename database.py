import datetime
import os
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
DB_PATH = os.path.join("db", "database.db")


class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True, nullable=True)

    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")


class Upload(Base):
    __tablename__ = 'uploads'

    id = mapped_column(Integer, primary_key=True)
    uid = mapped_column(String(36), unique=True, nullable=False, default=str(uuid.uuid4()))
    filename = mapped_column(String(255), nullable=False)
    upload_time = mapped_column(DateTime, nullable=False, default=datetime.now)
    finish_time = mapped_column(DateTime)
    status = mapped_column(String(50), nullable=False)
    user_id = mapped_column(Integer, ForeignKey("users.id"), default="Not Registered", nullable=True)

    user = relationship("User", back_populates="uploads")

    def upload_path(self):
        return os.path.join("uploads", self.filename)

    def set_finish_time(self):
        self.finish_time = datetime.now()  # finish_time


# Create the database and tables
engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# ------------------test the database------------------
# Create a new user and upload
email = input("Enter your email (optional): ").strip()

if email:
    # User provided an email, check if it exists in Users table
    user = session.query(User).filter_by(email=email).first()

    # email already registered
    if user:
        upload = Upload(filename="justDumpFile.txt", status="done", user_id=user.id)
        upload.set_finish_time()  # Set finish_time for uploads without a user
    else:
        # User doesn't exist, create a new User
        user = User(email=email)
        session.add(user)
        session.commit()
        upload = Upload(filename="justDumpFile.txt", status="done", user_id=user.id)
        upload.set_finish_time()  # Set finish_time for uploads without a user

    session.add(upload)
    session.commit()
else:
    # User did not provide an email, create Upload without User
    upload = Upload(filename="justDumpFile.txt", status="done")
    upload.set_finish_time()  # Set finish_time for uploads without a user
    session.add(upload)
    session.commit()
