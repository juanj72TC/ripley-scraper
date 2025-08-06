from playwright.sync_api import sync_playwright, TimeoutError
from src.config import Config

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

                # Validar si el login fue exitoso
                if "logon.do" not in page.url:
                    print("[✅] ¡Login exitoso!")
                else:
                    print("[❌] Login fallido. Verifica credenciales o captcha.")

                # Guardar estado para depuración
                page.screenshot(path="brave_post_login.png")
                print("[📷] Captura guardada como 'brave_post_login.png'")

                with open("brave_post_login.html", "w", encoding="utf-8") as f:
                    f.write(page.content())

            except TimeoutError:
                print("[❌] Timeout: el campo de login no apareció.")
                page.screenshot(path="brave_timeout.png")
                print("[📷] Captura guardada como 'brave_timeout.png'")

            browser.close()
