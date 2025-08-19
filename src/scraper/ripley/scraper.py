from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
import pandas as pd
from src.models.ripley import RipleyResponse, RipleyCredentials, StockResponseRipley
from src.validators.date_format import validate_date_format
from src.config import Config
from src.utils.browser_manager import BrowserManager
from io import StringIO


class RipleyScraper:
    SELECTORS = {
        "username_input": "input#txtCodUsuario",
        "password_input": "input#txtPassword",
        "login_button": "input#btnLogin",
        "date_from_input": "input#txtFechaDesde",
        "date_to_input": "input#txtFechaHasta",
        "search_button": "input[value='Buscar']",
        "table_class": "DojoTable",
        "checkbox_upc": "input[name='chkConCodigoUpc']",
        "checkbox_salida_archivo": "input[name='chkFile']",
    }
    BASE_URL = "https://b2b.ripley.cl"
    TIMEOUTS = {
        "default": 10000,
        "navigation": 90000,
        "network": 15000,
    }

    def __init__(self, config: Config, browser_manager: BrowserManager):
        self.config = config

        self.browser_manager = browser_manager

    async def run(
        self,
        ripley_credentials: RipleyCredentials,
        date_from: str | None = None,
        date_to: str | None = None,
    ):
        # self.browser_manager.launch_browser()
        print("Navegador iniciado...")
        browser = None
        context = None
        try:
            async with async_playwright() as p:
                # TODO: Validar que el navegador siempre este en ejecución
                # connect_url = (
                #     getattr(self.browser_manager, "connect_url", None)
                #     or f"http://127.0.0.1:{self.browser_manager.port}"
                # )
                connect_url = "http://127.0.0.1:9222"

                browser = await p.chromium.connect_over_cdp(connect_url)
                version = browser.version
                print(f"[✅] Conectado a {version} en {connect_url}")

                context = await browser.new_context()
                page = await context.new_page()

                await self._do_login(page, ripley_credentials)

                menu_frame = await self._search_menu_frame(page)
                match ripley_credentials.type_report:
                    case ripley_credentials.TypeReport.sales:
                        response = await self._sales_process(
                            menu_frame, page, date_from, date_to
                        )
                        return pd.DataFrame(response)

                    case ripley_credentials.TypeReport.stock:
                        response = await self._stock_process(menu_frame, page)
                        return pd.DataFrame(response)

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

    # --- Métodos privados async ---

    async def _sales_process(self, menu_frame, page, date_from, date_to):

        await menu_frame.evaluate(
            "() => executeActividad('1274','portal/comercial/consulta/ConsDetalladaVentasBuscar.do')"
        )

        target_frame = await self._search_target_frame(page, "Ventas")
        await target_frame.wait_for_load_state("load")

        target_frame = await self._fill_input_dates(
            target_frame,
            date_from=date_from or "01-07-2025",
            date_to=date_to or "31-07-2025",
        )
        return await self._get_data(target_frame,1)

    async def _stock_process(self, menu_frame, page):
        await menu_frame.evaluate(
            "() => executeActividad('1268','portal/comercial/consulta/ConsDetalladaStockBuscar.do')"
        )
        target_frame = await self._search_target_frame(page, "Stock")
        await target_frame.wait_for_load_state("load")
        await target_frame.click(self.SELECTORS["search_button"])
        await target_frame.wait_for_load_state("networkidle", timeout=20000)
        await target_frame.select_option("select[name='pageSize']", "200")
        await target_frame.wait_for_timeout(self.TIMEOUTS["default"])
        return await self._get_data(target_frame)

    async def _get_all_items_selector(self, target_frame, name_selector: str):
        options = await target_frame.eval_on_selector_all(
            f"select[name='{name_selector}'] option",
            "elements => elements.map(el => ({value: el.value, text: el.textContent.trim()}))",
        )
        return options, len(options)

    async def _get_data(self, target_frame, header: int = 0):
        options, len_ = await self._get_all_items_selector(target_frame, "pag")
        dataframes = []
        if len_ == 0:
            return []
        if len_ > 1:
            for option in options:
                await target_frame.select_option(
                    "select[name='pag']", option.get("value")
                )
                await target_frame.wait_for_timeout(self.TIMEOUTS["default"])
                dataframes.append(
                    self.convert_to_dataframe(await target_frame.content(),header)
                )
            return pd.concat(dataframes, ignore_index=True)
        if len_ == 1:
            # await target_frame.select_option(
            #     "select[name='pag']", options[0].get("value")
            # )
            await target_frame.wait_for_timeout(self.TIMEOUTS["default"])
            return self.convert_to_dataframe(await target_frame.content())

    def convert_to_dataframe(self, html_content, header: int = 0):
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_=self.SELECTORS["table_class"])
        if not table:
            print("[❌] No se encontró la tabla DojoTable.")
            return []

        df = pd.read_html(StringIO(str(table)), header=header)[0]
        return df

    async def _do_login(self, page, ripley_credentials: RipleyCredentials):
        print("[*] Iniciando sesión en Ripley...")
        await page.goto(
            "https://b2b.ripley.cl/b2bWeb/portal/logon.do",
            timeout=self.TIMEOUTS["navigation"],
        )
        await page.screenshot(path="src/artifacts/screenshots/first_frame.png")
        await page.wait_for_selector(self.SELECTORS["username_input"], timeout=60000)
        await page.fill(self.SELECTORS["username_input"], ripley_credentials.username)
        await page.fill(self.SELECTORS["password_input"], ripley_credentials.password)
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

    async def _search_target_frame(self, page, detail_report: str):
        for _ in range(40):  # ~20s
            for f in page.frames:
                u = f.url or ""
                if f"ConsDetallada{detail_report}Buscar.do" in u:
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
        await target_frame.check(self.SELECTORS["checkbox_upc"])
        # await target_frame.check(self.SELECTORS["checkbox_salida_archivo"])

        await target_frame.fill(self.SELECTORS["date_from_input"], date_from)
        await target_frame.fill(self.SELECTORS["date_to_input"], date_to)

        await target_frame.click(self.SELECTORS["search_button"])
        await target_frame.wait_for_load_state("networkidle", timeout=20000)
        await target_frame.select_option("select[name='pageSize']", "200")
        await target_frame.wait_for_timeout(self.TIMEOUTS["default"])

        return target_frame

    def convert_to_ripley_response(self, data: pd.DataFrame) -> list[RipleyResponse]:
        responses = []
        for _, row in data.iterrows():
            responses.append(
                RipleyResponse(
                    cod_art_ripley=row.get("Cód.Art. Ripley"),
                    upc=row.get("UPC"),
                    desc_art_ripley=row.get("Desc.Art. Ripley"),
                    cod_art_prov_case_pack=row.get("Cód.Art.Prov. (Case Pack)"),
                    desc_art_prov_case_pack=row.get("Desc.Art.Prov.(Case Pack)"),
                    sucursal=row.get("Sucursal"),
                    venta_u=row.get("Venta (u)"),
                    venta_pesos=row.get("Venta ($)"),
                    transfer_on_order_u=row.get("Transfer. on Order(u)"),
                    transfer_on_order_pesos=row.get("Transfer. on Order($)"),
                    stock_on_hand_disponible_u=row.get("Stock on Hand Disponible (u)"),
                    stock_on_hand_disponible_pesos=row.get(
                        "Stock on Hand Disponible ($)"
                    ),
                    costo_de_venta_pesos=row.get("Costo De Venta($)"),
                    mark_up=row.get("Mark-up"),
                    marca=row.get("Marca"),
                    temp=row.get("Temp."),
                )
            )
        return responses

    def _convert_to_stock_response(self, data: pd.DataFrame):
        responses = []
        for _, row in data.iterrows():
            responses.append(
                StockResponseRipley(
                    sucursal=row.get("Sucursal"),
                    marca=row.get("Marca"),
                    dpto=row.get("Dpto."),
                    linea=row.get("Línea"),
                    cod_art_ripley=row.get("Cód. Art. Ripley"),
                    desc_art_ripley=row.get("Desc. Art. Ripley"),
                    cod_art_prov_case_pack=row.get("Cód. Art. Prov. (Case Pack)"),
                    desc_art_prov_case_pack=row.get("Desc. Art. Prov. (Case Pack)"),
                    transfer_on_order_u=row.get("Tranfer. on order (u)"),
                    transfer_on_order_pesos=row.get("Tranfer. on order ($)"),
                    stock_on_hand_disponible_u=row.get("Stock on Hand Disponible(u)"),
                    stock_on_hand_disponible_pesos=row.get(
                        "Stock on Hand Disponible($)"
                    ),
                    stock_on_hand_empresa_u=row.get("Stock on hand empresa(u)"),
                    stock_on_hand_empresa_pesos=row.get("Stock on hand empresa($)"),
                    stock_protegido_u=row.get("Stock Protegido(u)"),
                    stock_pdte_por_oc_u=row.get("Stock Pdte por OC (u)"),
                )
            )
        return responses
