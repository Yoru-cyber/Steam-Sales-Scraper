import asyncio
import random
import time
import sys
import logging
import os
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import List

from playwright.async_api import async_playwright, Playwright, Page

today_date = datetime.now().strftime('%d-%m-%Y-%H:%M:%S')
if not os.path.exists("../../../logs"):
    os.mkdir("../../../logs")
if not os.path.exists("../../../data"):
    os.mkdir("../../../data")
logging.basicConfig(level=logging.INFO, filename=Path(f"./logs/app-{today_date}.log"),
                    filemode="w",
                    format="%(asctime)s %(threadName)s  %(levelname)s - %(message)s")
logging.info("Process starting")


@dataclass
class Product:
    name: str
    price: str


logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


async def get_product_info(page: Page):
    await page.wait_for_load_state("domcontentloaded", timeout=20000)
    await asyncio.sleep(4)
    p_name = await page.wait_for_selector(
        ".apphub_AppName", timeout=20000
    )
    p_price = await page.wait_for_selector(
        ".discount_final_price", timeout=20000
    )
    game = Product(
        name=await p_name.inner_text(),
        price=await p_price.inner_text(),
    )
    logging.info(
        f"Product Name: {game.name}, Product Price: {game.price}"
    )
    return game


async def solve_age_form(page: Page):
    age_field = await page.query_selector("select[id='ageYear']")
    await age_field.select_option(
        "2000"
    )
    link = await page.query_selector("a[id='view_product_page_btn']")
    await link.click()


async def scrape_data_async(url: str, playwright: Playwright) -> List[Product]:
    product_list: List[Product] = list()
    logging.info(f"Getting data from {url}")
    browser = await playwright.chromium.launch(headless=False, slow_mo=200)
    try:
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        logging.info(f"DOM content loaded from {url}")
        await page.wait_for_selector(".y9MSdld4zZCuoQpRVDgMm")
        products = await page.query_selector_all(".y9MSdld4zZCuoQpRVDgMm")
        await asyncio.sleep(random.randrange(1, 5))
        for product in products:
            anchor_locator = await product.query_selector("a")
            if anchor_locator:
                url = await anchor_locator.get_attribute("href")
                if url:
                    new_page = await browser.new_page()
                    await new_page.goto(url, wait_until="domcontentloaded")
                    await asyncio.sleep(random.randrange(1, 5))
                    logging.info(f"DOM content load from {url}")
                    if await new_page.query_selector(".age_gate"):
                        await new_page.wait_for_load_state("domcontentloaded")
                        await solve_age_form(page=new_page)
                        await new_page.wait_for_load_state("domcontentloaded")
                        await asyncio.sleep(random.randrange(1, 5))
                        logging.info(f"DOM content load from {url}")
                        game = await get_product_info(page=new_page)
                        product_list.append(game)
                        await new_page.close()
                    else:
                        await new_page.wait_for_load_state("domcontentloaded")
                        await asyncio.sleep(random.randrange(1, 5))
                        logging.info(f"DOM content load from {url}")
                        game = await get_product_info(page=new_page)
                        product_list.append(game)
                        await new_page.close()
    except Exception as e:
        logging.critical(f"App crashed {e}")
    finally:
        await browser.close()
        return product_list


async def main():
    urls = ["https://store.steampowered.com/specials/?flavor=contenthub_topsellers",
            "https://store.steampowered.com/specials/?flavor=contenthub_newandtrending",
            "https://store.steampowered.com/specials/"]
    urlss = ["https://store.steampowered.com/specials/?flavor=contenthub_newandtrending"]
    async with async_playwright() as p:
        tasks = [scrape_data_async(url, p) for url in urlss]
        results = await asyncio.gather(*tasks)
    print(results)
    # fnames = [Path("./data/All_items"),
    #           Path("./data/Best_Sellers"),
    #           Path("./data/New&Trending")]
    # write_csv(results[0], fnames[0])
    # write_csv(results[1], fnames[1])
    # write_csv(results[2], fnames[2])
    # to_excel(results, Path(f"./data/app-{today_date}.xlsx"))


if __name__ == "__main__":
    logging.info("App started")
    start_time = time.perf_counter()
    asyncio.run(main())
    logging.info(f"Executed in {time.perf_counter() - start_time:0.2f} seconds")
