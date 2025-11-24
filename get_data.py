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

async def navigate_to_page(page, url, max_retries=3):
  attempt=1
  while attempt <= max_retries:
    try:
      response = await page.goto(url, timeout=90000)
      return response
    except Exception as e:
      attempt+=1
      raise Exception({"status": "error", "message": str(e)})

async def table_results_overall(page, id_table):
  rows = await page.locator(id_table).all()
  data = []

  col_names = [
    "squad", "matches_played", 
    "wins", "drafts", "losses",
    "goals_for", "goals_against", "goals_difference",
    "total_pts", "last_match_pts", "expected_goal",
    "expected_goal_allowed", "expected_goal_difference",
    "expected_goal_difference_90", "last_five_matches",
    "attendance", "top_scorer", "goalkeeper", "notes"
    ]

  for row in rows:
    ranking = await row.locator("th").text_content() or ""
    cells = await row.locator("td").all()
    item = {}
    item["ranking"] = ranking[0].strip()

    if len(cells) >= len(col_names):
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def table_results_stats_squads(page):
  selector = "#stats_squads_standard_for tbody tr" # Using table id for subcolumns if theren't subcolumns use div id
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "age", "possession",
    "matches_played", "starts", "minutes", "minutes_played", "goals", "assists", "goals_assists", 
    "goals_no_penalty", "penalty_kicks", "penalty_attempts", "yellow_cards", "red_cards",
    "expected_goals", "expected_goal_no_penalty", "expected_assisted_goal", "expected_goal_no_penalty_plus_assist",
    "progressive_carries", "progressive_passes", "goals_per_90", "assists_per_90", "goals_assists_per_90",
    "goals_no_penalty_per_90", "goals_no_penalty_plus_assist_per_90", "expected_goals_per_90",
    "expected_assisted_goals_per_90", "expected_no_penalty_per_90", "expected_no_penalty_plus_assist_per_90"
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
    "squad", "players", "goals", "shots", "percent_shots_target", 
    "total_shots_per90", "target_shots_per90", "goals_per_shot",
    "target_shots_goal", "distance", "free_kicks", "penalties", "penalty_attempt",
    "expected_goal", "expected_goal_no_penalty", "expected_goal_per_shot", 
    "expected_goal_minus_goal", "expected_goal_no_penalty_minus_goal"
  ]

  for row in rows:
    cells = await row.locator("td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def table_results_squads_passing(page):
  selector = "#stats_squads_passing_for tbody tr"
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "90s_played", "total_passes_completed", "total_passes_attempted", "total_pass_completion",
    "total_passing_distance", "progressive_passing_distance", "short_passes_completed", "short_passes_attempted",
    "short_pass_completion", "medium_passes_completed", "medium_passes_attempted", "medium_pass_completion",
    "long_passes_completed", "long_passes_attempted", "long_pass_completion", "assists_from_passes",
    "expected_assists_goals", "expected_assists", "assists_minus_xag", "key_passes", "passes_into_final_third",
    "passes_into_penalty_area", "crosses_into_penalty_area", "progressive_passes"
  ]

  for row in rows:
    cells = await row.locator("th, td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def table_results_squads_goal_and_shot_creation(page):
  selector = "#stats_squads_gca_for tbody tr"
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "90s_played", "shot_creations", "shot_creation_per90",
    "passlive", "passdead", "takeons", "shot", "fauls_drawn", "defense_actions",
    "goal_creations", "goal_creation_per90"
  ]

  for row in rows:
    cells = await row.locator("th, td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def table_results_squads_defensive_actions(page):
  selector = "#stats_squads_defense_for tbody tr"
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "90s_played", "tackles", "tackles_won", "tackles_defensive", 
    "tackles_middle", "tackles_offensive", "dribblers_tackled", "dribbler_challenged",
    "dribblers_tackled_percent", "challenges_lost", "blocks", "blocked_shots", "blocked_passes",
    "interceptions", "tackles_interceptions", "clearances", "errors_leading_to_shot"
  ]

  for row in rows:
    cells = await row.locator("th, td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def table_results_squads_possesion(page):
  selector = "#stats_squads_possession_for tbody tr"
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "possesion", "90s_played", "touches", "touches_in_penalty_area",
    "touches_in_defensive", "touches_in_middle", "touches_in_offensive", "touches_in_offensive_penalty_area",
    "touches_live_ball", "attempted_takeons", "successful_takeons", "successful_takeon_percent",
    "tackled_takeon", "tackled_takeon_percent", "carries", "total_carry_distance", "progressive_carry_distance",
    "progresive_carries", "carries_into_final_third", "carries_into_penalty_area", "miscontrols", "dispossessed",
    "passes_received", "progressive_passes_received"
  ]

  for row in rows:
    cells = await row.locator("th, td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def table_results_squads_playing_time(page):
  selector = "#stats_squads_playing_time_for tbody tr"
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "age", "matches_played", "minutes", "minutes_per_match",
    "minutes_percent", "90s_played", "starts", "minutes_per_match_started", "completed_matches",
    "substitute_appearances", "minutes_per_substitution", "unused_substitutions", "points_per_match",
    "goals_scored", "goals_allowed", "plus_minus", "plus_minus_per_90", "expected_goal", "expected_goal_allowed",
    "expected_goal_difference", "expected_goal_difference_per_90"
  ]

  for row in rows:
    cells = await row.locator("th, td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def table_results_squads_miscellanoeus(page):
  selector = "#stats_squads_misc_for tbody tr"
  rows = await page.locator(selector).all()
  data = []

  col_names = [
    "squad", "players", "90s_played", "yellow_cards", "red_cards", "second_yellow_cards",
    "fouls_committed", "fouls_drawn", "offsides", "crosses", "interceptions", "tackles_won", "penalties_won",
    "penalties_conceded", "own_goals", "ball_recoveries", "aerials_won", "aerials_lost", "aerials_won_percent"
  ]

  for row in rows:
    cells = await row.locator("th, td").all()
    if len(cells) >= len(col_names):
      item = {}
      for i, key in enumerate(col_names):
        item[key] = await cells[i].text_content() or ""
      data.append(item)

  return data

async def build_json(comp_name, overall, squads_standard, squads_shooting, squads_passing, squads_goal_and_shot_creation, squads_defensive_action, squads_posesion, squads_playing_time, squads_miscellanoeus):
  result = {
    "league": comp_name,
    "season": "2025-2026",
    "overall_table": overall,
    "stats_squads_standard": squads_standard,
    "stats_squads_shooting": squads_shooting,
    "stats_squads_passing": squads_passing,
    "stats_squads_goal_and_shot_creation": squads_goal_and_shot_creation,
    "stats_squads_defensive_actions": squads_defensive_action,
    "stats_squads_possesion": squads_posesion,
    "stats_squads_playing_time": squads_playing_time,
    "stats_squads_miscellanoeus": squads_miscellanoeus
  }
  return json.dumps(result, indent=2)

async def main():
  playwright, browser, page = await setup_browser()
  competitions = {
   "laliga":{
      "id_general_table": "#div_results2025-2026121_overall table tbody tr",
      "url":"https://fbref.com/en/comps/12/La-Liga-Stats"
   },
  #  "premierleague":{
  #     "id_general_table": "#div_results2025-202691_overall table tbody tr",
  #     "url":"https://fbref.com/en/comps/9/Premier-League-Stats"
  #  },
  #  "bundesliga":{
  #     "id_general_table": "#div_results2025-2026201_overall table tbody tr",
  #     "url":"https://fbref.com/en/comps/20/Bundesliga-Stats"
  #  },
  #  "serie_a":{
  #     "id_general_table": "#div_results2025-2026111_overall table tbody tr",
  #     "url":"https://fbref.com/en/comps/11/Serie-A-Stats"
  #  },
  #  "champions":{
  #     "id_general_table": "#div_results2025-202680_overall table tbody tr",
  #     "url":"https://fbref.com/en/comps/8/Champions-League-Stats"
  #  }
  }

  for comp_name, values in competitions.items():
    await navigate_to_page(page, values['url'])

    overall_data = await table_results_overall(page, values['id_general_table'])
    squads_standard_data = await table_results_stats_squads(page)
    squads_shooting_data = await table_results_squads_shooting(page)
    squads_passing_data = await table_results_squads_passing(page)
    squads_goal_and_shot_creation_data = await table_results_squads_goal_and_shot_creation(page)
    squads_defensive_action_data = await table_results_squads_defensive_actions(page)
    squads_possesion_data = await table_results_squads_possesion(page)
    squads_playing_time_data = await table_results_squads_playing_time(page)
    squads_miscellaneous_data = await table_results_squads_miscellanoeus(page)
    #overall_data=[];squads_standard_data=[];squads_shooting_data=[];squads_passing_data=[];squads_goal_and_shot_creation_data=[];squads_defensive_action_data=[];squads_possesion_data=[];squads_playing_time_data=[];squads_miscellaneous_data=[]
    output = await build_json(
      comp_name, 
      overall_data, 
      squads_standard_data, 
      squads_shooting_data, 
      squads_passing_data,
      squads_goal_and_shot_creation_data,
      squads_defensive_action_data,
      squads_possesion_data,
      squads_playing_time_data,
      squads_miscellaneous_data
      )
    print(output)

  await browser.close()
  await playwright.stop()

asyncio.run(main())
