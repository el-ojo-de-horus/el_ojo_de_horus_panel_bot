import os
import json
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

URL_RESULTADOS = "https://loteriadehoy.com/animalitos/resultados/"

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

RE_HORA = re.compile(r"\b(0?[89]:00\s*AM|1[01]:00\s*AM|12:00\s*PM|0?[1-7]:00\s*PM)\b", re.IGNORECASE)

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
    # Busca un número al inicio o seguido del nombre de un animalito
    for m in re.finditer(r"(?<!\d)(00|[0-3]?\d)(?!\d)", texto):
        num = normalizar_num(m.group(1))
        if num is not None and num in ANIMALITOS:
            # Evita capturar números de horas (ej: 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7) si van pegados a :00
            fin = m.end()
            if texto[fin:fin+3] == ":00":
                continue
            return num
    return None

def extraer_sorteos_seccion(lineas):
    resultados = {}
    for i, linea in enumerate(lineas):
        m_hora = RE_HORA.search(linea)
        if not m_hora:
            continue

        hora = normalizar_hora(m_hora.group(1))
        if hora not in HORAS_VALIDAS or hora in resultados:
            continue

        # Revisa primero la misma línea, luego líneas anteriores cercanas y posteriores cercanas
        candidatos_contexto = [
            linea,
            " ".join(lineas[max(0, i-2):i]),
            " ".join(lineas[i+1:min(len(lineas), i+3)])
        ]

        for ctx in candidatos_contexto:
            num = buscar_numero_en_texto(ctx)
            if num and num in ANIMALITOS:
                resultados[hora] = {
                    "numero": num,
                    "animal": ANIMALITOS[num]
                }
                break

    return resultados

def obtener_sorteos_loteria_de_hoy():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "es-VE,es;q=0.9,en;q=0.8"
    }
    resp = requests.get(URL_RESULTADOS, headers=headers, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    lineas = [re.sub(r"\s+", " ", line.strip()) for line in soup.get_text("\n").splitlines() if line.strip()]

    idx_la = next((i for i, l in enumerate(lineas) if l.lower() == "lotto activo"), -1)
    if idx_la == -1:
        idx_la = next((i for i, l in enumerate(lineas) if "lotto activo" in l.lower() and "2" not in l.lower() and "int" not in l.lower() and "rd" not in l.lower()), -1)

    lotto_activo = {}
    la_granjita = {}

    if idx_la != -1:
        bloque = lineas[idx_la:idx_la + 220]
        idx_lg = next((i for i, l in enumerate(bloque[1:], start=1) if "la granjita" in l.lower() and "millonaria" not in l.lower()), -1)

        if idx_lg != -1:
            lineas_la = bloque[:idx_lg]
            resto_lg = bloque[idx_lg:]
            idx_fin = next((i for i, l in enumerate(resto_lg[1:], start=1) if any(k in l.lower() for k in ["lotto activo 2", "guacharo activo", "monje millonario"])), len(resto_lg))
            lineas_lg = resto_lg[:idx_fin]

            lotto_activo = extraer_sorteos_seccion(lineas_la)
            la_granjita = extraer_sorteos_seccion(lineas_lg)

    return lotto_activo, la_granjita, len(lineas)

def main():
    lotto_activo, la_granjita, total_lineas = obtener_sorteos_loteria_de_hoy()

    doc_ref = db.collection("resultados_diarios").document(fecha_hoy)
    payload = {"fecha": fecha_hoy}

    if lotto_activo:
        payload["lotto_activo"] = lotto_activo
    if la_granjita:
        payload["la_granjita"] = la_granjita

    doc_ref.set(payload, merge=True)
    print(f"Líneas HTML: {total_lineas} | Fecha: {fecha_hoy}")
    print("Lotto Activo:", lotto_activo)
    print("La Granjita:", la_granjita)

if __name__ == "__main__":
    main()
