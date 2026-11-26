import os
import json
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

URL_LOTTO_ACTIVO = "https://www.lottoactivo.com/resultados/lotto_activo/"
URL_LA_GRANJITA = "https://triples.bet/products-results/granjita-results"

cred_dict = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

vzla_tz = timezone(timedelta(hours=-4))
ahora = datetime.now(vzla_tz)
fecha_hoy = ahora.strftime("%Y-%m-%d")

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

HORAS_VALIDAS = [
    "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM",
    "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM",
    "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "es-VE,es;q=0.9,en;q=0.8"
}

RE_HORA = re.compile(r"\b(0?[89]:00\s*AM|1[01]:00\s*AM|12:00\s*PM|0?[1-7]:00\s*PM)\b", re.IGNORECASE)
RE_NUMERO_ANIMAL = re.compile(r"^(00|[0-3]?\d)\b(?:\s+[A-Za-zÁÉÍÓÚÑáéíóúñ]+)?")

def normalizar_num(n):
    n = n.strip()
    if n == "00":
        return "00"
    if n.isdigit():
        val = int(n)
        if 0 <= val <= 36:
            return str(val)
    return None

def normalizar_hora(h):
    h = re.sub(r"\s+", " ", h.strip().upper())
    if re.match(r"^[89]:00\s*AM$", h):
        h = "0" + h
    return h

def buscar_numero_en_texto(texto):
    if "pendiente" in texto.lower():
        return None
    m_inicio = RE_NUMERO_ANIMAL.match(texto.strip())
    if m_inicio:
        num = normalizar_num(m_inicio.group(1))
        if num is not None and num in ANIMALITOS:
            return num
    for m in re.finditer(r"(?<!\d)(00|[0-3]?\d)(?!\d)", texto):
        num = normalizar_num(m.group(1))
        if num is not None and num in ANIMALITOS:
            fin = m.end()
            if texto[fin:fin+3] == ":00":
                continue
            return num
    return None

def extraer_sorteos_de_lineas(lineas):
    resultados = {}
    for i, linea in enumerate(lineas):
        m_hora = RE_HORA.search(linea)
        if not m_hora:
            continue

        hora = normalizar_hora(m_hora.group(1))
        if hora not in HORAS_VALIDAS or hora in resultados:
            continue

        # Revisa primero las líneas siguientes (donde viene el animalito en triples.bet) y luego las anteriores
        candidatos_contexto = [
            " ".join(lineas[i+1:min(len(lineas), i+5)]),
            linea,
            " ".join(lineas[max(0, i-3):i])
        ]

        for ctx in candidatos_contexto:
            if "sorteo pendiente" in ctx.lower():
                break
            num = buscar_numero_en_texto(ctx)
            if num and num in ANIMALITOS:
                resultados[hora] = {
                    "numero": num,
                    "animal": ANIMALITOS[num]
                }
                break

    return resultados

def obtener_lotto_activo():
    try:
        resp = requests.get(URL_LOTTO_ACTIVO, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        lineas = [re.sub(r"\s+", " ", l.strip()) for l in soup.get_text("\n").splitlines() if l.strip()]
        return extraer_sorteos_de_lineas(lineas)
    except Exception as e:
        print("Error consultando lottoactivo.com:", e)
        return {}

def obtener_la_granjita():
    try:
        resp = requests.get(URL_LA_GRANJITA, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        lineas = [re.sub(r"\s+", " ", l.strip()) for l in soup.get_text("\n").splitlines() if l.strip()]

        idx_inicio = next(
            (i for i, l in enumerate(lineas) if "resultados la granjita" in l.lower() or l.lower() == "hoy"),
            0
        )
        sub_lineas = lineas[idx_inicio:]
        idx_fin = next(
            (i for i, l in enumerate(sub_lineas) if "otros sorteos y resultados" in l.lower()),
            len(sub_lineas)
        )
        return extraer_sorteos_de_lineas(sub_lineas[:idx_fin])
    except Exception as e:
        print("Error consultando triples.bet:", e)
        return {}

def main():
    lotto_activo = obtener_lotto_activo()
    la_granjita = obtener_la_granjita()

    doc_ref = db.collection("resultados_diarios").document(fecha_hoy)
    payload = {"fecha": fecha_hoy}

    if lotto_activo:
        payload["lotto_activo"] = lotto_activo
    if la_granjita:
        payload["la_granjita"] = la_granjita

    doc_ref.set(payload, merge=True)
    print(f"Fecha: {fecha_hoy}")
    print("Lotto Activo:", lotto_activo)
    print("La Granjita:", la_granjita)

if __name__ == "__main__":
    main()
