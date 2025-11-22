import json
import asyncio
from playwright.async_api import async_playwright

realistic_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

async def setup_browser():
  playwright = await async_playwright().start()
  browser = await playwright.chromium.launch()
  context = await browser.new_context(user_agent=realistic_user_agent)
  page = await context.new_page()
  return playwright, browser, page

async def navigate_to_page(page, url):
  await page.goto(url, timeout=90000)

async def table_results_overall(page):
  selector = "#div_results2025-2026121_overall table tbody tr"
  rows = await page.locator(selector).all()
  data = []

  for row in rows:
    cells = await row.locator("td").all()
    if len(cells) >= 19:
      item = {
        "ranking": await row.locator("th").text_content() or "",
        "squad": await cells[0].text_content() or "",
        "matches_played": await cells[1].text_content() or "",
        "wins": await cells[2].text_content() or "",
        "drafts": await cells[3].text_content() or "",
        "losses": await cells[4].text_content() or "",
        "goals_for": await cells[5].text_content() or "",
        "goals_against": await cells[6].text_content() or "",
        "goals_difference": await cells[7].text_content() or "",
        "total_pts": await cells[8].text_content() or "",
        "last_match_pts": await cells[9].text_content() or "",
        "expected_goal": await cells[10].text_content() or "",
        "expected_goal_allowed": await cells[11].text_content() or "",
        "expected_goal_difference": await cells[12].text_content() or "",
        "expected_goal_difference_90": await cells[13].text_content() or "",
        "last_five_matches": await cells[14].text_content() or "",
        "attendance": await cells[15].text_content() or "",
        "top_scorer": await cells[16].text_content() or "",
        "goalkeeper": await cells[17].text_content() or "",
        "notes": await cells[18].text_content() if len(cells) > 18 else ""
      }
      data.append(item)

  return data

async def table_results_stats_squads(page):
  selector = "#stats_squads_standard_for tbody tr" # Using table id for subcolumns if theren't subcolumns use div id
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "age", "possession",
    "mp", "starts", "minutes", "nineties",
    "goals", "assists", "goals_assists", "goals_no_pk",
    "penalty_goals", "penalty_attempts", "yellow_cards", "red_cards",
    "xg", "npxg", "xag", "npxg_xag",
    "progressive_carries", "progressive_passes",
    "goals_per90", "assists_per90", "goals_assists_per90",
    "goals_no_pk_per90", "g_a_no_pk_per90",
    "xg_per90", "xag_per90", "xg_xag_per90",
    "npxg_per90", "npxg_xag_per90"
  ]

  for row in rows:
    cells = await row.locator("th, td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        text = await cells[i].text_content()
        item[key] = text.strip() if text else ""
      data.append(item)

  return data

async def table_results_squads_shooting(page):
  selector = "#div_stats_squads_shooting_for table tbody tr"
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players",
    "goals", "shots", "shots_on_target", "sot_percent",
    "shots_per90", "sot_per90", "goals_per_shot", "goals_per_sot",
    "distance", "free_kicks", "penalties", "penalty_att",
    "xg", "npxg", "npxg_per_shot", "goals_minus_xg", "np_goals_minus_xg"
  ]

  for row in rows:
    cells = await row.locator("td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def build_json(overall, squads_standard, squads_shooting):
  result = {
    "league": "LaLiga",
    "season": "2025-2026",
    "overall_table": overall,
    "stats_squads_standard": squads_standard,
    "stats_squads_shooting": squads_shooting
  }
  return json.dumps(result, indent=2)

async def main():
  playwright, browser, page = await setup_browser()
  await navigate_to_page(page, "https://fbref.com/en/comps/12/La-Liga-Stats")

  overall_data = await table_results_overall(page)
  squads_standard_data = await table_results_stats_squads(page)
  squads_shooting_data = await table_results_squads_shooting(page)

  output = await build_json(overall_data, squads_standard_data, squads_shooting_data)
  print(output)

  await browser.close()
  await playwright.stop()

asyncio.run(main())
