import sys
import os
import asyncio
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from tools.browser import setup_browser, navigate_to_page
from tools.cache_redis import save_data, get_data

H2H = {
    "base_url": "https://fbref.com/en/stathead/matchup/teams/",
    "barcelona": {"id": "206d90db"},
    "real_madrid": {"id": "53a2f082"},
    "atletico_madrid": {"id": "db3b9613"},
    "villarreal": {"id": "2a8183b3"},
    "real_betis": {"id": "fc536746"},
    "espanyol": {"id": "a8661628"},
    "getafe": {"id": "7848bd64"},
    "athletic_club": {"id": "2b390eca"},
    "rayo_vallecano": {"id": "98e8af82"},
    "real_sociedad": {"id": "e31d1cd9"},
    "elche": {"id": "6c8b07df"},
    "celta_vigo": {"id": "f25da7fb"},
    "sevilla": {"id": "ad2be733"},
    "alaves": {"id": "8d6fd021"},
    "valencia": {"id": "dcc91a7b"},
    "mallorca": {"id": "2aa12281"},
    "osasuna": {"id": "03c57e2b"},
    "girona": {"id": "9024a00a"},
    "levante": {"id": "9800b6a1"},
    "oviiedo": {"id": "ab358912"},
    "arsenal": {"id": "18bb7c10"},
    "manchester_city": {"id": "b8fd03ef"},
    "chelsea": {"id": "cff3d9bb"},
    "aston_villa": {"id": "8602292d"},
    "brighton": {"id": "d07537b9"},
    "sunderland": {"id": "8ef52968"},
    "manchester_united": {"id": "19538871"},
    "liverpool": {"id": "822bd0ba"},
    "everton": {"id": "d3fd31cc"},
    "crystal_palace": {"id": "47c64c55"},
    "tottenham": {"id": "361ca564"},
    "brentford": {"id": "cd051869"},
    "newcastle": {"id": "b2b47a98"},
    "bournemouth": {"id": "4ba7cbea"},
    "fullham": {"id": "fd962109"},
    "nottingham_forest": {"id": "e4a775cb"},
    "west_ham": {"id": "7c21e445"},
    "leeds_united": {"id": "5bfb9659"},
    "burnley": {"id": "943e8050"},
    "wolverhampton": {"id": "8cec06e1"},
    "milan": {"id": "dc56fe14"},
    "napoli": {"id": "d48ad4ff"},
    "inter": {"id": "d609edc0"},
    "roma": {"id": "cf74a709"},
    "como": {"id": "28c9c3cd"},
    "bologna": {"id": "1d8099f8"},
    "juventus": {"id": "e0652b02"},
    "lazio": {"id": "7213da33"},
    "udinese": {"id": "04eea015"},
    "sassuolo": {"id": "e2befd26"},
    "cremonese": {"id": "9aad3a77"},
    "atalanta": {"id": "922493f3"},
    "torino": {"id": "105360fe"},
    "lecce": {"id": "ffcbe334"},
    "cagliari": {"id": "c4260e09"},
    "genoa": {"id": "658bf2de"},
    "parma": {"id": "eab4234c"},
    "pisa": {"id": "4cceedfc"},
    "fiorentina": {"id": "421387cf"},
    "hellas_verona": {"id": "0e72edf2"},
    "bayern_munich": {"id": "054efa67"},
    "leipzig": {"id": "acbb6a5b"},
    "dortmund": {"id": "add600ae"},
    "bayer_leverkusen": {"id": "c7a9f859"},
    "hoffenheim": {"id": "033ea6b8"},
    "stuttgart": {"id": "598bc722"},
    "eintracht_frankfurt": {"id": "f0ac8ee6"},
    "freiburg": {"id": "a486e511"},
    "werder_bremen": {"id": "62add3bf"},
    "koln": {"id": "bc357bf7"},
    "union_berlin": {"id": "7a41008f"},
    "monchengladbach": {"id": "32f3ee20"},
    "hamburg": {"id": "26790c6a"},
    "augsburg": {"id": "0cdc4311"},
    "wolfsburg": {"id": "4eaa11d7"},
    "heidenheim": {"id": "18d9d2a7"},
    "stpauli": {"id": "54864664"},
    "mainz": {"id": "a224b06a"},
}

async def fetch_h2h_data(page):
    all_matches = await page.locator("#games_history_all tbody tr").all()
    data = []

    col_names = [
        "competitions", "round", "day", "date", "time", "home", "expected_goals_home", "score",
        "expected_goals_away", "away", "attendance", "venue", "referee", "match_report", "notes"
    ]

    for match in all_matches:
        cells = await match.locator("th, td").all()
        if len(cells) >= len(col_names):
            item = {}
            for i, key in enumerate(col_names):
                values = await cells[i].inner_text() or ""
                values = " ".join(values.split())
                item[key] = values
            data.append(item)
    return data

async def get_h2h(team1, team2):
    missing = [team for team in (team1, team2) if team not in H2H]
    if missing:
        return {"status": "error", "message": f"Team(s) not found(s): {', '.join(missing)}"}
    
    cache_key = f"ft_h2h:{team1}:{team2}"
    cached_data = get_data(cache_key)

    if cached_data:
        return {
            "status": "success",
            "data": cached_data
        }

    team1_id = H2H[team1]['id']
    team2_id = H2H[team2]['id']
    url = f"{H2H['base_url']}{team1_id}/{team2_id}" # Order here does not matter
    playwright, browser, page = await setup_browser()
    await navigate_to_page(page, url)
    data = await fetch_h2h_data(page)
    await browser.close()
    await playwright.stop()

    save_data(cache_key, data)

    return {"status": "success", "data": data}

# a = asyncio.run(get_h2h("real_madrid", "barcelona"))
