from dataclasses import dataclass
from typing import List
from playwright.sync_api import sync_playwright


@dataclass
class Product:
    name: str
    price: str


def scrape_data(url: str, fname: str):
    product_list: List[Product] = list()
    with sync_playwright() as playwright:
        chrome = playwright.chromium
        browser = chrome.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.evaluate("() => window.scrollBy(0, document.body.scrollHeight)")
        page.wait_for_selector(".y9MSdld4zZCuoQpRVDgMm")
        div_locators = page.query_selector_all(".y9MSdld4zZCuoQpRVDgMm")

        for element in div_locators:
            anchor_locator = element.query_selector("a")
            if anchor_locator:
                url = anchor_locator.get_attribute("href")
                if url is not None:
                    new_page = browser.new_page()
                    new_page.goto(url)
                    new_page.wait_for_load_state("domcontentloaded", timeout=10000)
                    if new_page.query_selector(".age_gate") is not None:
                        new_page.query_selector("select[id='ageYear']").select_option(
                            "2000"
                        )
                        new_page.query_selector("a[id='view_product_page_btn']").click()
                        new_page.wait_for_load_state("domcontentloaded", timeout=10000)
                        game = Product(
                            name=new_page.wait_for_selector(
                                ".apphub_AppName"
                            ).inner_text(),
                            price=new_page.query_selector(
                                ".discount_final_price"
                            ).inner_text(),
                        )
                        product_list.append(game)
                        new_page.close()
                    else:
                        if new_page.wait_for_selector(".apphub_AppName") is None:
                            break
                        game = Product(
                            name=new_page.query_selector(
                                ".apphub_AppName"
                            ).inner_text(),
                            price=new_page.query_selector(
                                ".discount_final_price"
                            ).inner_text(),
                        )
                        product_list.append(game)
                        new_page.close()

                else:
                    pass
        browser.close()
        for product in product_list:
            with open(f"{fname}.txt", "a") as f:
                f.write(f"Game name: {product.name}\nGame price: {product.price}\n\n")


def main():
    url_best_rated = "https://store.steampowered.com/specials/?flavor=contenthub_toprated"
    url_best_sellers = (
        "https://store.steampowered.com/specials/?flavor=contenthub_topsellers"
    )
    url_new_trending = (
        "https://store.steampowered.com/specials/?flavor=contenthub_newandtrending"
    )
    url_all_items = "https://store.steampowered.com/specials/"
    scrape_data(url_all_items, "all_items")
    scrape_data(url_best_sellers, "best_sellers")
    scrape_data(url_new_trending, "new_trending")


# add multithreading or async IDK
if __name__ == "__main__":
    main()
