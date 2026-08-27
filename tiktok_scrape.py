import asyncio
import json
import sys

from playwright.async_api import async_playwright

HASHTAG = sys.argv[1] if len(sys.argv) > 1 else "juz40festbts"
MAX_SCROLLS = 120       # максимум прокруток
STOP_AFTER = 12         # остановиться, если столько прокруток подряд без новых постов
OUTPUT = f"posts_{HASHTAG}.json"

collected = {}

async def main():
    async with async_playwright() as p:
        browser = await p.webkit.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()

        async def on_response(response):
            if "api/challenge/item_list" in response.url:
                try:
                    data = await response.json()
                    for item in data.get("itemList", []):
                        collected[item["id"]] = item
                except Exception:
                    pass

        page.on("response", on_response)

        url = f"https://www.tiktok.com/tag/{HASHTAG}"
        print(f"Открываю {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        print("Если появилась капча — пройдите её мышкой в окне браузера.")
        await asyncio.sleep(8)

        stale = 0
        prev = 0
        for i in range(MAX_SCROLLS):
            await page.mouse.wheel(0, 2500)
            await asyncio.sleep(2.5)
            n = len(collected)
            print(f"Прокрутка {i+1}/{MAX_SCROLLS}, постов: {n}")
            if n == prev:
                stale += 1
                if stale >= STOP_AFTER:
                    print("Новые посты перестали приходить — похоже, это всё, что отдаёт TikTok.")
                    break
            else:
                stale = 0
                prev = n

        await browser.close()

    if collected:
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(list(collected.values()), f, ensure_ascii=False, indent=2)
        print(f"\nСохранено {len(collected)} постов в {OUTPUT}")
    else:
        print("\nПостов не перехвачено — смените VPN-сервер или пройдите капчу.")

asyncio.run(main())
