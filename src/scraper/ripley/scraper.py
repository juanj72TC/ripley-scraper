from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
import pandas as pd
from src.models.ripley_response import RipleyResponse
from src.validators.date_format import validate_date_format
from src.config import Config
from src.utils.browser_manager import BrowserManager


class RipleyScraper:
    SELECTORS = {
        "username_input": "input#txtCodUsuario",
        "password_input": "input#txtPassword",
        "login_button": "input#btnLogin",
        "date_from_input": "input#txtFechaDesde",
        "date_to_input": "input#txtFechaHasta",
        "search_button": "input[value='Buscar']",
        "table_class": "DojoTable",
    }
    TIMEOUTS = {
        "default": 15000,
        "navigation": 90000,
        "network": 15000,
    }

    def __init__(self, config: Config, browser_manager: BrowserManager):
        self.config = config
        self.username = config.config["ripley"]["username"]
        self.password = config.config["ripley"]["password"]
        self.browser_manager = browser_manager

    async def run(self, date_from: str | None = None, date_to: str | None = None):
        self.browser_manager.launch_browser()
        print("Navegador iniciado...")
        browser = None
        context = None
        try:
            async with async_playwright() as p:
                connect_url = (
                    getattr(self.browser_manager, "connect_url", None)
                    or f"http://127.0.0.1:{self.browser_manager.port}"
                )

                browser = await p.chromium.connect_over_cdp(connect_url)  # ✅ await
                version = browser.version  # ✅ await
                print(f"[✅] Conectado a {version} en {connect_url}")

                context = await browser.new_context()  # ✅ await
                page = await context.new_page()  # ✅ await

                await self._do_login(page)  # ✅ await

                menu_frame = await self._search_menu_frame(page)
                await menu_frame.evaluate(
                    "() => executeActividad('1348','portal/comercial/consulta/ConsDetalladaVentasSinStockBuscar.do')"
                )

                target_frame = await self._search_target_frame(page)
                await target_frame.wait_for_load_state("load")

                html_content = await self._fill_input_dates(
                    target_frame,
                    date_from=date_from or "01-07-2025",
                    date_to=date_to or "31-07-2025",
                )

                soup = BeautifulSoup(html_content, "html.parser")
                table = soup.find("table", class_=self.SELECTORS["table_class"])
                if not table:
                    print("[❌] No se encontró la tabla DojoTable.")
                    return []

                df = pd.read_html(str(table), header=1)[0]
                df.to_csv("src/artifacts/exports/ripley_data.csv", index=False)
                return self.convert_to_ripley_response(df)

        except TimeoutError:
            if context:
                try:
                    page = context.pages[-1]
                    await page.screenshot(
                        path="src/artifacts/screenshots/brave_timeout.png"
                    )
                except Exception:
                    pass
            print("[❌] Timeout durante el flujo.")
            return []
        finally:
            try:
                if context:
                    await context.close()
            except Exception:
                pass
            try:
                if browser:
                    await browser.close()  # ✅ await
            except Exception:
                pass
            self.browser_manager.terminate_browser()

    # --- Métodos privados async ---

    async def _do_login(self, page):
        print("[*] Iniciando sesión en Ripley...")
        await page.goto(
            "https://b2b.ripley.cl/b2bWeb/portal/logon.do",
            timeout=self.TIMEOUTS["navigation"],
        )
        await page.screenshot(path="src/artifacts/screenshots/first_frame.png")
        await page.wait_for_selector(self.SELECTORS["username_input"], timeout=60000)
        await page.fill(self.SELECTORS["username_input"], self.username)
        await page.fill(self.SELECTORS["password_input"], self.password)
        print("Datos ingresados")
        await page.click(self.SELECTORS["login_button"])
        await page.wait_for_load_state("networkidle", timeout=self.TIMEOUTS["network"])
        await page.screenshot(path="src/artifacts/screenshots/brave_post_login.png")
        print("[✅] ¡Login exitoso!")

    async def _search_menu_frame(self, page):
        for frame in page.frames:
            if "setProveedor.do" in (frame.url or ""):
                return frame
        raise RuntimeError("No se encontró el frame del menú (setProveedor.do).")

    async def _search_target_frame(self, page):
        for _ in range(40):  # ~20s
            for f in page.frames:
                u = f.url or ""
                if "ConsDetalladaVentasSinStockBuscar.do" in u:
                    return f
            await page.wait_for_timeout(500)
        raise RuntimeError("No se encontró el frame del formulario de ventas.")

    async def _fill_input_dates(self, target_frame, date_from: str, date_to: str):
        if not validate_date_format(date_from) or not validate_date_format(date_to):
            raise ValueError("El formato de las fechas debe ser DD-MM-YYYY")

        await target_frame.wait_for_selector(
            self.SELECTORS["date_from_input"], timeout=10000
        )
        await target_frame.wait_for_selector(
            self.SELECTORS["date_to_input"], timeout=10000
        )

        await target_frame.fill(self.SELECTORS["date_from_input"], date_from)
        await target_frame.fill(self.SELECTORS["date_to_input"], date_to)

        await target_frame.click(self.SELECTORS["search_button"])
        await target_frame.wait_for_load_state("networkidle", timeout=20000)

        return await target_frame.content()

    def convert_to_ripley_response(self, data: pd.DataFrame) -> list[RipleyResponse]:
        responses = []
        for _, row in data.iterrows():
            responses.append(
                RipleyResponse(
                    fecha=row["Fecha"],
                    cod_art_ripley=row["Cód.Art. Ripley"],
                    upc=row.get("UPC"),
                    desc_art_ripley=row["Desc.Art. Ripley"],
                    cod_art_prov_case_pack=row["Cód.Art.Prov. (Case Pack)"],
                    desc_art_prov_case_pack=row["Desc.Art.Prov.(Case Pack)"],
                    sucursal=row["Sucursal"],
                    venta_u=row["Venta (u)"],
                    venta_pesos=row["Venta ($)"],
                    costo_de_venta_pesos=row["Costo De Venta($)"],
                    mark_up=row["Mark-up"],
                    marca=row["Marca"],
                    temp=row["Temp."],
                )
            )
        return responses
