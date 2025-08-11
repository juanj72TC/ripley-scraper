import subprocess
import time


class BrowserManager:
    def __init__(
        self,
    ):
        self.subprocess_ = subprocess

    def launch_browser(self):
        print("[*] Lanzando Brave en modo depuración...")
        self.subprocess_.Popen(
            [
                "brave",
                "--remote-debugging-port=9222",
                "--user-data-dir=/tmp/brave-playwright",
            ]
        )
        time.sleep(5)
        print("[✅] Brave lanzado.")

    def terminate_browser(self):
        print("[*] Terminando proceso de Brave...")
        self.subprocess_.Popen(
            ["pkill", "-f", "brave.*--remote-debugging-port=9222"]
        )
        print("[✅] Proceso de Brave terminado.")
