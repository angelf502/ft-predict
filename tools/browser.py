from playwright.async_api import async_playwright

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

async def setup_browser():
  playwright = await async_playwright().start()
  browser = await playwright.chromium.launch()
  context = await browser.new_context(user_agent=USER_AGENT)
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
