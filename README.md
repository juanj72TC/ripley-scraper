# ripley scraper

 ripley scraper de pruebas, uso de playwright con navegador de entorno real, con perfil de usuario en ejecucion

 ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=for-the-badge&logo=poetry&logoColor=0B3D8D)

## Requisitos

- python 3.12
- poetry 1.7.1

### pasos

- iniciar el navegador brave en modo debug:

 ```bash
 brave --remote-debugging-port=9222 --user-data-dir=/tmp/brave-playwright # usar la ruta respectiva en el equipo
 ```

 puede ser cualquier navegador que tenga como motor base Chrome, (chromium, brave, chrome)

- ejecutar el entorno con poetry o con pip

#### poetry

 ```bash
 poetry shell
 ```

 ```bash
 poetry install
 ```

  ```bash
 uvicorn main:app --reload #--host 0.0.0.0 --port 5000 esto para en caso de querer usarlo en mdo debug y exponer la ip en la red ya sea interna o 
 ```

#### pip

 ```bash
 python -m venv venv
 ```

  ```bash
 source venv/bin/activate
 ```

  ```bash
 pip install -r requirements.txt
 ```

  ```bash
 uvicorn main:app --reload
 ```

### Documentación adicional

- actualmente el proyecto burla el captcha e inicia sesion en la plataforma con navegador directo del sistema operativo en modo "-- no headless"

- para que el flujo funcione de manera adecuada, tienes que tener instalado en wsl o linux directamente el navegador o permitir la conexion entre entornos WSL-Windows para que se pueda acceder al puerto donde se ejecuta el navegador en modo debug.
