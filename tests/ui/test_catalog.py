from playwright.sync_api import Page, expect


def test_catalog_loads(page: Page, base_url: str):
    page.goto(base_url)
    cards = page.locator(".movie-card")
    expect(cards).to_have_count(20)
    previous = page.get_by_role("button", name="Previous", exact=True)
    expect(previous).to_be_disabled()
    next = page.get_by_role("button", name="Next", exact=True)
    expect(next).to_be_enabled()

def test_catalog_pagination(page: Page, base_url: str):
    page.goto(base_url)
    cards = page.locator(".movie-card")
    next_button = page.get_by_role("button", name="Next", exact=True)
    next_button.click()
    expect(cards).to_have_count(5)
    previous = page.get_by_role("button", name="Previous", exact=True)
    expect(previous).to_be_enabled()
    expect(next_button).to_be_disabled()
    previous.click()
    expect(cards).to_have_count(20)
    expect(previous).to_be_disabled()
    expect(next_button).to_be_enabled()

def test_title_search_and_reset(page: Page, base_url: str):
    page.goto(base_url)
    search_input = page.get_by_label("Search by title")
    search_input.fill("coast")
    page.get_by_role("button", name="Apply").click()
    cards = page.locator(".movie-card")
    expect(cards).to_have_count(1)
    title = cards.get_by_role("heading")
    expect(title).to_contain_text("Coast")
    page.get_by_role("button", name="Reset").click()
    expect(cards).to_have_count(20)
    expect(search_input).to_have_value("")