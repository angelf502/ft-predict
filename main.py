import asyncio
import json
from data.get_data import main as get_data_main
from data.get_injuries import main as get_injuries_main
from data.get_h2h import get_h2h_teams
from src.probability import AdvancedPredictionSystem

class FootballPredictionSystem:
    def __init__(self):
        self.system = None

    async def load_league_data(self, league: str) -> bool:
        try:
            football_data, injury_data = await asyncio.gather(
                get_data_main(league),
                get_injuries_main(league),
                return_exceptions=True
            )

            if isinstance(football_data, Exception):
                return False
            if isinstance(injury_data, Exception):
                return False

            if isinstance(football_data, str):
                football_data = json.loads(football_data)

            self.system = AdvancedPredictionSystem(
                football_data['home_away_table'],
                injury_data,
                get_h2h_func=get_h2h_teams
            )

            return True

        except Exception:
            return False

    def get_available_teams(self):
        if not self.system:
            return []
        return self.system.get_available_teams()

    async def predict_match(self, home_team: str, away_team: str):
        if not self.system:
            raise ValueError("League data must be loaded first.")
        return await self.system.predict_match(home_team, away_team)

    def display_prediction(self, prediction: dict):
        match = prediction['match']
        probabilities = prediction['probabilities']
        context = prediction['context']

        print("=" * 60)
        print(f"PREDICTION: {match['home']} vs {match['away']}")
        print("=" * 60)

        print(f"Home: {probabilities['home'] * 100:.1f}%")
        print(f"Draw: {probabilities['draw'] * 100:.1f}%")
        print(f"Away: {probabilities['away'] * 100:.1f}%")

        result_map = {
            'home': 'HOME WIN',
            'draw': 'DRAW',
            'away': 'AWAY WIN'
        }

        print(f"Main prediction: {result_map[prediction['prediction']]}")
        print(f"Confidence: {prediction['confidence']}%")

        print(f"H2H matches: {context['total_h2h_matches']}")
        print(f"Home injuries: {context['home_injuries']}")
        print(f"Away injuries: {context['away_injuries']}")

        print("=" * 60)


async def main():
    system = FootballPredictionSystem()

    leagues = ["laliga", "premierleague", "bundesliga", "serie_a", "champions"]

    for i, league in enumerate(leagues, 1):
        print(f"{i}. {league.upper()}")

    try:
        league_index = int(input("Select league number: ")) - 1
        if league_index < 0 or league_index >= len(leagues):
            return
        league = leagues[league_index]
    except ValueError:
        return

    success = await system.load_league_data(league)
    if not success:
        return

    teams = system.get_available_teams()
    for i, team in enumerate(teams, 1):
        print(f"{i}. {team}")

    try:
        home_index = int(input("Home team number: ")) - 1
        away_index = int(input("Away team number: ")) - 1

        if (
            home_index < 0 or home_index >= len(teams)
            or away_index < 0 or away_index >= len(teams)
            or home_index == away_index
        ):
            return

        home_team = teams[home_index]
        away_team = teams[away_index]

        prediction = await system.predict_match(home_team, away_team)
        system.display_prediction(prediction)

    except Exception:
        return


if __name__ == "__main__":
    asyncio.run(main())
