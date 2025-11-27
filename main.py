import asyncio
import json
from get_data import main as get_data_main
from get_injuries import main as get_injuries_main
from probability import AnalizadorProbabilidades

class FootballPredictionSystem:
    def __init__(self):
        self.analizador = None
    
    async def load_league_data(self, league):
        print(f"Loading data for {league}...")
        
        try:
            football_data, injury_data = await asyncio.gather(
                get_data_main(league),
                get_injuries_main(league),
                return_exceptions=True
            )
            
            if isinstance(football_data, Exception):
                print(f"Error in get_data: {football_data}")
                return False
            if isinstance(injury_data, Exception):
                print(f"Error in get_injuries: {injury_data}")
                return False
            
            if isinstance(football_data, str):
                football_data = json.loads(football_data)
            
            print(f"Data loaded: {len(football_data['home_away_table'])} teams, {len(injury_data['data'])} injuries")
            
            self.analizador = AnalizadorProbabilidades(
                football_data['home_away_table'],
                injury_data
            )
            
            return True
            
        except Exception as e:
            print(f"General error loading data: {e}")
            return False
    
    def get_available_teams(self):
        if not self.analizador:
            return []
        return list(self.analizador.home_away.keys())
    
    def predict_match(self, home_team, away_team):
        if not self.analizador:
            raise ValueError("You must load league data first.")
        
        return self.analizador.predecir_partido(home_team, away_team)
    
    def display_prediction(self, home_team, away_team, probabilities):
        print(f"\nPREDICTION: {home_team} vs {away_team}")
        print("=" * 50)
        print(f"Home Win: {probabilities['local']*100:.1f}%")
        print(f"Draw: {probabilities['empate']*100:.1f}%")
        print(f"Away Win: {probabilities['visitante']*100:.1f}%")
        print("=" * 50)
        
        if probabilities['local'] > probabilities['visitante'] and probabilities['local'] > probabilities['empate']:
            print(f"FAVORITE: {home_team}")
        elif probabilities['visitante'] > probabilities['local'] and probabilities['visitante'] > probabilities['empate']:
            print(f"FAVORITE: {away_team}")
        else:
            print("PREDICTION: Draw or very close match")
            

async def main():
    system = FootballPredictionSystem()
    
    leagues = ["laliga", "premierleague", "bundesliga", "serie_a", "champions"]
    
    print("FOOTBALL PREDICTION SYSTEM")
    print("=" * 40)
    
    print("\nSelect a league:")
    for i, league in enumerate(leagues, 1):
        print(f"{i}. {league}")
    
    try:
        selection = int(input("\nEnter the league number: ")) - 1
        selected_league = leagues[selection]
    except (ValueError, IndexError):
        print("Invalid selection")
        return
    
    success = await system.load_league_data(selected_league)
    if not success:
        print("Data could not be loaded")
        return
    
    teams = system.get_available_teams()
    print(f"\nAvailable teams in {selected_league}:")
    for i, team in enumerate(teams, 1):
        print(f"{i}. {team}")
    
    print("\nSelect the teams for prediction:")
    try:
        home_idx = int(input("Home team number: ")) - 1
        away_idx = int(input("Away team number: ")) - 1
        
        home_team = teams[home_idx]
        away_team = teams[away_idx]
        
        probabilities = system.predict_match(home_team, away_team)
        system.display_prediction(home_team, away_team, probabilities)
        
    except (ValueError, IndexError):
        print("Invalid team selection")


if __name__ == "__main__":
    asyncio.run(main())
