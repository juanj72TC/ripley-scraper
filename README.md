# ripley scraper
	ripley scraper de pruebas, uso de playwright con navegador de entorno real

## Requisitos
	- python 3.12
	- poetry 1.7.1
	- navegador brave instalado

### pasos
	- iniciar el navegador brave en modo debug:
	```bash
	brave --remote-debugging-port=9222 --user-data-dir=/tmp/brave-playwright # usar la ruta respectiva en el equipo
	```
	- ejecutar el entorno para inicio de sesion
		```bash
	#1
	poetry shell
	#2
	poetry install
	#3
	uvicorn main:app --reload
	```

### Documentación adicional
	- actualmente el proyecto burla el captha e inicia sesion en la plataforma con navegador directo del sistema operativo en modo "-- no headless"

