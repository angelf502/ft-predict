import json
import asyncio
from playwright.async_api import async_playwright

realistic_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
COMPETITIONS = {
   "laliga": {"url": "https://www.sportsgambler.com/injuries/football/spain-la-liga/"},
   "premierleague": {"url": "https://www.sportsgambler.com/injuries/football/england-premier-league/"},
   "bundesliga": {"url": "https://www.sportsgambler.com/injuries/football/germany-bundesliga/"},
   "serie_a": {"url": "https://www.sportsgambler.com/injuries/football/italy-serie-a/"},
   "champions": {"url": "https://www.sportsgambler.com/injuries/football/uefa-champions-league/", "team_locator": "h3.injuries-title"},
}

async def setup_browser():
  playwright = await async_playwright().start()
  browser = await playwright.chromium.launch()
  context = await browser.new_context(user_agent=realistic_user_agent)
  page = await context.new_page()
  return playwright, browser, page

async def navigate_to_page(page, url, max_retries=3):
  attempt=1
  while attempt <= max_retries:
    try:
      response = await page.goto(url, timeout=90000)
      return response
    except Exception as e:
      attempt+=1
      raise Exception({"status": "error", "message": str(e)})
    
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
    
async def main():
  playwright, browser, page = await setup_browser()

  for details in COMPETITIONS.values():
    await navigate_to_page(page, details['url'])
    data = await injury_results(page, details.get('team_locator', "h3.injuries-title a"))
    print(json.dumps(data, indent=2))

  await browser.close()
  await playwright.stop()

asyncio.run(main())