from src.app.database import Player, Team, session_scope

async def insert_data():
    async with session_scope() as session:
        teams = [Team(name="Team 1"), Team(name="Team 2")]
        players = [
            Player(name="Player 1", teams=[teams[0]], club="Club 1"),
            Player(name="Player 2", teams=[teams[0]], club="Club 1"),
            Player(name="Player 3", teams=[teams[1]], club="Club 2"),
            Player(name="Player 4", teams=[teams[1]], club="Club 2"),
        ]
        await session.add_all(teams)
        await session.add_all(players)
        await session.commit()
