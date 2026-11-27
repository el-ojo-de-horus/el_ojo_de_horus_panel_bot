import os
import re
import datetime
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import requests

# ─── CONFIGURACIÓN FIREBASE ───
if not firebase_admin._apps:
    cred_path = "firebase-credentials.json"
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        raise RuntimeError("No se encontró firebase-credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

VZLA_TZ = datetime.timezone(datetime.timedelta(hours=-4))
COLECCION_RESULTADOS = "resultados_diarios"
URL_LOTOVEN = "https://lotoven.com/animalitos/"

ANIMALITOS = {
    "0": "Delfín", "00": "Ballena", "1": "Carnero", "2": "Toro", "3": "Ciempiés",
    "4": "Alacrán", "5": "León", "6": "Rana", "7": "Perico", "8": "Ratón",
    "9": "Águila", "10": "Tigre", "11": "Gato", "12": "Caballo", "13": "Mono",
    "14": "Paloma", "15": "Zorro", "16": "Oso", "17": "Pavo", "18": "Burro",
    "19": "Chivo", "20": "Cochino", "21": "Gallo", "22": "Camello", "23": "Cebra",
    "24": "Iguana", "25": "Gallina", "26": "Vaca", "27": "Perro", "28": "Zamuro",
    "29": "Elefante", "30": "Caimán", "31": "Lapa", "32": "Ardilla", "33": "Pescado",
    "34": "Venado", "35": "Jirafa", "36": "Culebra"
}

MESES = {
    "january": 1, "enero": 1,
    "february": 2, "febrero": 2,
    "march": 3, "marzo": 3,
    "april": 4, "abril": 4,
    "may": 5, "mayo": 5,
    "june": 6, "junio": 6,
    "july": 7, "julio": 7,
    "august": 8, "agosto": 8,
    "september": 9, "septiembre": 9,
    "october": 10, "octubre": 10,
    "november": 11, "noviembre": 11,
    "december": 12, "diciembre": 12,
}

HORAS_SORTEO = [
    "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM",
    "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM",
    "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-VE,es;q=0.9,en;q=0.8",
}

RE_FECHA_LOTOVEN = re.compile(
    r"\b(\d{1,2})\s+de\s+([A-Za-zÁÉÍÓÚáéíóú]+)\s+de\s+(20\d{2})\b",
    re.IGNORECASE,
)

# Captura: <numero 00..36> <texto corto del animal> <hora 08:00 AM .. 07:00 PM>
RE_SORTEO = re.compile(
    r"(?<!\d)(00|[0-3]?\d)\s+([A-Za-zÁÉÍÓÚáéíóúÑñ\s-]{2,25}?)\s+(0?[89]:00\s*AM|1[01]:00\s*AM|12:00\s*PM|0?[1-7]:00\s*PM)\b",
    re.IGNORECASE,
)


def fecha_vzla_str() -> str:
    return datetime.datetime.now(VZLA_TZ).strftime("%Y-%m-%d")


def detectar_fecha_en_bloque(bloque: str) -> str | None:
    m = RE_FECHA_LOTOVEN.search(bloque)
    if not m:
        return None
    dia = int(m.group(1))
    mes_nombre = m.group(2).lower()
    anio = int(m.group(3))
    mes = MESES.get(mes_nombre)
    if not mes:
        return None
    try:
        return datetime.date(anio, mes, dia).isoformat()
    except ValueError:
        return None


def normalizar_hora(hora_raw: str) -> str:
    limpia = re.sub(r"\s+", " ", hora_raw.strip().upper())
    if re.match(r"^[89]:00\s*AM$", limpia) or re.match(r"^[1-7]:00\s*PM$", limpia):
        return "0" + limpia
    return limpia


def normalizar_numero(num_raw: str):
    n = num_raw.strip()
    if n == "00":
        return "00"
    if n.isdigit():
        val = int(n)
        if 0 <= val <= 36:
            return str(val)
    return None


def extraer_bloque_ruleta(texto: str, inicio_marcador: str, fin_marcadores: list):
    idx_inicio = texto.find(inicio_marcador)
    if idx_inicio == -1:
        return {}, None, ""

    subtexto = texto[idx_inicio:]
    corte = len(subtexto)
    for marcador_fin in fin_marcadores:
        pos = subtexto.find(marcador_fin, len(inicio_marcador))
        if pos != -1 and pos < corte:
            corte = pos

    bloque = subtexto[:corte]
    fecha_bloque = detectar_fecha_en_bloque(bloque)
    resultados = {}

    for match in RE_SORTEO.finditer(bloque):
        num = normalizar_numero(match.group(1))
        hora = normalizar_hora(match.group(3))
        if num is not None and hora in HORAS_SORTEO and hora not in resultados:
            resultados[hora] = {
                "numero": num,
                "animal": ANIMALITOS[num],
            }

    return resultados, fecha_bloque, bloque[:320]


def actualizar_resultados():
    fecha_hoy_vzla = fecha_vzla_str()
    lotto_activo = {}
    la_granjita = {}
    fecha_publicada = None

    try:
        resp = requests.get(URL_LOTOVEN, headers=HEADERS, timeout=25)
        print(f"[LotoVen] {URL_LOTOVEN} -> HTTP {resp.status_code} ({len(resp.text)} bytes)")
        if resp.status_code == 200 and resp.text.strip():
            soup = BeautifulSoup(resp.text, "html.parser")
            texto_plano = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

            lotto_activo, fecha_la, muestra_la = extraer_bloque_ruleta(
                texto_plano,
                "Resultados Lotto Activo",
                ["Resultados La Granjita", "Resultados Lotto Activo 2"],
            )
            la_granjita, fecha_lg, muestra_lg = extraer_bloque_ruleta(
                texto_plano,
                "Resultados La Granjita",
                ["Resultados Lotto Activo 2", "Resultados Guacharo Activo"],
            )
            fecha_publicada = fecha_la or fecha_lg

            if not lotto_activo:
                print(f"[Debug LottoActivo] Muestra texto: {muestra_la}")
            if not la_granjita:
                print(f"[Debug LaGranjita] Muestra texto: {muestra_lg}")
    except Exception as exc:
        print(f"[LotoVen] Error consultando {URL_LOTOVEN}: {exc}")

    fecha_destino = fecha_publicada or fecha_hoy_vzla
    doc_ref = db.collection(COLECCION_RESULTADOS).document(fecha_destino)
    payload = {"fecha": fecha_destino}

    if lotto_activo:
        payload["lotto_activo"] = lotto_activo
    if la_granjita:
        payload["la_granjita"] = la_granjita

    doc_ref.set(payload, merge=True)

    print(f"📅 Fecha reloj Venezuela: {fecha_hoy_vzla} | Fecha publicada LotoVen: {fecha_destino}")
    print(f"🎰 Lotto Activo extraídos: {len(lotto_activo)} -> {lotto_activo}")
    print(f"🐾 La Granjita extraídos: {len(la_granjita)} -> {la_granjita}")


if __name__ == "__main__":
    actualizar_resultados()
