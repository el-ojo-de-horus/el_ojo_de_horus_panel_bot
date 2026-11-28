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

# Tabla Técnica de Jale Profesional (corregida y normalizada; 35 = Jirafa)
TABLA_JALE = {
    "0":  {"jala": ["00", "33", "30"], "familia": "Trinidad del Agua"},
    "00": {"jala": ["0", "33", "29"],  "familia": "Los Gigantes del Agua"},
    "1":  {"jala": ["2", "26", "19"],  "familia": "Familia de Cuernos"},
    "2":  {"jala": ["1", "26", "5"],   "familia": "Ganadería y Fuerza"},
    "3":  {"jala": ["4", "36", "24"],  "familia": "Rastreros y Reptiles"},
    "4":  {"jala": ["3", "36", "1"],   "familia": "Suelo y Venenosos"},
    "5":  {"jala": ["10", "11", "13"], "familia": "Jerarquía de Felinos"},
    "6":  {"jala": ["35", "7", "33"],  "familia": "Humedales y Salto"},
    "7":  {"jala": ["9", "35", "25"],  "familia": "Aves y Colores"},
    "8":  {"jala": ["13", "32", "11"], "familia": "Roedores y Agilidad"},
    "9":  {"jala": ["7", "35", "28"],  "familia": "Las Rapaces"},
    "10": {"jala": ["5", "11", "20"],  "familia": "Felinos Salvajes"},
    "11": {"jala": ["5", "10", "27"],  "familia": "Felinos Domésticos"},
    "12": {"jala": ["18", "22", "23"], "familia": "Animales de Casco"},
    "13": {"jala": ["8", "32", "5"],   "familia": "Agilidad y Monte"},
    "14": {"jala": ["15", "17", "35"], "familia": "Aves de Tierra"},
    "15": {"jala": ["31", "34", "16"], "familia": "Astucia y Monte"},
    "16": {"jala": ["29", "15", "22"], "familia": "Pelaje y Fuerza"},
    "17": {"jala": ["14", "25", "35"], "familia": "Aves Grandes"},
    "18": {"jala": ["12", "22", "19"], "familia": "Animales de Carga"},
    "19": {"jala": ["1", "18", "34"],  "familia": "Animales de Pezuña"},
    "20": {"jala": ["26", "21", "00"], "familia": "Granja y Pesados"},
    "21": {"jala": ["25", "17", "7"],  "familia": "Aves de Corral"},
    "22": {"jala": ["18", "29", "12"], "familia": "Animales de Sabana"},
    "23": {"jala": ["12", "10", "22"], "familia": "Rayados y Casco"},
    "24": {"jala": ["36", "3", "4"],   "familia": "Reptiles de Sangre Fría"},
    "25": {"jala": ["21", "17", "14"], "familia": "Aves de Corral"},
    "26": {"jala": ["2", "20", "1"],   "familia": "Ganadería"},
    "27": {"jala": ["11", "15", "8"],  "familia": "Domésticos"},
    "28": {"jala": ["9", "35", "33"],  "familia": "Carroñeros y Aire"},
    "29": {"jala": ["16", "22", "00"], "familia": "Pesados y Sabana"},
    "30": {"jala": ["36", "0", "33"],  "familia": "Depredadores de Agua"},
    "31": {"jala": ["34", "15", "32"], "familia": "Animales de Cueva"},
    "32": {"jala": ["13", "31", "8"],  "familia": "Trepadores y Salto"},
    "33": {"jala": ["0", "00", "30"],  "familia": "El Cardumen"},
    "34": {"jala": ["31", "15", "1"],  "familia": "Monte y Salto"},
    "35": {"jala": ["7", "9", "14"],   "familia": "Aves en general"},
    "36": {"jala": ["30", "3", "24"],  "familia": "Rastreros Largos"},
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


def formatear_etiqueta_animal(clave: str, con_parentesis: bool = False) -> str:
    c = normalizar_clave_animal(clave)
    nombre = ANIMALITOS.get(c, "")
    etiqueta_num = "00" if c == "00" else c.zfill(2)
    if con_parentesis and nombre:
        return f"{nombre} ({etiqueta_num})"
    return f"{etiqueta_num} {nombre}".strip()


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


def jornada_esta_completa(data_hoy: dict) -> tuple[bool, dict]:
    """Verifica que lotto_activo y la_granjita tengan las 12 horas completas (08:00 AM - 07:00 PM)."""
    if not isinstance(data_hoy, dict) or not data_hoy:
        return False, {
            "lotto_activo": list(HORAS_ORDENADAS),
            "la_granjita": list(HORAS_ORDENADAS),
        }

    faltantes = {}
    completa = True

    for op in ("lotto_activo", "la_granjita"):
        bloque = data_hoy.get(op)
        ausentes = []
        for hora in HORAS_ORDENADAS:
            entry = bloque.get(hora) if isinstance(bloque, dict) else None
            num = (
                normalizar_clave_animal(entry.get("numero"))
                if isinstance(entry, dict) and entry.get("numero") is not None
                else ""
            )
            if not num or num not in ANIMALITOS:
                ausentes.append(hora)
        faltantes[op] = ausentes
        if ausentes:
            completa = False

    return completa, faltantes


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
        return [], [], [], Counter(), Counter(), Counter(), Counter(), None

    todos = []
    conteo_la = Counter()
    conteo_lg = Counter()
    primera_la = None

    for op in ("lotto_activo", "la_granjita"):
        bloque = data_hoy.get(op)
        if isinstance(bloque, dict):
            for hora in HORAS_ORDENADAS:
                entry = bloque.get(hora)
                if isinstance(entry, dict) and "numero" in entry:
                    clave = normalizar_clave_animal(entry["numero"])
                    if clave in ANIMALITOS:
                        todos.append(clave)
                        if op == "lotto_activo":
                            conteo_la[clave] += 1
                            if primera_la is None:
                                primera_la = clave
                        else:
                            conteo_lg[clave] += 1

    conteo_total = Counter(todos)
    conteo_term = Counter([int(n[-1]) for n in todos if n and n[-1].isdigit()])
    saturadas = [t for t, c in conteo_term.items() if c >= 4]

    jale_impulso = Counter()
    for clave in todos:
        info_jale = TABLA_JALE.get(clave)
        if info_jale:
            for idx_j, jalado in enumerate(info_jale["jala"]):
                clave_j = normalizar_clave_animal(jalado)
                if clave_j in ANIMALITOS:
                    jale_impulso[clave_j] += (3.0 - idx_j * 0.6)

    triangulaciones = []
    if "12" in todos and "18" in todos:
        triangulaciones.append("23")
    if "0" in todos and "33" in todos:
        triangulaciones.append("00")
    if "11" in todos and "27" in todos:
        triangulaciones.append("5")

    jales_ordenados = [c for c, _ in jale_impulso.most_common()]
    for cand_j in jales_ordenados[:3]:
        if cand_j not in triangulaciones:
            triangulaciones.append(cand_j)

    return (
        saturadas,
        triangulaciones,
        jales_ordenados,
        conteo_term,
        conteo_total,
        conteo_la,
        conteo_lg,
        primera_la,
    )


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


def calcular_top_5_probables(
    claves_fijos: set,
    vertice: int,
    bases: tuple,
    saturadas: list,
    triangulaciones: list,
    jales_ordenados: list,
    historico: Counter,
    conteo_term_hoy: Counter,
) -> list:
    """Selecciona los 5 animalitos con mayor probabilidad según convergencia de señales y Tabla de Jale."""
    terminales_opuestos = {(t + 5) % 10 for t in saturadas}
    if not terminales_opuestos:
        terminales_opuestos.add((vertice + 5) % 10)

    pesos_jale = {}
    for idx_j, clave_j in enumerate(jales_ordenados[:8]):
        pesos_jale[clave_j] = max(1.0, 3.2 - idx_j * 0.35)

    candidatos_puntuados = []

    for clave in ORDEN_CLAVES_ANIMALITOS:
        if clave in claves_fijos:
            continue

        term = int(clave[-1])
        puntaje = 0.0

        if term == vertice:
            puntaje += 3.5
        if term in bases:
            puntaje += 2.5
        if term in terminales_opuestos:
            puntaje += 2.0
        if clave in triangulaciones:
            puntaje += 3.5
        puntaje += pesos_jale.get(clave, 0.0)

        puntaje -= conteo_term_hoy.get(term, 0) * 0.45
        puntaje -= historico.get(clave, 0) * 0.6

        candidatos_puntuados.append((puntaje, clave))

    candidatos_puntuados.sort(
        key=lambda item: (-item[0], ORDEN_CLAVES_ANIMALITOS.index(item[1]))
    )

    top_5 = []
    for _, clave in candidatos_puntuados[:5]:
        top_5.append({
            "numero": clave,
            "animal": nombre_animal(clave),
            "etiqueta": formatear_etiqueta_animal(clave),
            "familia": TABLA_JALE.get(clave, {}).get("familia", ""),
        })

    return top_5


def construir_analisis_html(
    hoy: datetime.date,
    manana: datetime.date,
    conteo_term_hoy: Counter,
    conteo_total: Counter,
    conteo_la: Counter,
    conteo_lg: Counter,
    primera_la: str,
    fijos_formateados: dict,
    top_5_probables: list,
) -> tuple[str, str]:
    """Genera el título y el bloque HTML de análisis técnico que leerá y pintará index.html."""
    dia_base_minus = DIAS_ES[hoy.weekday()].lower()
    dia_proy_cap = DIAS_ES[manana.weekday()]
    titulo_html = f"<h2>📉 Análisis de Cinta y Detección de Bloqueos para el {dia_proy_cap}</h2>"

    if not conteo_total:
        html_completo = (
            f"{titulo_html}\n"
            f"  <p>Aún no hay sorteos registrados en la jornada del {dia_base_minus} para completar la lectura de cinta y detección de bloqueos para el {dia_proy_cap.lower()}.</p>"
        )
        return titulo_html, html_completo

    term_ordenados = [t for t, _ in conteo_term_hoy.most_common()]
    term_concentracion = term_ordenados[:4] if len(term_ordenados) >= 4 else term_ordenados
    if len(term_concentracion) > 1:
        txt_terminales = (
            ", ".join(str(t) for t in term_concentracion[:-1])
            + f" y {term_concentracion[-1]}"
        )
    elif term_concentracion:
        txt_terminales = str(term_concentracion[0])
    else:
        txt_terminales = "sin concentración destacada"

    eventos_pizarra = []
    if primera_la:
        eventos_pizarra.append(f"{formatear_etiqueta_animal(primera_la)} abriendo Lotto Activo")

    for clave, cant in conteo_total.most_common():
        if clave == primera_la:
            continue
        if conteo_la[clave] >= 1 and conteo_lg[clave] >= 1 and cant >= 2:
            etiqueta_tipo = "triple impacto entre ambas ruletas" if cant >= 3 else "repitiendo entre ambas pizarras"
            eventos_pizarra.append(f"{formatear_etiqueta_animal(clave)} ({etiqueta_tipo})")
        elif conteo_la[clave] >= 2:
            eventos_pizarra.append(f"{formatear_etiqueta_animal(clave)} marcando doble salida en Lotto Activo")
        elif conteo_lg[clave] >= 2:
            eventos_pizarra.append(f"{formatear_etiqueta_animal(clave)} marcando doble salida en La Granjita")
        elif cant >= 2:
            eventos_pizarra.append(f"{formatear_etiqueta_animal(clave)} repitiendo en la jornada")
        if len(eventos_pizarra) >= 5:
            break

    txt_eventos = ", ".join(eventos_pizarra) if eventos_pizarra else "sin repeticiones múltiples relevantes"

    fijo_ruptura = fijos_formate
