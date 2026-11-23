
from urllib.parse import quote_plus, urlparse

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


class JobSearchError(Exception):
    """Error controlado durante la búsqueda de ofertas laborales."""


def get_source(url):
    hostname = (urlparse(url).hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    portals = {
        "computrabajo.com": "Computrabajo",
        "indeed.com": "Indeed",
        "linkedin.com": "LinkedIn",
        "jooble.org": "Jooble",
        "chiletrabajos.cl": "Chiletrabajos",
        "trabajando.cl": "Trabajando.com",
        "laborum.cl": "Laborum",
        "trabajosdiarios.com": "Trabajos Diarios",
        "opcionempleo.cl": "Opción Empleo",
        "infojobs.net": "InfoJobs",
    }

    for domain, name in portals.items():
        if hostname == domain or hostname.endswith("." + domain):
            return name

    return hostname or "Portal desconocido"


def is_general_search_page(url, title):
    path = urlparse(url).path.lower()
    title = (title or "").lower()

    general_paths = (
        "/q-",
        "/trabajo-",
        "/trabajos-",
        "/empleos-",
        "/encuentra-un-empleo",
        "/ofertas-trabajo",
        "/trabajo/",
    )

    general_words = (
        "bolsa de trabajo",
        "ofertas de empleo",
        "empleos de",
        "trabajos de",
        "ofertas de trabajo",
    )

    return (
        any(path.startswith(prefix) for prefix in general_paths)
        or any(word in title for word in general_words)
    )


def search_jobs(role, location="Chile", commune="", work_mode=""):
    role = (role or "").strip()

    if not role:
        raise JobSearchError(
            "Debes indicar el cargo que deseas buscar."
        )

    location = (location or "").strip()
    commune = (commune or "").strip()
    work_mode = (work_mode or "").strip()

    query_parts = [role, "empleo", "trabajo"]

    if commune:
        query_parts.append(commune)

    if location:
        query_parts.append(location)

    if work_mode:
        query_parts.append(work_mode)

    query_parts.append("Chile")

    query = " ".join(query_parts)

    search_url = (
        f"https://duckduckgo.com/?q={quote_plus(query)}"
    )

    results = []
    seen_urls = set()

    try:
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=False,
                args=[
                    "--start-minimized",
                    "--window-position=-32000,-32000",
                    "--window-size=1200,800",
                ],
            )

            try:
                page = browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/131.0.0.0 Safari/537.36"
                    )
                )

                page.set_default_timeout(30000)

                page.goto(
                    search_url,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

                page.wait_for_selector(
                    "a[data-testid='result-title-a']",
                    state="visible",
                    timeout=30000,
                )

                links = page.locator(
                    "a[data-testid='result-title-a']"
                )

                for index in range(min(links.count(), 10)):
                    link = links.nth(index)

                    title = link.inner_text().strip()
                    result_url = link.get_attribute("href")

                    if not title or not result_url:
                        continue

                    parsed = urlparse(result_url)

                    if parsed.scheme not in ("http", "https"):
                        continue

                    if not parsed.hostname:
                        continue

                    if parsed.hostname.lower().endswith(
                        "duckduckgo.com"
                    ):
                        continue

                    normalized_url = (
                        result_url.rstrip("/").lower()
                    )

                    if normalized_url in seen_urls:
                        continue

                    seen_urls.add(normalized_url)

                    is_general = is_general_search_page(
                        result_url,
                        title,
                    )

                    results.append({
                        "title": title,
                        "url": result_url,
                        "source": get_source(result_url),
                        "description": "",
                        "result_type": (
                            "Página general de empleos"
                            if is_general
                            else "Posible oferta individual"
                        ),
                        "is_general": is_general,
                    })

            finally:
                browser.close()

    except PlaywrightTimeoutError as exc:
        raise JobSearchError(
            "DuckDuckGo no mostró resultados dentro de 30 segundos. "
            "Puede estar limitando la búsqueda automatizada. "
            "Inténtalo nuevamente."
        ) from exc

    except Exception as exc:
        raise JobSearchError(
            f"No fue posible completar la búsqueda: {exc}"
        ) from exc

    if not results:
        raise JobSearchError(
            "DuckDuckGo no devolvió enlaces de empleo. "
            "Prueba con otro cargo o ubicación."
        )

    return results
