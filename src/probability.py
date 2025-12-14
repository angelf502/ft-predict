from typing import Dict, List, Optional

class AdvancedPredictionSystem:
    def __init__(self, home_away_data, injuries_data, get_h2h_func=None):
        self.home_away = self._process_home_away(home_away_data)
        self.injuries = self._process_injuries(injuries_data, home_away_data)
        self.get_h2h_func = get_h2h_func
        self.h2h_cache = {}

        self.weights = {
            'home_away_stats': 0.45,
            'h2h_patterns': 0.25,
            'injuries_impact': 0.25,
            'xg_quality': 0.05
        }

    async def predict_match(self, home_team: str, away_team: str) -> Dict:
        if home_team not in self.home_away:
            raise ValueError(f"Home team '{home_team}' not found")
        if away_team not in self.home_away:
            raise ValueError(f"Away team '{away_team}' not found")

        h2h_data = await self._load_h2h(home_team, away_team)

        prob_home_away = self._analyze_home_away(home_team, away_team)
        prob_h2h = self._analyze_h2h(h2h_data) if h2h_data else self._neutral_probability()
        injuries_impact = self._analyze_injuries(home_team, away_team)
        xg_quality = self._analyze_xg_quality(h2h_data) if h2h_data else self._neutral_xg_quality()

        probabilities = self._combine_probabilities(
            prob_home_away, prob_h2h, injuries_impact, xg_quality
        )

        probabilities = self._apply_context_adjustments(probabilities)

        return self._format_results(probabilities, home_team, away_team, h2h_data)

    def _analyze_home_away(self, home: str, away: str) -> Dict[str, float]:
        home_stats = self.home_away[home]['home']
        away_stats = self.home_away[away]['away']

        try:
            xg_diff_home = float(home_stats.get('expected_goal_difference_per_game', 0))
            xg_diff_away = float(away_stats.get('expected_goal_difference_per_game', 0))

            ppg_home = float(home_stats.get('points_per_game', 0))
            ppg_away = float(away_stats.get('points_per_game', 0))

            win_rate_home = float(home_stats.get('wins', 0)) / float(home_stats.get('matches_played', 1))
            loss_rate_away = float(away_stats.get('losses', 0)) / float(away_stats.get('matches_played', 1))
        except (ValueError, ZeroDivisionError):
            return self._neutral_probability()

        base_home_advantage = 0.02

        quality_adj = (xg_diff_home - xg_diff_away) * 0.03
        efficiency_adj = (ppg_home - ppg_away) * 0.02
        result_factor = (win_rate_home + loss_rate_away - 0.5) * 0.05

        prob_home = 0.33 + base_home_advantage + (quality_adj * 0.8) + (efficiency_adj * 0.7) + (result_factor * 0.6)
        prob_away = 0.33 - (quality_adj * 0.6) - (efficiency_adj * 0.5) - (result_factor * 0.3)
        prob_draw = 1 - prob_home - prob_away

        return {
            'home': max(0.15, min(prob_home, 0.60)),
            'draw': max(0.20, min(prob_draw, 0.50)),
            'away': max(0.20, min(prob_away, 0.60))
        }

    def _analyze_h2h(self, h2h_data: List[Dict]) -> Dict[str, float]:
        if not h2h_data:
            return self._neutral_probability()

        valid_matches = [m for m in h2h_data if m.get('score') and '–' in m['score']]
        if not valid_matches:
            return self._neutral_probability()

        home_wins = away_wins = draws = 0

        for match in valid_matches[:10]:
            try:
                home_goals, away_goals = map(int, match['score'].split('–'))
                if home_goals > away_goals:
                    home_wins += 1
                elif away_goals > home_goals:
                    away_wins += 1
                else:
                    draws += 1
            except ValueError:
                continue

        total = len(valid_matches)
        return {
            'home': max(0.10, min(home_wins / total, 0.90)),
            'draw': max(0.05, min(draws / total, 0.50)),
            'away': max(0.10, min(away_wins / total, 0.90))
        }

    def _analyze_injuries(self, home: str, away: str) -> Dict[str, float]:
        def team_factor(team: str) -> float:
            team_injuries = [
                i for i in self.injuries
                if i['team'].strip().lower() == team.strip().lower()
            ]

            if not team_injuries:
                return 1.0

            factor = 1.0
            for injury in team_injuries:
                position = injury.get('position', 'M').upper()
                injury_type = injury.get('type', '')

                base_impact = {
                    'F': 0.85,
                    'M': 0.88,
                    'D': 0.90,
                    'G': 0.80
                }.get(position, 0.88)

                if 'inj-type injury-plus' in injury_type:
                    base_impact *= 0.85
                elif 'inj-type injury-questionmark' in injury_type:
                    base_impact *= 0.95

                try:
                    matches = 0 if injury.get('matches') == '-' else int(injury.get('matches', 0))
                    goals = 0 if injury.get('goals') == '-' else int(injury.get('goals', 0))
                    assists = 0 if injury.get('assists') == '-' else int(injury.get('assists', 0))

                    if matches > 5 or (goals + assists) > 2:
                        base_impact *= 0.90
                except (ValueError, TypeError):
                    pass

                factor *= base_impact

            return max(0.5, factor)

        return {
            'home_factor': team_factor(home),
            'away_factor': team_factor(away)
        }

    def _analyze_xg_quality(self, h2h_data: List[Dict]) -> Dict[str, float]:
        matches = [
            m for m in h2h_data
            if m.get('expected_goals_home') and m.get('expected_goals_away')
        ]

        if not matches:
            return self._neutral_xg_quality()

        matches = matches[:5]
        home_xg = away_xg = count = 0

        for m in matches:
            try:
                home_xg += float(m['expected_goals_home'])
                away_xg += float(m['expected_goals_away'])
                count += 1
            except ValueError:
                continue

        if count == 0:
            return self._neutral_xg_quality()

        total = home_xg + away_xg
        return {
            'home': home_xg / total if total else 0.5,
            'away': away_xg / total if total else 0.5
        }

    def _combine_probabilities(self, ha, h2h, injuries, xg):
        base = {
            'home': ha['home'] * self.weights['home_away_stats'] + h2h['home'] * self.weights['h2h_patterns'],
            'draw': ha['draw'] * self.weights['home_away_stats'] + h2h['draw'] * self.weights['h2h_patterns'],
            'away': ha['away'] * self.weights['home_away_stats'] + h2h['away'] * self.weights['h2h_patterns']
        }

        base['home'] *= injuries['home_factor']
        base['away'] *= injuries['away_factor']

        adj_home = (xg['home'] - 0.5) * self.weights['xg_quality']
        adj_away = (xg['away'] - 0.5) * self.weights['xg_quality']

        base['home'] += adj_home
        base['away'] += adj_away
        base['draw'] -= (adj_home + adj_away) / 2

        total = sum(base.values())
        return {k: v / total for k, v in base.items()} if total else self._neutral_probability()

    def _apply_context_adjustments(self, probs):
        probs['home'] = max(0.15, min(probs['home'], 0.70))
        probs['away'] = max(0.15, min(probs['away'], 0.70))
        probs['draw'] = max(0.20, min(probs['draw'], 0.50))

        total = sum(probs.values())
        return {k: v / total for k, v in probs.items()}

    def _format_results(self, probs, home, away, h2h):
        main_pick = max(probs, key=probs.get)
        values = sorted(probs.values(), reverse=True)
        confidence = min(95, max(30, (values[0] - values[1]) * 300)) if len(values) > 1 else 50

        return {
            'match': {'home': home, 'away': away},
            'probabilities': {k: round(v, 3) for k, v in probs.items()},
            'prediction': main_pick,
            'confidence': round(confidence, 1),
            'context': {
                'total_h2h_matches': len(h2h) if h2h else 0,
                'home_injuries': len(self._get_team_injuries(home)),
                'away_injuries': len(self._get_team_injuries(away))
            }
        }

    def _get_team_injuries(self, team: str) -> List[Dict]:
        team = team.strip().lower()
        return [i for i in self.injuries if i['team'].strip().lower() == team]

    async def _load_h2h(self, team1: str, team2: str) -> Optional[List[Dict]]:
        key = f"{team1}|{team2}"
        if key in self.h2h_cache:
            return self.h2h_cache[key]

        if self.get_h2h_func:
            result = await self.get_h2h_func(team1, team2)
            if result and result.get('status') == 'success':
                self.h2h_cache[key] = result['data']
                return result['data']
        return None

    def _neutral_probability(self):
        return {'home': 0.33, 'draw': 0.34, 'away': 0.33}

    def _neutral_xg_quality(self):
        return {'home': 0.5, 'away': 0.5}

    def _process_home_away(self, data):
        return {item['squad'].strip(): item for item in data}

    def _process_injuries(self, injuries_data, home_away_data):
        if isinstance(injuries_data, dict) and 'data' in injuries_data:
            all_injuries = injuries_data['data']
        elif isinstance(injuries_data, list):
            all_injuries = injuries_data
        else:
            all_injuries = []

        league_teams = {
            self._normalize_team_name(t): t
            for t in self._process_home_away(home_away_data).keys()
        }

        filtered = []
        for injury in all_injuries:
            injury_team = self._normalize_team_name(injury.get('team', ''))
            for norm, original in league_teams.items():
                if self._teams_match(norm, injury_team):
                    injury['team'] = original
                    filtered.append(injury)
                    break
        return filtered

    def _normalize_team_name(self, name: str) -> str:
        if not name:
            return ''
        name = name.lower()
        for w in ['fc', 'cf', 'afc', 'the', 'de', 'la']:
            name = name.replace(w, '')
        return (
            name.replace('_', ' ')
            .replace('-', ' ')
            .replace('.', '')
            .replace("'", '')
            .strip()
        )

    def _teams_match(self, n1: str, n2: str) -> bool:
        if not n1 or not n2:
            return False
        if n1 == n2:
            return True
        if n1 in n2 or n2 in n1:
            return True
        return bool(set(n1.split()) & set(n2.split()))
    
    def get_available_teams(self):
        return list(self.home_away.keys())
