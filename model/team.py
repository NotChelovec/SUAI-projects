from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey, Integer, String
from typing import List

from database.database import Base

class Team(Base):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    discipline_id: Mapped[int] = mapped_column(ForeignKey("discipline.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("student.id"))
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)

    students: Mapped[List["Student"]] = relationship(
        "Student", back_populates="team", foreign_keys="[Student.team_id]"
    )

    def close_team(self):
        self.is_open = False

    def __repr__(self) -> str:
        return f"Team(id={self.id!r}, name={self.name!r}, discipline_id={self.discipline_id!r}, group_id={self.group_id!r}, creator_id={self.creator_id!r}, is_open={self.is_open!r})"
