import time
import os
from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from core.models import Product


class Command(BaseCommand):
    help = 'Запускает парсер и сохраняет данные в базу Django'

    def handle(self, *args, **options):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        parser_instance = parse("душ")
        parser_instance.parser()

class parse:
    def __init__(self, keyword):
        self.keyword = keyword
        self.list_item_name = []
        self.list_item_price = []

    def __get_links(self):
        self.page.wait_for_selector("div[class$='grid'][class^='SearchPage']")
        self.__page_down(self.page)
        self.page.wait_for_selector("text=Вперед")

        search_result = self.page.query_selector("div[class $='grid'][class ^='SearchPage']")
        cards = search_result.query_selector_all("article[class ^='ProductCard-module']")
        print(f'найдено товаров: {len(cards)}')

        for count, card in enumerate(cards):
            try:
                title_el = card.query_selector("h3")
                title = title_el.inner_text().strip() if title_el else "Название не найдено"

                price_el = card.query_selector("[class*='priceVal']")
                price = price_el.inner_text().strip() if price_el else "Цена не указана"

                print(f"Товар №{count + 1}: {title} | Цена: {price}")

                new_product = Product.objects.create(
                    title=title,
                    price=price
                )
                if new_product.id:
                    print(f"Успешно сохранено в БД с ID: {new_product.id}")

            except Exception as e:
                print(f"ОШИБКА СОХРАНЕНИЯ: {e}")



    def __next_page(self):
        next_button = self.page.query_selector("a:has-text('Вперед'), button:has-text('Вперед')")

        is_disabled = next_button.get_attribute("disabled")
        if is_disabled is not None:
            print(">>> Кнопка пагинации заблокирована. Конец списка.")
            return False

        try:
            print("Переходим на следующую страницу...")
            next_button.click()
            self.page.wait_for_load_state("networkidle", timeout=5000)
            return True
        except Exception:
            return False

    def __page_down(self, page):
        self.page.evaluate('''async () => {
            await new Promise((resolve) => {
                const scrollStep = 200;
                const scrollInterval = 100;
                let currentPosition = 0;

                const interval = setInterval(() => {
                    const scrollHeight = document.documentElement.scrollHeight;
                    window.scrollBy(0, scrollStep);
                    currentPosition += scrollStep;

                    if (currentPosition >= scrollHeight) {
                        clearInterval(interval);
                        resolve();
                    }
                }, scrollInterval);
            });
        }''')

    def parser(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            self.context = browser.new_context()
            self.page = browser.new_page()

            self.page.goto("https://santehuspeh.by/")
            self.page.query_selector("input[class$='searchInput']").type(text=self.keyword, delay=0.3)
            self.page.click("a[class$='searchShowAll']")
            has_pages = True
            while has_pages:
                self.__get_links()
                has_pages = self.__next_page()
                time.sleep(2)
            print(f"\nВсего спаршено товаров: {len(self.list_item_name)}")
            browser.close()


if __name__ == '__main__':
    parse("душ").parser()

