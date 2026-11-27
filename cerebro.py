import os
import json
import datetime
from collections import Counter
import firebase_admin
from firebase_admin import credentials, firestore

# ─── CONFIGURACIÓN FIREBASE ───
if not firebase_admin._apps:
    cred_env = os.environ.get("FIREBASE_CREDENTIALS") or os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if cred_env:
        cred = credentials.Certificate(json.loads(cred_env))
    elif os.path.exists("firebase-credentials.json"):
        cred = credentials.Certificate("firebase-credentials.json")
    else:
        raise RuntimeError("No se encontraron credenciales de Firebase.")
    firebase_admin.initialize_app(cred)

db = firestore.client()

VZLA_TZ = datetime.timezone(datetime.timedelta(hours=-4))
COLECCION_RESULTADOS = "resultados_diarios"
COLECCION_PROYECCIONES = "proyecciones"
CARPETA_IMG = "img"

HORAS_ORDENADAS = [
    "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM",
    "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM",
    "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"
]

DIAS_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo"
}

MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

# ─── TABLAS ───
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

TERMINALES = {
    0: ["0", "00", "10", "20", "30"],
    1: ["1", "11", "21", "31"],
    2: ["2", "12", "22", "32"],
    3: ["3", "13", "23", "33"],
    4: ["4", "14", "24", "34"],
    5: ["5", "15", "25", "35"],
    6: ["6", "16", "26", "36"],
    7: ["7", "17", "27"],
    8: ["8", "18", "28"],
    9: ["9", "19", "29"],
}

ORDEN_CLAVES_ANIMALITOS = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "0", "00"
]


def fecha_vzla() -> datetime.date:
    return datetime.datetime.now(VZLA_TZ).date()


def formatear_fecha_es(fecha: datetime.date) -> dict:
    dia_semana = DIAS_ES[fecha.weekday()]
    mes_nombre = MESES_ES[fecha.month]
    return {
        "dia_semana": dia_semana,
        "dia": fecha.day,
        "mes_numero": fecha.month,
        "mes_nombre": mes_nombre,
        "anio": fecha.year,
        "texto": f"{dia_semana}, {fecha.day:02d} de {mes_nombre} de {fecha.year}"
    }


def normalizar_clave_animal(num_raw) -> str:
    s = str(num_raw).strip()
    if s == "00":
        return "00"
    if s.isdigit():
        val = int(s)
        if 0 <= val <= 36:
            return str(val)
    return s


def nombre_animal(num_raw) -> str:
    clave = normalizar_clave_animal(num_raw)
    return ANIMALITOS.get(clave, "")


def buscar_imagen_animalito(num_raw, carpeta: str = CARPETA_IMG) -> str:
    """Busca un archivo de imagen en la carpeta img/ acorde al número del animalito."""
    clave = normalizar_clave_animal(num_raw)
    candidatos_base = [clave]
    if clave != "00" and clave.isdigit():
        candidatos_base.append(clave.zfill(2))

    extensiones = (".png", ".jpg", ".jpeg", ".webp", ".gif")

    if os.path.isdir(carpeta):
        archivos = sorted(os.listdir(carpeta))
        for base in candidatos_base:
            for ext in extensiones:
                candidato = f"{base}{ext}"
                if candidato in archivos:
                    return f"{carpeta}/{candidato}"

        for base in candidatos_base:
            for arch in archivos:
                bajo = arch.lower()
                if bajo.endswith(extensiones) and (
                    bajo.startswith(f"{base.lower()}_")
                    or bajo.startswith(f"{base.lower()}-")
                    or bajo.startswith(f"{base.lower()}.")
                ):
                    return f"{carpeta}/{arch}"

    pad = clave if clave == "00" else clave.zfill(2)
    return f"{carpeta}/{pad}.png"


def obtener_ultimo_cierre(data_hoy: dict) -> dict:
    """Obtiene el último animalito sorteado en el día (priorizando Lotto Activo y luego La Granjita)."""
    for op in ("lotto_activo", "la_granjita"):
        bloque = data_hoy.get(op)
        if isinstance(bloque, dict):
            for hora in reversed(HORAS_ORDENADAS):
                entry = bloque.get(hora)
                if isinstance(entry, dict) and entry.get("numero") is not None:
                    num = normalizar_clave_animal(entry["numero"])
                    animal = nombre_animal(num) or entry.get("animal", "")
                    return {
                        "fuente": op,
                        "hora": hora,
                        "numero": num,
                        "animal": animal,
                        "imagen": buscar_imagen_animalito(num),
                    }
    return {
        "fuente": "",
        "hora": "",
        "numero": "",
        "animal": "",
        "imagen": buscar_imagen_animalito("0"),
    }


def calcular_piramide(fecha: datetime.date):
    fila = [int(c) for c in fecha.strftime("%d%m%Y")]
    bases = (0, 0)
    while len(fila) > 1:
        fila = [(fila[i] + fila[i + 1]) % 10 for i in range(len(fila) - 1)]
        if len(fila) == 2:
            bases = (fila[0], fila[1])
    return fila[0], bases


def obtener_historico_reciente(fecha_base: datetime.date, dias: int = 7) -> Counter:
    apariciones = Counter()
    for i in range(1, dias + 1):
        fecha_str = (fecha_base - datetime.timedelta(days=i)).isoformat()
        doc = db.collection(COLECCION_RESULTADOS).document(fecha_str).get()
        if doc.exists:
            data = doc.to_dict() or {}
            for op in ("lotto_activo", "la_granjita"):
                if isinstance(data.get(op), dict):
                    for _, entry in data[op].items():
                        if isinstance(entry, dict) and "numero" in entry:
                            apariciones[normalizar_clave_animal(entry["numero"])] += 1
    return apariciones


def analizar_cinta_dia(data_hoy: dict):
    if not data_hoy:
        return [], []

    todos = []
    for op in ("lotto_activo", "la_granjita"):
        if isinstance(data_hoy.get(op), dict):
            for _, entry in data_hoy[op].items():
                if isinstance(entry, dict) and "numero" in entry:
                    todos.append(normalizar_clave_animal(entry["numero"]))

    conteo_term = Counter([int(n[-1]) for n in todos if n and n[-1].isdigit()])
    saturadas = [t for t, c in conteo_term.items() if c >= 4]

    triangulaciones = []
    if "12" in todos and "18" in todos:
        triangulaciones.append("23")
    if "0" in todos and "33" in todos:
        triangulaciones.append("00")
    if "11" in todos and "27" in todos:
        triangulaciones.append("5")

    return saturadas, triangulaciones


def seleccionar_clave_unica(candidatas, usados: set, respaldo_pool: list) -> str:
    """Devuelve la primera clave normalizada válida no repetida en `usados`."""
    for raw in candidatas:
        clave = normalizar_clave_animal(raw)
        if clave in ANIMALITOS and clave not in usados:
            usados.add(clave)
            return clave

    for raw in respaldo_pool:
        clave = normalizar_clave_animal(raw)
        if clave in ANIMALITOS and clave not in usados:
            usados.add(clave)
            return clave

    for clave in ORDEN_CLAVES_ANIMALITOS:
        if clave not in usados:
            usados.add(clave)
            return clave

    return normalizar_clave_animal(candidatas[0]) if candidatas else "0"


def generar_proyeccion():
    hoy = fecha_vzla()
    manana = hoy + datetime.timedelta(days=1)

    hoy_str = hoy.isoformat()
    manana_str = manana.isoformat()
    fecha_info = formatear_fecha_es(manana)

    doc_hoy = db.collection(COLECCION_RESULTADOS).document(hoy_str).get()
    data_hoy = doc_hoy.to_dict() if doc_hoy.exists else {}

    # Pirámide y proyección para MAÑANA a partir del cierre de HOY
    vertice, bases = calcular_piramide(manana)
    universo_term = list(set([vertice] + list(bases)))
    universo_nums = [n for t in universo_term for n in TERMINALES[t]]

    saturadas, triangulaciones = analizar_cinta_dia(data_hoy)
    historico = obtener_historico_reciente(hoy, dias=7)
    ultimo_cierre = obtener_ultimo_cierre(data_hoy)

    pool_respaldo = sorted(
        ORDEN_CLAVES_ANIMALITOS,
        key=lambda n: (historico.get(n, 0), ORDEN_CLAVES_ANIMALITOS.index(n))
    )
    usados = set()
    fijos_raw = {}

    # 1. Deuda histórica dentro del universo
    cand_deuda = sorted(universo_nums, key=lambda n: historico.get(n, 0))
    fijos_raw["Deuda_Historica"] = seleccionar_clave_unica(cand_deuda, usados, pool_respaldo)

    # 2. Vértice simetría
    cand_simetria = list(TERMINALES[vertice][1:]) + list(TERMINALES[vertice][:1])
    fijos_raw["Vertice_Simetria"] = seleccionar_clave_unica(cand_simetria, usados, pool_respaldo)

    # 3. Triangulación VIP
    if triangulaciones:
        cand_triangulacion = list(triangulaciones) + list(TERMINALES[bases[0]])
    else:
        cand_triangulacion = list(TERMINALES[bases[0]])
    fijos_raw["Triangulacion_VIP"] = seleccionar_clave_unica(cand_triangulacion, usados, pool_respaldo)

    # 4. Mecánica de ruptura
    if saturadas:
        t_sat = saturadas[0]
        t_op = (t_sat + 5) % 10
        cand_ruptura = list(TERMINALES[t_op][2:]) + list(TERMINALES[t_op][:2])
    else:
        t_op_v = (vertice + 5) % 10
        cand_ruptura = list(TERMINALES[t_op_v])
    fijos_raw["Mecanica_Ruptura"] = seleccionar_clave_unica(cand_ruptura, usados, pool_respaldo)

    # 5. Espejo acuático (siempre clave válida en ANIMALITOS y sin repetir)
    v_clave = normalizar_clave_animal(fijos_raw["Vertice_Simetria"])
    if v_clave in ("0", "10", "20", "30"):
        espejo_primario = "00" if v_clave != "00" else "0"
        cand_espejo = [espejo_primario, "0", "00"] + list(TERMINALES[0])
    else:
        term_v = int(v_clave[-1])
        cand_espejo = [str(term_v)] + list(TERMINALES[term_v])
    fijos_raw["Espejo_Acuario"] = seleccionar_clave_unica(cand_espejo, usados, pool_respaldo)

    fijos_formateados = {
        k: {
            "numero": normalizar_clave_animal(v),
            "animal": nombre_animal(v)
        }
        for k, v in fijos_raw.items()
    }

    resumen_5_fijos = [
        f"{item['numero'].zfill(2) if item['numero'] != '00' else '00'} {item['animal']}"
        for item in fijos_formateados.values()
    ]

    # Tripletas
    t1 = int(str(fijos_raw["Triangulacion_VIP"])[-1])
    t2 = int(str(fijos_raw["Mecanica_Ruptura"])[-1])
    t3 = int(str(fijos_raw["Vertice_Simetria"])[-1])
    tripletas = [TERMINALES[t1][:3], TERMINALES[t2][:3], TERMINALES[t3][:3]]

    proyeccion = {
        "fecha_base": hoy_str,
        "fecha_proyeccion": manana_str,
        "fecha_legible": fecha_info["texto"],
        "fecha_desglose": {
            "dia": fecha_info["dia"],
            "mes": fecha_info["mes_nombre"],
            "mes_numero": fecha_info["mes_numero"],
            "anio": fecha_info["anio"],
        },
        "piramide": {"vertice": vertice, "bases": list(bases)},
        "saturadas": saturadas,
        "ultimo_cierre": ultimo_cierre,
        "imagen_cierre": ultimo_cierre["imagen"],
        "fijos": fijos_formateados,
        "resumen_5_fijos": resumen_5_fijos,
        "tripletas": tripletas
    }

    db.collection(COLECCION_PROYECCIONES).document(manana_str).set(proyeccion, merge=True)
    print(f"✅ Cerebro ejecutado. Base {hoy_str} -> Proyección para {fecha_info['texto']} ({manana_str}).")
    print(f"🎯 Los 5 fijos: {' | '.join(resumen_5_fijos)}")
    print(f"🖼️ Último cierre: {ultimo_cierre['numero']} {ultimo_cierre['animal']} ({ultimo_cierre['hora']}) -> {ultimo_cierre['imagen']}")


if __name__ == "__main__":
    generar_proyeccion()
