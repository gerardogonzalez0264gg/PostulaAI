"""Safely fetch and extract publicly accessible job-offer pages."""
from ipaddress import ip_address
from urllib.parse import urlparse
import socket
import requests
from bs4 import BeautifulSoup

class OfferFetchError(Exception):
    pass

def _validate_public_url(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise OfferFetchError("El enlace debe ser una URL pública válida con http:// o https://.")
    if parsed.port and parsed.port not in {80, 443}:
        raise OfferFetchError("Por seguridad, solo se permiten puertos web estándar.")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise OfferFetchError("No se pudo encontrar el servidor de esa oferta.") from exc
    for item in addresses:
        if not ip_address(item[4][0]).is_global:
            raise OfferFetchError("Por seguridad, no se permiten enlaces a redes privadas o direcciones locales.")
    return url.strip()

def extract_offer_text(url: str) -> str:
    safe_url = _validate_public_url(url)
    try:
        response = requests.get(safe_url, headers={"User-Agent": "PostulaAI/0.1"}, timeout=(5, 12), allow_redirects=False, stream=True)
    except requests.RequestException as exc:
        raise OfferFetchError("No se pudo acceder al enlace. Puedes pegar la descripción manualmente.") from exc
    with response:
        if response.is_redirect:
            raise OfferFetchError("El portal redirige el enlace. Abre la oferta y pega su descripción en PostulaAI.")
        if response.status_code >= 400:
            raise OfferFetchError("El portal no permitió acceder a la oferta. Puedes pegar su descripción manualmente.")
        if "text/html" not in response.headers.get("Content-Type", "").lower():
            raise OfferFetchError("El enlace no contiene una página HTML compatible.")
        chunks, total = [], 0
        for chunk in response.iter_content(65536):
            total += len(chunk)
            if total > 1_500_000:
                raise OfferFetchError("La página es demasiado grande para analizarla automáticamente.")
            chunks.append(chunk)
    soup = BeautifulSoup(b"".join(chunks), "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        element.decompose()
    for element in soup.select("[aria-hidden='true'], .cookie, .advertisement, .ads"):
        element.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = " ".join(" ".join(main.stripped_strings).split())
    if len(text) < 250:
        raise OfferFetchError("No encontramos suficiente información. Pega la descripción de la oferta manualmente.")
    if title and title not in text[:250]:
        text = f"Título de la página: {title}. " + text
    return text[:20000]
