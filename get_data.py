# https://scrapingant.com/blog/change-user-agent-playwright
import json
import asyncio
from playwright.async_api import async_playwright

realistic_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

async def main():
  async with async_playwright() as p:
    browser = await p.chromium.launch()
    context = await browser.new_context(user_agent=realistic_user_agent)
    page = await context.new_page()
    await page.goto("https://fbref.com/en/comps/12/La-Liga-Stats")
    table_data = []
    rows = await page.locator("#div_results2025-2026121_overall table tbody tr").all()
    
    for row in rows:
      cells = await row.locator("td").all()
      if len(cells) >= 19:
          team_data = {
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
          table_data.append(team_data)

    result = {
        "league": "LaLiga",
        "season": "2025-2026",
        "teams": table_data
    }
    print(json.dumps(result, indent=2))
    
    await browser.close()

asyncio.run(main())