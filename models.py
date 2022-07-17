from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    age = Column(String(30))
    sex = Column(String(30))
    name = Column(String)
    city = Column(String)
    vk_id = Column(Integer, unique=True)
    photos = relationship(
        "Photo", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, city={self.city!r})"


class Photo(Base):
    __tablename__ = "photo"
    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="photos")

    def __repr__(self):
        return f"Photo(id={self.id!r}, path={self.vk_id!r})"


class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    pair_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Address(user_id={self.user_id!r}, pair_id={self.pair_id!r})"


engine = create_engine("sqlite:///db.sqlite3", echo=True, future=True)
Base.metadata.create_all(engine)
