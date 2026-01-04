import logging

from src.app.database import Club, Group, Player, Team, session_scope


async def insert_data():
    async with session_scope() as session:
        logger = logging.getLogger("insert_data")
        logger.info("Inserting test data into database")

        group_names = ["Championship Alpha", "League Beta", "Division Gamma", "Premier Delta"]
        groups = [Group(name=name) for name in group_names]

        clubs = [
            Club(name="River Plate FC"),
            Club(name="Mountain United"),
            Club(name="Coastal City SC"),
            Club(name="Forest Rangers")
        ]

        teams = [
            Team(name="Strikers"),
            Team(name="Titans"),
            Team(name="Warriors"),
            Team(name="Voyagers")
        ]

        logger.info("Adding groups")
        session.add_all(groups)
        logger.info("Adding clubs")
        session.add_all(clubs)
        logger.info("Adding teams")
        session.add_all(teams)
        await session.commit()

        first_names = ["Liam", "Noah", "Oliver", "James", "Elijah", "William", "Henry", "Lucas", "Benjamin", "Theodore"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

        players = []
        player_idx = 0
        for group in groups:
            for _ in range(20):
                f_name = first_names[player_idx % len(first_names)]
                l_name = last_names[(player_idx // len(first_names)) % len(last_names)]

                # Assign teams
                player_teams = []
                if player_idx % 4 != 0:  # Every 4th player has no team
                    # Assign a primary team
                    player_teams.append(teams[player_idx % len(teams)])

                    # Assign an additional team to every 3rd player (among those who have teams) for variety
                    if player_idx % 3 == 0:
                        second_team = teams[(player_idx + 1) % len(teams)]
                        player_teams.append(second_team)

                # Assign a club (every 5th player has no club)
                player_club = clubs[player_idx % len(clubs)] if player_idx % 5 != 0 else None

                players.append(
                    Player(
                        name=f"{f_name} {l_name} {player_idx + 1}",
                        teams=player_teams,
                        club=player_club,
                        group=group
                    )
                )
                player_idx += 1

        logger.info("Adding players")
        session.add_all(players)
