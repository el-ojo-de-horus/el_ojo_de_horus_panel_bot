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

def extraer_bloque_ruleta(texto_bloque):
    resultados = {}
    patron = re.compile(
        r"\b(00|[0-3]?\d)\b\s+[A-Za-zÁÉÍÓÚÑáéíóúñ]+\s+(0?[89]:00\s*AM|1[01]:00\s*AM|12:00\s*PM|0?[1-7]:00\s*PM)",
        re.IGNORECASE
    )
    for match in patron.finditer(texto_bloque):
        num = normalizar_num(match.group(1))
        hora = normalizar_hora(match.group(2))
        if num in ANIMALITOS and hora in HORAS_VALIDAS and hora not in resultados:
            resultados[hora] = {
                "numero": num,
                "animal": ANIMALITOS[num]
            }
    return resultados

def obtener_sorteos_loteria_de_hoy():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    resp = requests.get(URL_RESULTADOS, headers=headers, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    lineas = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]
    texto_plano = "\n".join(lineas)

    lotto_activo = {}
    la_granjita = {}

    idx_la = texto_plano.find("Lotto Activo")
    if idx_la != -1:
        fragmento_la = texto_plano[idx_la:idx_la + 4500]
        partes_lg = fragmento_la.split("La Granjita", 1)
        lotto_activo = extraer_bloque_ruleta(partes_lg[0])
        if len(partes_lg) > 1:
            sub_lg = partes_lg[1].split("Lotto Activo 2", 1)[0]
            la_granjita = extraer_bloque_ruleta(sub_lg)

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
    print(f"Fecha {fecha_hoy} sincronizada -> Lotto Activo: {len(lotto_activo)} horas | La Granjita: {len(la_granjita)} horas")

if __name__ == "__main__":
    main()
