# gc_service.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os, json

TZ = ZoneInfo("America/Guayaquil")

class GoogleService:
    def __init__(self, creds_file: str = "credentials.json"):

        creds_env = os.getenv("GOOGLE_CREDENTIALS_JSON")

        if creds_env:
            try:
                creds_env = creds_env.replace("\\n", "\n")
                info = json.loads(creds_env)

                creds = service_account.Credentials.from_service_account_info(
                    info,
                    scopes=["https://www.googleapis.com/auth/calendar"]
                )
                print("🔐 Usando credenciales desde variable de entorno (Render).")

            except Exception as e:
                raise Exception(f"❌ Error cargando GOOGLE_CREDENTIALS_JSON: {e}")

        else:
            try:
                creds = service_account.Credentials.from_service_account_file(
                    creds_file,
                    scopes=["https://www.googleapis.com/auth/calendar"]
                )
                print("📄 Usando credenciales locales desde credentials.json.")

            except Exception as e:
                raise Exception(
                    f"❌ No se pudo cargar credentials.json.\n"
                    f"Error: {e}\nAsegúrate que el archivo existe o define GOOGLE_CREDENTIALS_JSON."
                )

        self.service = build("calendar", "v3", credentials=creds)

    # ------------------------------------------------------------------
    # VERIFICAR SI YA HAY EVENTO EN EL MISMO HORARIO
    # ------------------------------------------------------------------
    def existe_evento(self, calendar_id, inicio, fin):
        try:
            eventos = self.service.events().list(
                calendarId=calendar_id,
                timeMin=inicio.isoformat(),
                timeMax=fin.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute().get("items", [])
            return len(eventos) > 0

        except Exception as e:
            print("❌ Error verificando conflicto:", e)
            return False

    # ------------------------------------------------------------------
    # CREAR EVENTO EN GOOGLE CALENDAR
    # ------------------------------------------------------------------
    def crear_evento(self, calendar_id, resumen, descripcion, inicio, fin, timezone="America/Guayaquil"):
        try:
            evento = {
                "summary": resumen,
                "description": descripcion,
                "start": {
                    "dateTime": inicio.isoformat(),
                    "timeZone": timezone
                },
                "end": {
                    "dateTime": fin.isoformat(),
                    "timeZone": timezone
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [{"method": "popup", "minutes": 30}]
                }
            }

            self.service.events().insert(
                calendarId=calendar_id,
                body=evento
            ).execute()

            print(f"✅ Evento creado correctamente: {resumen}")

        except Exception as e:
            raise Exception(f"❌ Error creando evento en Google Calendar: {e}")
