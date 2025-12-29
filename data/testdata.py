from src.app.database import Player, Team, session_scope, Club, Group

async def insert_data():
    async with session_scope() as session:
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

        first_names = ["Liam", "Noah", "Oliver", "James", "Elijah", "William", "Henry", "Lucas", "Benjamin", "Theodore"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

        players = []
        player_idx = 0
        for group in groups:
            for _ in range(20):
                f_name = first_names[player_idx % len(first_names)]
                l_name = last_names[(player_idx // len(first_names)) % len(last_names)]

                players.append(
                    Player(
                        name=f"{f_name} {l_name} {player_idx + 1}",
                        teams=[teams[player_idx % len(teams)]],
                        club=clubs[player_idx % len(clubs)],
                        group=group
                    )
                )
                player_idx += 1

        session.add_all(groups)
        session.add_all(clubs)
        session.add_all(teams)
        session.add_all(players)
