import time
import sys
import logging
from dataclasses import dataclass
from typing import List

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w",
                    format="%(asctime)s  %(levelname)s - %(message)s")
logging.info("Process starting")


@dataclass
class Product:
    name: str
    price: str


purple_bg = PatternFill(start_color="3e2f5b", fill_type="solid")
green_bg = PatternFill(start_color="71b340", fill_type="solid")
base_font = Font(size=11, bold=True, color="000000", name="Courier New")
base_alignment = Alignment(horizontal="center", vertical="center")

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def scrape_data(url: str, fname: str) -> List[Product]:
    product_list: List[Product] = list()
    with sync_playwright() as playwright:
        chrome = playwright.chromium
        browser = chrome.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=10000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        i = 4
        while i > 0:
            page.evaluate("() => window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_selector("._3d9cKhzXJMPBYzFkB_IaRp.Focusable").click()
            time.sleep(2)
            i -= 1
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
                        logging.info(f"Product Name: {game.name}, Product Price: {game.price}")
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
                        logging.info(f"Product Name: {game.name}, Product Price: {game.price}")
                        product_list.append(game)
                        new_page.close()
                else:
                    pass
        browser.close()
        for product in product_list:
            with open(f"{fname}.txt", "w") as f:
                f.write(f"{product.name},{product.price}\n")
        return product_list


# def to_excel(list: List[List[Product]] = [], fname: str = ""):
#     wb = Workbook()
#     ws_all_items = wb.create_sheet("All Items", 0)
#     ws_bestsellers = wb.create_sheet("Bestsellers", 1)
#     ws_new_trending = wb.create_sheet("New & Trending", 2)
#     ws_all_items['A1'].value = "Name"
#     ws_bestsellers['A1'].value = "Name"
#     ws_new_trending['A1'].value = "Name"
#     ws_all_items['B1'].value = "Price"
#     ws_bestsellers['B1'].value = "Price"
#     ws_new_trending['B1'].value = "Price"
#     for row in ws_all_items
#     wb.save("test.xlsx")

def main():
    logging.info("App started")
    # url_best_rated = "https://store.steampowered.com/specials/?flavor=contenthub_toprated"
    # url_best_sellers = (
    #     "https://store.steampowered.com/specials/?flavor=contenthub_topsellers"
    # )
    # url_new_trending = (
    #     "https://store.steampowered.com/specials/?flavor=contenthub_newandtrending"
    # )
    url_all_items = "https://store.steampowered.com/specials/"
    all_items = scrape_data(url_all_items, "All_Items")
    # bestsellers = scrape_data(url_best_sellers, "best_sellers")
    # new_trending = scrape_data(url_new_trending, "new_trending")
    wb = Workbook()

    ws_all_items = wb.active
    ws_all_items.title = "All Items"
    ws_bestsellers = wb.create_sheet("Bestsellers", 1)
    ws_new_trending = wb.create_sheet("New & Trending", 2)
    ws_all_items['A1'].value = "Name"
    ws_all_items['A1'].font = base_font
    ws_all_items['A1'].fill = purple_bg
    ws_all_items['A1'].alignment = base_alignment
    ws_all_items['B1'].value = "Price"
    ws_all_items['B1'].font = base_font
    ws_all_items['B1'].fill = green_bg
    ws_all_items['B1'].alignment = base_alignment
    ws_bestsellers['A1'].value = "Name"
    ws_bestsellers['A1'].font = base_font
    ws_bestsellers['A1'].fill = purple_bg
    ws_bestsellers['B1'].value = "Price"
    ws_bestsellers['B1'].font = base_font
    ws_bestsellers['B1'].alignment = base_alignment
    ws_bestsellers.fill = green_bg
    ws_new_trending['A1'].value = "Name"
    ws_new_trending['A1'].font = base_font
    ws_new_trending['A1'].fill = purple_bg
    ws_new_trending['A1'].alignment = base_alignment
    ws_new_trending['B1'].value = "Price"
    ws_new_trending['B1'].font = base_font
    ws_new_trending.fill = green_bg
    ws_new_trending['B1'].alignment = base_alignment
    for row in ws_all_items.iter_cols(min_row=2, max_row=ws_all_items.max_row + len(all_items), min_col=1, max_col=1):
        for cell, product in zip(row, all_items):
            cell.alignment = base_alignment
            cell.value = product.name
    for row in ws_all_items.iter_cols(min_row=2, max_row=ws_all_items.max_row + len(all_items), min_col=2, max_col=2):
        for cell, product in zip(row, all_items):
            cell.alignment = base_alignment
            cell.value = product.price

    # for row in ws_bestsellers.iter_cols(min_row=2, max_row=ws_bestsellers.max_row + len(bestsellers),
    #                                     min_col=1, max_col=1):
    #     for cell, product in zip(row, bestsellers):
    #         cell.value = product.name
    # for row in ws_bestsellers.iter_cols(min_row=2, max_row=ws_bestsellers.max_row + len(bestsellers),
    #                                     min_col=2, max_col=2):
    #     for cell, product in zip(row, bestsellers):
    #         cell.value = product.price
    # for row in ws_new_trending.iter_cols(min_row=2, max_row=ws_new_trending.max_row + len(new_trending),
    #                                      min_col=1, max_col=1):
    #     for cell, product in zip(row, new_trending):
    #         cell.value = product.name
    # for row in ws_new_trending.iter_cols(min_row=2, max_row=ws_new_trending.max_row + len(new_trending),
    #                                      min_col=2, max_col=2):
    #     for cell, product in zip(row, new_trending):
    #         cell.value = product.price
    wb.save("test.xlsx")


# add multithreading or async IDK
if __name__ == "__main__":
    main()
