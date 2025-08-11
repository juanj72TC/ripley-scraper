from playwright.sync_api import sync_playwright, TimeoutError
from src.config import Config
import pandas as pd
from bs4 import BeautifulSoup
from src.validators.date_format import validate_date_format
from src.models.ripley_response import RipleyResponse
from src.utils.browser_manager import BrowserManager  # debe proveer .connect_url


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

    def run(self, date_from: str | None = None, date_to: str | None = None):

        self.browser_manager.launch_browser()
        browser = None
        context = None
        try:
            with sync_playwright() as p:

                connect_url = getattr(self.browser_manager, "connect_url", None)
                if not connect_url:

                    connect_url = f"http://127.0.0.1:{self.browser_manager.port}"

                browser = p.chromium.connect_over_cdp(connect_url)

                context = browser.new_context()
                page = context.new_page()

                page = self._do_login(page)

                menu_frame = self._search_menu_frame(page)
                menu_frame.evaluate(
                    "() => executeActividad('1348','portal/comercial/consulta/ConsDetalladaVentasSinStockBuscar.do')"
                )

                target_frame = self._search_target_frame(page)
                target_frame.wait_for_load_state("load")

                html_content = self._fill_input_dates(
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
                    page.screenshot(path="src/artifacts/screenshots/brave_timeout.png")
                except Exception:
                    pass
            print("[❌] Timeout durante el flujo.")
            return []
        finally:

            try:
                if context:
                    context.close()
            except Exception:
                pass
            try:
                if browser:
                    browser.close()  # cierra la conexión CDP (no mata Brave)
            except Exception:
                pass
            self.browser_manager.terminate_browser()  # mata la instancia de Brave

    # --- Métodos privados ---

    def _do_login(self, page):
        page.goto(
            "https://b2b.ripley.cl/b2bWeb/portal/logon.do",
            timeout=self.TIMEOUTS["navigation"],
        )
        page.wait_for_selector(self.SELECTORS["username_input"], timeout=60000)
        page.fill(self.SELECTORS["username_input"], self.username)
        page.fill(self.SELECTORS["password_input"], self.password)
        page.click(self.SELECTORS["login_button"])
        page.wait_for_load_state("networkidle", timeout=self.TIMEOUTS["network"])
        page.screenshot(path="src/artifacts/screenshots/brave_post_login.png")
        print("[✅] ¡Login exitoso!")
        return page

    def _search_menu_frame(self, page):

        for frame in page.frames:
            if "setProveedor.do" in (frame.url or ""):
                return frame
        raise RuntimeError("No se encontró el frame del menú (setProveedor.do).")

    def _search_target_frame(self, page):

        for _ in range(40):  # ~20s
            for f in page.frames:
                u = f.url or ""
                if "ConsDetalladaVentasSinStockBuscar.do" in u:
                    return f
            page.wait_for_timeout(500)
        raise RuntimeError("No se encontró el frame del formulario de ventas.")

    def _fill_input_dates(self, target_frame, date_from: str, date_to: str):
        if not validate_date_format(date_from) or not validate_date_format(date_to):
            raise ValueError("El formato de las fechas debe ser DD-MM-YYYY")

        target_frame.wait_for_selector(self.SELECTORS["date_from_input"], timeout=10000)
        target_frame.wait_for_selector(self.SELECTORS["date_to_input"], timeout=10000)

        target_frame.fill(self.SELECTORS["date_from_input"], date_from)
        target_frame.fill(self.SELECTORS["date_to_input"], date_to)

        target_frame.click(self.SELECTORS["search_button"])
        # Espera a que regrese contenido (a veces recarga en el mismo frame)
        target_frame.wait_for_load_state("networkidle", timeout=20000)

        return target_frame.content()

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
