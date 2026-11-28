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

    fijo_ruptura = fijos_formateados.get("Mecanica_Ruptura", {})
    fijo_triang = fijos_formateados.get("Triangulacion_VIP", {})
    fijo_simetria = fijos_formateados.get("Vertice_Simetria", {})
    fijo_deuda = fijos_formateados.get("Deuda_Historica", {})
    fijo_espejo = fijos_formateados.get("Espejo_Acuario", {})

    impulso_a = formatear_etiqueta_animal(fijo_simetria.get("numero", "10"), con_parentesis=True)
    impulso_b = formatear_etiqueta_animal(fijo_ruptura.get("numero", "30"), con_parentesis=True)
    refuerzo_c = formatear_etiqueta_animal(fijo_triang.get("numero", "13"), con_parentesis=True)
    proy_d = formatear_etiqueta_animal(fijo_espejo.get("numero", "00"), con_parentesis=True)
    proy_e = formatear_etiqueta_animal(fijo_deuda.get("numero", "0"), con_parentesis=True)

    destacado_1 = formatear_etiqueta_animal(top_5_probables[0]["numero"], con_parentesis=True) if len(top_5_probables) > 0 else refuerzo_c
    destacado_2 = formatear_etiqueta_animal(top_5_probables[1]["numero"], con_parentesis=True) if len(top_5_probables) > 1 else impulso_b

    top_destacado = conteo_total.most_common(2)
    ref_1 = formatear_etiqueta_animal(top_destacado[0][0], con_parentesis=True) if len(top_destacado) > 0 else "Perro (27)"
    ref_2 = formatear_etiqueta_animal(top_destacado[1][0], con_parentesis=True) if len(top_destacado) > 1 else "Alacrán (04)"

    p1 = (
        f"<p>En la lectura de cinta del {dia_base_minus} detectamos una fuerte concentración en la "
        f"<strong>Terminal {txt_terminales}</strong> ({txt_eventos}). Aplicando la "
        f"<strong>Mecánica de Ruptura</strong> y la <strong>Tabla de Jale</strong>, el algoritmo libera presión "
        f"impulsando la tracción hacia el <strong>{impulso_a}</strong> y el <strong>{impulso_b}</strong>, "
        f"reforzando la continuidad del <strong>{refuerzo_c}</strong> y la proyección de la "
        f"<strong>{proy_d}</strong> y el <strong>{proy_e}</strong>.</p>"
    )

    p2 = (
        f"<p>Asimismo, la contundencia del {ref_1} y la repetición del {ref_2} en la jornada del {dia_base_minus} "
        f"posicionan al <strong>{destacado_1}</strong> y al <strong>{destacado_2}</strong> al frente de la matriz de datos "
        f"para la jornada de este {dia_proy_cap.lower()}.</p>"
    )

    html_completo = f"{titulo_html}\n  {p1}\n  {p2}"
    return titulo_html, html_completo


def construir_dato_auditor_html(
    manana: datetime.date,
    conteo_total: Counter,
    conteo_la: Counter,
    fijos_formateados: dict,
    top_5_probables: list,
) -> tuple[str, str]:
    """Genera el texto plano y el bloque HTML del Dato Caliente de la Hora para index.html."""
    dia_proy_minus = DIAS_ES[manana.weekday()].lower()

    rep_la = [c for c, cant in conteo_la.most_common() if cant >= 2]
    rep_total = [c for c, cant in conteo_total.most_common() if cant >= 2]

    clave_la = rep_la[0] if rep_la else (conteo_la.most_common(1)[0][0] if conteo_la else "27")
    clave_cinta = next((c for c in rep_total if c != clave_la), rep_total[0] if rep_total else "4")

    etq_la_mayus = formatear_etiqueta_animal(clave_la).upper()
    etq_cinta_mayus = formatear_etiqueta_animal(clave_cinta).upper()

    fijo_ruptura = fijos_formateados.get("Mecanica_Ruptura", {})
    fijo_triang = fijos_formateados.get("Triangulacion_VIP", {})

    clave_descarga = top_5_probables[1]["numero"] if len(top_5_probables) > 1 else fijo_ruptura.get("numero", "30")
    clave_cruce = top_5_probables[0]["numero"] if len(top_5_probables) > 0 else fijo_triang.get("numero", "13")

    etq_descarga_mayus = formatear_etiqueta_animal(clave_descarga).upper()
    etq_cruce_mayus = formatear_etiqueta_animal(clave_cruce).upper()

    texto_plano = (
        f"¡Mucho ojo aquí, jugador! Cuando el {etq_la_mayus} te repite en Lotto Activo y el "
        f"{etq_cinta_mayus} te satura la cinta entre ambas pizarras, la matriz de datos aprieta la lectura "
        f"y deja marcadas las líneas de arrastre. Para destrabar la lectura este {dia_proy_minus} desde temprano, "
        f"el algoritmo siempre busca la rápida descarga del {etq_descarga_mayus} o el cruce directo del "
        f"{etq_cruce_mayus}. ¡Muy atento desde el primer sorteo de las 08:00 AM !"
    )

    html_dato = (
        f'<div class="dato-curioso">\n'
        f'    💡 <strong><em>El Dato Caliente de la Hora:</em></strong><br />\n'
        f'    <em>{texto_plano}</em>\n'
        f'  </div>'
    )

    return texto_plano, html_dato


def construir_pronostico_html(
    manana: datetime.date,
    fijos_formateados: dict,
    imagen_cierre: str,
) -> tuple[str, str]:
    """Genera el título y el bloque HTML de Los 5 Fijos para que index.html solo lo pinte."""
    dia_proy_cap = DIAS_ES[manana.weekday()]
    mes_proy_cap = MESES_ES[manana.month].capitalize()
    titulo_texto = f"📊 Los 5 Fijos del {dia_proy_cap} {manana.day:02d} de {mes_proy_cap}"

    def item_fijo(clave_fijo: str, etiqueta_pilar: str, clase_color: str) -> str:
        datos = fijos_formateados.get(clave_fijo, {})
        num = normalizar_clave_animal(datos.get("numero", ""))
        animal = datos.get("animal") or nombre_animal(num)
        etiqueta_animal = "--"
        if num and animal:
            etiqueta_animal = f"{'00' if num == '00' else num.zfill(2)} {animal}"
        elif num:
            etiqueta_animal = formatear_etiqueta_animal(num)
        return (
            f'  <div class="proyeccion-item">\n'
            f'    <span class="tipo">{etiqueta_pilar}</span>\n'
            f'    <span class="animalito {clase_color}">{etiqueta_animal}</span>\n'
            f'  </div>'
        )

    img_src = imagen_cierre or "img/logo.jpg"

    html_pronostico = (
        f'<div class="proyeccion-header">\n'
        f'  <div><img id="imgPortadaCierre" alt="Imagen de cierre" src="{img_src}" onerror="this.onerror=null;this.src=\'img/logo.jpg\';" /></div>\n'
        f'  <br />{titulo_texto}\n'
        f'</div>\n'
        f'{item_fijo("Deuda_Historica", "Pilar Deuda Histórica:", "c1")}\n'
        f'{item_fijo("Vertice_Simetria", "Pilar Vértice Simetría:", "c2")}\n'
        f'{item_fijo("Triangulacion_VIP", "Triangulación VIP:", "c3")}\n'
        f'{item_fijo("Mecanica_Ruptura", "Mecánica de Ruptura:", "c4")}\n'
        f'{item_fijo("Espejo_Acuario", "Espejo Acuático:", "c5")}'
    )

    return titulo_texto, html_pronostico


def generar_proyeccion():
    hoy = fecha_vzla()
    manana = hoy + datetime.timedelta(days=1)

    hoy_str = hoy.isoformat()
    manana_str = manana.isoformat()
    fecha_info = formatear_fecha_es(manana)

    doc_hoy = db.collection(COLECCION_RESULTADOS).document(hoy_str).get()
    data_hoy = doc_hoy.to_dict() if doc_hoy.exists else {}

    completa, faltantes = jornada_esta_completa(data_hoy)
    if not completa:
        print(f"⏳ Jornada {hoy_str} aún incompleta. No se genera proyección todavía.")
        for op, horas_f in faltantes.items():
            if horas_f:
                print(f"   - {op}: faltan {', '.join(horas_f)}")
        return

    vertice, bases = calcular_piramide(manana)
    universo_term = list(set([vertice] + list(bases)))
    universo_nums = [n for t in universo_term for n in TERMINALES[t]]

    (
        saturadas,
        triangulaciones,
        jales_ordenados,
        conteo_term_hoy,
        conteo_total,
        conteo_la,
        conteo_lg,
        primera_la,
    ) = analizar_cinta_dia(data_hoy)

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

    # 5. Espejo acuático
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
        formatear_etiqueta_animal(item["numero"])
        for item in fijos_formateados.values()
    ]

    top_5_probables = calcular_top_5_probables(
        claves_fijos=set(fijos_raw.values()),
        vertice=vertice,
        bases=bases,
        saturadas=saturadas,
        triangulaciones=triangulaciones,
        jales_ordenados=jales_ordenados,
        historico=historico,
        conteo_term_hoy=conteo_term_hoy,
    )
    resumen_top_5_probables = [item["etiqueta"] for item in top_5_probables]

    pronostico_titulo, pronostico_html = construir_pronostico_html(
        manana=manana,
        fijos_formateados=fijos_formateados,
        imagen_cierre=ultimo_cierre["imagen"],
    )

    analisis_tecnico_titulo, analisis_tecnico_html = construir_analisis_html(
        hoy=hoy,
        manana=manana,
        conteo_term_hoy=conteo_term_hoy,
        conteo_total=conteo_total,
        conteo_la=conteo_la,
        conteo_lg=conteo_lg,
        primera_la=primera_la,
        fijos_formateados=fijos_formateados,
        top_5_probables=top_5_probables,
    )

    dato_auditor, dato_auditor_html = construir_dato_auditor_html(
        manana=manana,
        conteo_total=conteo_total,
        conteo_la=conteo_la,
        fijos_formateados=fijos_formateados,
        top_5_probables=top_5_probables,
    )

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
        "jales_activados": [formatear_etiqueta_animal(c) for c in jales_ordenados[:6]],
        "ultimo_cierre": ultimo_cierre,
        "imagen_cierre": ultimo_cierre["imagen"],
        "fijos": fijos_formateados,
        "resumen_5_fijos": resumen_5_fijos,
        "top_5_probables": top_5_probables,
        "resumen_top_5_probables": resumen_top_5_probables,
        "pronostico_titulo": pronostico_titulo,
        "pronostico_html": pronostico_html,
        "analisis_tecnico_titulo": analisis_tecnico_titulo,
        "analisis_tecnico_html": analisis_tecnico_html,
        "dato_auditor": dato_auditor,
        "dato_auditor_html": dato_auditor_html,
    }

    proyeccion["tripletas"] = firestore.DELETE_FIELD

    db.collection(COLECCION_PROYECCIONES).document(manana_str).set(proyeccion, merge=True)
    print(f"✅ Cerebro ejecutado. Base {hoy_str} -> Proyección para {fecha_info['texto']} ({manana_str}).")
    print(f"🎯 Los 5 fijos: {' | '.join(resumen_5_fijos)}")
    print(f"🔥 Top 5 mayor probabilidad: {' | '.join(resumen_top_5_probables)}")
    print(f"🖼️ Último cierre: {ultimo_cierre['numero']} {ultimo_cierre['animal']} ({ultimo_cierre['hora']}) -> {ultimo_cierre['imagen']}")


if __name__ == "__main__":
    generar_proyeccion()
