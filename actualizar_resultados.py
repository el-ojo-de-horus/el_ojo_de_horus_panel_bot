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

HORAS_VALIDAS = {
    "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM",
    "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM",
    "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"
}

RE_HORA = re.compile(r"^(0?[89]:00\s*AM|1[01]:00\s*AM|12:00\s*PM|0?[1-7]:00\s*PM)$", re.IGNORECASE)
RE_NUM_ANIMAL = re.compile(r"^(00|[0-3]?\d)\b(?:\s+([A-Za-zÁÉÍÓÚÑáéíóúñ]+))?")

def normalizar_num(n):
    n = n.strip()
    if n == "00":
        return "00"
    if n.isdigit():
        return str(int(n))
    return n

def normalizar_hora(h):
    h = re.sub(r"\s+", " ", h.strip().upper())
    if re.match(r"^[89]:00\s*AM$", h):
        h = "0" + h
    return h

def parsear_lineas_ruleta(lineas):
    resultados = {}
    pendiente_animal = None

    for line in lineas:
        # Si la línea es un número con animalito (ej: "12 Caballo" o "4 Alacran")
        m_animal = RE_NUM_ANIMAL.match(line)
        if m_animal:
            num = normalizar_num(m_animal.group(1))
            if num in ANIMALITOS:
                pendiente_animal = num
                continue

        # Si la línea es una hora (ej: "08:00 AM")
        m_hora = RE_HORA.match(line)
        if m_hora and pendiente_animal is not None:
            hora = normalizar_hora(m_hora.group(1))
            if hora in HORAS_VALIDAS and hora not in resultados:
                resultados[hora] = {
                    "numero": pendiente_animal,
                    "animal": ANIMALITOS[pendiente_animal]
                }
            pendiente_animal = None

    return resultados

def obtener_sorteos_loteria_de_hoy():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    resp = requests.get(URL_RESULTADOS, headers=headers, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    lineas = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]

    lotto_activo = {}
    la_granjita = {}

    try:
        idx_la = lineas.index("Lotto Activo")
    except ValueError:
        idx_la = next((i for i, l in enumerate(lineas) if l == "Lotto Activo"), -1)

    if idx_la != -1:
        sub_lineas = lineas[idx_la:idx_la + 180]
        try:
            idx_lg_rel = sub_lineas.index("La Granjita")
        except ValueError:
            idx_lg_rel = next((i for i, l in enumerate(sub_lineas) if l == "La Granjita"), -1)

        if idx_lg_rel != -1:
            lineas_la = sub_lineas[:idx_lg_rel]
            resto = sub_lineas[idx_lg_rel + 1:]
            idx_fin_lg = next((i for i, l in enumerate(resto) if "Lotto Activo 2" in l or "Guacharo Activo" in l), len(resto))
            lineas_lg = resto[:idx_fin_lg]

            lotto_activo = parsear_lineas_ruleta(lineas_la)
            la_granjita = parsear_lineas_ruleta(lineas_lg)

    return lotto_activo, la_granjita

def main():
    lotto_activo, la_granjita = obtener_sorteos_loteria_de_hoy()

    doc_ref = db.collection("resultados_diarios").document(fecha_hoy)
    payload = {"fecha": fecha_hoy}

    if lotto_activo:
        payload["lotto_activo"] = lotto_activo
    if la_granjita:
        payload["la_granjita"] = la_granjita

    doc_ref.set(payload, merge=True)
    print(f"Fecha {fecha_hoy} sincronizada -> Lotto Activo: {lotto_activo} | La Granjita: {la_granjita}")

if __name__ == "__main__":
    main()
