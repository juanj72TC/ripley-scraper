from playwright.sync_api import sync_playwright, TimeoutError
from src.config import Config
import pandas as pd
from bs4 import BeautifulSoup


class RipleyScraper:
    def __init__(self, config: Config):
        self.config = config
        self.username = config.config["ripley"]["username"]
        self.password = config.config["ripley"]["password"]

    def run(self):
        with sync_playwright() as p:
            print("[*] Conectando a Brave en http://localhost:9222...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.new_page()

            try:
                print("[*] Navegando a la página de login de Ripley...")
                page.goto("https://b2b.ripley.cl/b2bWeb/portal/logon.do", timeout=90000)

                print("[*] Esperando que aparezca el campo de usuario...")
                page.wait_for_selector("input#txtCodUsuario", timeout=60000)

                print("[*] Ingresando credenciales...")
                page.fill("input#txtCodUsuario", self.username)
                page.fill("input#txtPassword", self.password)

                print("[*] Enviando formulario...")
                page.click("input#btnLogin")

                # Esperar redirección o validación del login
                page.wait_for_load_state("networkidle", timeout=15000)

                page.screenshot(path="brave_post_login.png")
                print("[📷] Captura guardada como 'brave_post_login.png'")
                print("[✅] ¡Login exitoso!")

                # Buscar el frame del menú
                menu_frame = None
                for frame in page.frames:
                    if "setProveedor.do" in frame.url:
                        menu_frame = frame
                        break

                if not menu_frame:
                    print("[❌] No se encontró el frame del menú.")
                    return

                print("[*] Ejecutando actividad dentro del frame del menú...")
                menu_frame.evaluate(
                    "() => executeActividad('1348', 'portal/comercial/consulta/ConsDetalladaVentasSinStockBuscar.do')"
                )

                # Esperar a que se cargue el frame con el formulario
                target_frame = None
                for _ in range(20):
                    for f in page.frames:
                        if "ConsDetalladaVentasSinStockBuscar.do" in f.url:
                            target_frame = f
                            break
                    if target_frame:
                        break
                    page.wait_for_timeout(500)

                if not target_frame:
                    print("[❌] No se encontró el frame del formulario.")
                    return

                print(f"[✅] Frame del formulario cargado: {target_frame.url}")
                target_frame.wait_for_load_state("load")

                # Esperar y llenar los campos de fecha
                print("[*] Esperando inputs de fechas...")
                target_frame.wait_for_selector("input#txtFechaDesde", timeout=10000)
                target_frame.wait_for_selector("input#txtFechaHasta", timeout=10000)

                target_frame.fill("input#txtFechaDesde", "01-07-2025")
                target_frame.fill("input#txtFechaHasta", "31-07-2025")

                print("[*] Haciendo clic en Buscar...")
                target_frame.click("input[value='Buscar']")
                target_frame.wait_for_load_state("networkidle", timeout=15000)
                print(target_frame.content())
                # Extraer la tabla con pandas

                html = target_frame.content()
                soup = BeautifulSoup(html, "html.parser")
                table = soup.find("table", class_="DojoTable")

                if table:
                    df = pd.read_html(str(table), header=0)[0]
                    print(df)
                else:
                    print("[❌] No se encontró la tabla con clase 'DojoTable'.")

                print("[✅] Búsqueda enviada correctamente.")

            except TimeoutError:
                print("[❌] Timeout: el campo de login no apareció.")
                page.screenshot(path="brave_timeout.png")
                print("Captura guardada como 'brave_timeout.png'")

    def _do_login(self,page):
        pass

