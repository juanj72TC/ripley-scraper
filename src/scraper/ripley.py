from playwright.sync_api import sync_playwright, TimeoutError
from src.config import Config
import time


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

                # Guardar estado después del login
                page.screenshot(path="brave_post_login.png")
                print("[📷] Captura guardada como 'brave_post_login.png'")

                print("[✅] ¡Login exitoso!")

                # 🔁 Esperar hasta que cargue el frame del menú
                print("[*] Esperando el frame del menú...")
                menu_frame = None
                # timeout = time.time() + 10  # Espera máxima: 10s
                # while time.time() < timeout:
                for frame in page.frames:
                    print(f"[DEBUG] Frame encontrado: {frame.url}")

                    if "setProveedor.do" in frame.url:

                        frame.evaluate(
                            "() => executeActividad('1348', 'portal/comercial/consulta/ConsDetalladaVentasSinStockBuscar.do')"
                        )
                        for _ in range(20):
                            for f in page.frames:
                                if "ConsDetalladaVentasSinStockBuscar.do" in f.url:
                                    f.wait_for_load_state("networkidle")

                                    
                                    break

                        break

                page.wait_for_timeout(500)

            except TimeoutError:
                print("[❌] Timeout: el campo de login no apareció.")
                page.screenshot(path="brave_timeout.png")
                print("[📷] Captura guardada como 'brave_timeout.png'")
