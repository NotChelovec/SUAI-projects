from typing import List
from sqlalchemy import Boolean, Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

class Student(Base):
    __tablename__ = "student"
    __table_args__ = {'extend_existing': True}  # Добавляем параметр extend_existing

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(50))
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id", ondelete='CASCADE'))
    group: Mapped["Group"] = relationship(back_populates="students")
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=True)
    team: Mapped["Team"] = relationship(back_populates="students", foreign_keys="[Student.team_id]")

    missed: Mapped[List["MissedClass"]] = relationship(
        back_populates="student",
        cascade="all, delete, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.full_name!r}, group_id={self.group_id!r}, is_registered={self.is_registered!r}, telegram_id={self.telegram_id!r}, team_id={self.team_id!r})"




