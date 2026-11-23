
import base64
import os
from pathlib import Path
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailServiceError(Exception):
    pass


def create_oauth_flow(state=None, code_verifier=None):
    if not CREDENTIALS_FILE.exists():
        raise GmailServiceError(
            "No se encontró credentials.json en la carpeta principal de PostulaAI."
        )

    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        state=state,
        code_verifier=code_verifier
    )

    flow.redirect_uri = "http://127.0.0.1:5000/gmail/callback"
    return flow


def save_credentials(credentials):
    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8"
    )


def get_credentials():
    if not TOKEN_FILE.exists():
        return None

    credentials = Credentials.from_authorized_user_file(
        str(TOKEN_FILE),
        SCOPES
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(credentials)

    if not credentials.valid:
        return None

    return credentials


def get_gmail_service():
    credentials = get_credentials()

    if not credentials:
        raise GmailServiceError(
            "Gmail no está conectado. Autoriza primero tu cuenta."
        )

    return build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False
    )


def decode_message_body(payload):
    """Extract readable text from a Gmail message."""

    parts = payload.get("parts", [])

    if parts:
        for part in parts:
            result = decode_message_body(part)
            if result:
                return result

    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data")

        if data:
            decoded = base64.urlsafe_b64decode(data)
            return decoded.decode("utf-8", errors="replace")

    return ""


def classify_email(subject, body):
    text = f"{subject} {body}".lower()

    interview_words = [
        "entrevista", "interview", "reunión", "reunion",
        "selección", "seleccion", "agenda una entrevista"
    ]

    rejection_words = [
        "no hemos seleccionado", "no fuiste seleccionado",
        "no has sido seleccionado", "rechazamos tu candidatura",
        "regrettably", "not selected", "unfortunately"
    ]

    information_words = [
        "información adicional", "informacion adicional",
        "documentos", "antecedentes", "disponibilidad",
        "additional information", "please provide"
    ]

    if any(word in text for word in rejection_words):
        return "Rechazo"

    if any(word in text for word in interview_words):
        return "Entrevista"

    if any(word in text for word in information_words):
        return "Solicitud de información"

    return "Otra respuesta"


def get_recent_emails(max_results=50):
    service = get_gmail_service()

    response = service.users().messages().list(
        userId="me",
        q="newer_than:90d {entrevista interview postulación postulacion candidatura empleo selección seleccion recruiter recruiting}",
        maxResults=max_results
    ).execute()

    messages = response.get("messages", [])
    emails = []

    for message in messages:
        detail = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = detail.get("payload", {})
        headers = payload.get("headers", [])

        header_values = {
            item["name"].lower(): item["value"]
            for item in headers
        }

        subject = header_values.get("subject", "(Sin asunto)")
        sender = header_values.get("from", "")
        date = header_values.get("date", "")

        body = decode_message_body(payload)

        if not body:
            body = payload.get("snippet", "")

        emails.append({
            "gmail_id": message["id"],
            "sender": sender,
            "subject": subject,
            "body": body[:12000],
            "preview": body[:500],
            "category": classify_email(subject, body),
            "date": date
        })

    return emails
