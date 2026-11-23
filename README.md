
# PostulaAI

Aplicación web local para gestionar postulaciones laborales, buscar ofertas de empleo y analizar oportunidades con inteligencia artificial.

## Características

- Búsqueda de ofertas laborales mediante DuckDuckGo.
- Filtros por palabra clave, región, comuna y modalidad.
- Análisis de ofertas laborales con inteligencia artificial.
- Generación de respuestas personalizadas para preguntas de postulación.
- Gestión del perfil profesional.
- Registro e historial de ofertas laborales.
- Seguimiento de postulaciones: revisadas y postuladas.
- Integración con Gmail mediante OAuth 2.0.
- Sincronización y clasificación de correos relacionados con postulaciones.
- Base de datos SQLite para almacenar información localmente.

## Tecnologías

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Playwright
- Google Gmail API
- OAuth 2.0
- HTML, CSS y JavaScript
- API compatible con Chat Completions

## Requisitos

- Python 3.10 o superior.
- Google Chrome o Chromium para la búsqueda de ofertas.
- Credenciales de Google OAuth para utilizar Gmail.
- API key de un proveedor compatible para utilizar las funciones de IA.

## Instalación en Windows

Clona el repositorio:

```powershell
git clone URL_DEL_REPOSITORIO
cd PostulaAI
```

Crea y activa el entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Instala el navegador de Playwright:

```powershell
python -m playwright install chromium
```

Crea el archivo de configuración:

```powershell
Copy-Item .env.example .env
```

Configura las variables necesarias en `.env`:

- `SECRET_KEY`
- `AI_API_KEY`
- `AI_BASE_URL`
- `AI_MODEL`

## Configuración de Gmail

Para utilizar la integración con Gmail:

1. Crea un proyecto en Google Cloud.
2. Habilita Gmail API.
3. Configura las credenciales OAuth 2.0.
4. Configura la URI de redirección local:
   `http://127.0.0.1:5000/gmail/callback`
5. Guarda el archivo de credenciales como `credentials.json` en la carpeta raíz del proyecto.

No publiques `credentials.json` ni `token.json`.

## Ejecución

Inicia la aplicación:

```powershell
python app.py
```

Abre en el navegador:

http://127.0.0.1:5000

## Seguridad y privacidad

- Diseñada para ejecutarse localmente.
- Las credenciales y variables privadas se almacenan en archivos excluidos de Git.
- La información de las postulaciones se guarda en una base de datos SQLite local.
- No se envían postulaciones automáticamente.
- Las respuestas generadas por IA deben revisarse antes de utilizarlas.
- No está preparada para publicarse directamente en Internet sin implementar autenticación, protección CSRF y controles de acceso adecuados.

## Estado del proyecto

Proyecto personal de desarrollo enfocado en automatización, gestión de información e inteligencia artificial aplicada a la búsqueda laboral.
