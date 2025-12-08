import sys, os
import asyncio
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from tools.browser import setup_browser, navigate_to_page
from tools.cache_redis import save_data, get_data

COMPETITIONS = {
   "laliga": {"url": "https://www.sportsgambler.com/injuries/football/spain-la-liga/"},
   "premierleague": {"url": "https://www.sportsgambler.com/injuries/football/england-premier-league/"},
   "bundesliga": {"url": "https://www.sportsgambler.com/injuries/football/germany-bundesliga/"},
   "serie_a": {"url": "https://www.sportsgambler.com/injuries/football/italy-serie-a/"},
   "champions": {"url": "https://www.sportsgambler.com/injuries/football/uefa-champions-league/", "team_locator": "h3.injuries-title"},
}
    
async def injury_results(page, team_locator):
  selector = ".injury-block"
  injury_blocks = await page.locator(selector).all()
  data = []

  col_names = [
    "team", "type", "player", "position", "matches", "goals", "assists", 
    "info", "expected_return"
  ]

  for block in injury_blocks:
    team_element = block.locator(team_locator)
    team_name = await team_element.text_content() or ""
    rows = await block.locator(".inj-row").all()
    for row in rows:
      container = row.locator(".inj-container:not(.inj-titles)")
      cells = await container.locator("span:not(.inj-dropdown)").all()
      if len(cells) >= len(col_names) - 1:
        item = {"team": team_name}
        for i, key in enumerate(col_names[1:], 1):
          if key == "type":
            class_name = await cells[i-1].get_attribute("class") or ""
            item[key] = class_name
          else:
            item[key] = await cells[i-1].text_content() or ""
        data.append(item)

  return data
    
async def main(league):
  if league not in COMPETITIONS:
    return {"status": "error", "message": f"League: '{league}' not found."}

  cache_key = "ft_injuries"
  cached_data = get_data(cache_key)

  if cached_data:
    return {
      "status": "success",
      "data": cached_data
    }

  playwright, browser, page = await setup_browser()
  competition = COMPETITIONS[league]
  await navigate_to_page(page, competition['url'])
  data = await injury_results(page, competition.get('team_locator', "h3.injuries-title a"))
  await browser.close()
  await playwright.stop()

  save_data(cache_key, data)

  return {"status": "success", "data": data}

# a = asyncio.run(main(league=""))
