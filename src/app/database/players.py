from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database.base import DataBase


class Group(DataBase):
    """Represents a group or category for players."""
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    players: Mapped[list["Player"]] = relationship(back_populates="group")


class Club(DataBase):
    """Represents a club affiliation."""
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    players: Mapped[list["Player"]] = relationship(back_populates="club")


class PlayerTeam(DataBase):
    """Association table for Many-to-Many relationship between players and teams."""
    __tablename__ = "player_team"

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)


class Player(DataBase):
    """Represents a player in the system.

    This class provides a structure for storing and managing information related
    to a player, such as their name, group, and club. Additionally, it establishes
    a relationship with the 'Team' class, allowing players to be associated with
    one or more teams. The class utilizes database mapping to define its attributes
    and relationships.

    :ivar id: Unique identifier for the player.
    :type id: int
    :ivar name: Name of the player.
    :type name: str
    :ivar group_id: Foreign key referencing the group.
    :type group_id: int
    :ivar club_id: Foreign key referencing the club.
    :type club_id: int
    :ivar group: Group object associated with the player.
    :type group: Group
    :ivar club: Club object associated with the player.
    :type club: Club
    :ivar teams: List of teams associated with the player.
    :type teams: list[Team]
    """
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), nullable=True)

    # Relationships
    group: Mapped["Group"] = relationship(back_populates="players")
    club: Mapped["Club"] = relationship(back_populates="players")
    teams: Mapped[list["Team"]] = relationship(
        secondary="player_team", back_populates="players"
    )

class Team(DataBase):
    """Representation of a sports team.

    This class maps to the "teams" table in the database. Each team has an identifier, a name, 
    and a foreign key reference to a player. Additionally, it includes a relationship back 
    to the associated player for easy access to related data.

    :ivar id: Unique identifier for the team.
    :type id: int
    :ivar team_name: The name of the team.
    :type team_name: str
    :ivar player_id: Foreign key referencing the associated player's ID.
    :type player_id: int
    :ivar players: The player associated with the team. This is a back-reference to the
    "Player" entity, allowing bidirectional navigation between Team and Player.
    :type Player: Player
    """
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    # Many-to-many relationship to 'players'
    players: Mapped[list["Player"]] = relationship(
        secondary="player_team", back_populates="teams"
    )