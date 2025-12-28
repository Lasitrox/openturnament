from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database.base import Base

# Association table for Many-to-Many relationship
player_team = Table(
    "player_team",
    Base.metadata,
    Column("player_id", ForeignKey("players.id"), primary_key=True),
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
)


class Player(Base):
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
    :ivar group: Group or category to which the player belongs.
    :type group: str
    :ivar club: Club affiliation of the player.
    :type club: str
    :ivar teams: List of teams associated with the player. This attribute is
                 managed as a relationship with cascading behavior, allowing
                 the deletion of related teams when a player is removed.
    :type teams: list[Team]
    """
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    group: Mapped[str] = mapped_column()
    club: Mapped[str] = mapped_column()

    # Relationship to the sub-table 'teams'
    teams: Mapped[list["Team"]] = relationship(
        secondary=player_team, back_populates="players"
    )

class Team(Base):
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
    name: Mapped[str] = mapped_column()
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))

    # Many-to-many relationship to 'players'
    players: Mapped[list["Player"]] = relationship(
        secondary=player_team, back_populates="teams"
    )