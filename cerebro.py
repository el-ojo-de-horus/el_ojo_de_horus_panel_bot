import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from collections import Counter

# ─── CONFIGURACIÓN FIREBASE ───
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ─── TABLAS ───
ANIMALITOS = {
    "0":"Delfín","00":"Ballena","1":"Carnero","2":"Toro","3":"Ciempiés","4":"Alacrán","5":"León","6":"Rana","7":"Perico","8":"Ratón","9":"Águila","10":"Tigre","11":"Gato","12":"Caballo","13":"Mono","14":"Paloma","15":"Zorro","16":"Oso","17":"Pavo","18":"Burro","19":"Chivo","20":"Cochino","21":"Gallo","22":"Camello","23":"Cebra","24":"Iguana","25":"Gallina","26":"Vaca","27":"Perro","28":"Zamuro","29":"Elefante","30":"Caimán","31":"Lapa","32":"Ardilla","33":"Pescado","34":"Venado","35":"Jirafa","36":"Culebra"
}
TERMINALES = {
    0: ["0", "00", "10", "20", "30"], 1: ["1", "11", "21", "31"], 2: ["2", "12", "22", "32"],
    3: ["3", "13", "23", "33"], 4: ["4", "14", "24", "34"], 5: ["5", "15", "25", "35"],
    6: ["6", "16", "26", "36"], 7: ["7", "17", "27"], 8: ["8", "18", "28"], 9: ["9", "19", "29"],
}

def calcular_piramide(fecha):
    fila = [int(c) for c in fecha.strftime("%d%m%Y")]
    while len(fila) > 1:
        fila = [(fila[i] + fila[i+1]) % 10 for i in range(len(fila) - 1)]
        if len(fila) == 2: bases = tuple(fila)
    return fila[0], bases

def obtener_historico_reciente(dias=7):
    """Lee los últimos N días para calcular la deuda real."""
    hoy = datetime.date.today()
    apariciones = Counter()
    for i in range(1, dias + 1):
        fecha_str = (hoy - datetime.timedelta(days=i)).isoformat()
        doc = db.collection('resultados').document(fecha_str).get()
        if doc.exists:
            data = doc.to_dict()
            for op in ['lotto_activo', 'la_granjita']:
                if op in data:
                    for hora, entry in data[op].items():
                        if 'numero' in entry:
                            apariciones[str(entry['numero'])] += 1
    return apariciones

def analizar_cinta_hoy():
    """Analiza los resultados de HOY para la ruptura de MAÑANA."""
    hoy = datetime.date.today().isoformat()
    doc = db.collection('resultados').document(hoy).get()
    if not doc.exists: return [], []
    
    data = doc.to_dict()
    todos = []
    for op in ['lotto_activo', 'la_granjita']:
        if op in data:
            for h, entry in data[op].items():
                if 'numero' in entry: todos.append(str(entry['numero']))
    
    conteo_term = Counter([int(n[-1]) for n in todos])
    saturadas = [t for t, c in conteo_term.items() if c >= 4]
    
    triangulaciones = []
    if "12" in todos and "18" in todos: triangulaciones.append("23")
    if "0" in todos and "33" in todos: triangulaciones.append("00")
    if "11" in todos and "27" in todos: triangulaciones.append("05")
    
    return saturadas, triangulaciones

def generar_proyeccion():
    hoy = datetime.date.today()
    manana = hoy + datetime.timedelta(days=1)
    
    # 1. Datos Base
    vertice, bases = calcular_piramide(manana)
    universo_term = list(set([vertice] + list(bases)))
    universo_nums = [n for t in universo_term for n in TERMINALES[t]]
    
    saturadas, triangulaciones = analizar_cinta_hoy()
    historico = obtener_historico_reciente()

    fijos = {}

    # PILAR 1: DEUDA HISTÓRICA (El que menos ha salido en 7 días DENTRO del universo)
    cand_deuda = sorted(universo_nums, key=lambda n: historico.get(n, 0))
    fijos["Deuda_Historica"] = cand_deuda[0]

    # PILAR 2: VÉRTICE (Un número de la terminal del vértice)
    fijos["Vertice_Simetria"] = TERMINALES[vertice][1] # Tomamos el segundo de la familia para variar

    # PILAR 3: TRIANGULACIÓN VIP
    if triangulaciones:
        fijos["Triangulacion_VIP"] = triangulaciones[0]
    else:
        fijos["Triangulacion_VIP"] = TERMINALES[bases[0]][0]

    # PILAR 4: RUPTURA (Opuesto de la terminal más saturada)
    if saturadas:
        t_sat = saturadas[0]
        t_op = (t_sat + 5) % 10
        fijos["Mecanica_Ruptura"] = TERMINALES[t_op][2] # Tercero de la familia
    else:
        fijos["Mecanica_Ruptura"] = TERMINALES[(vertice + 5) % 10][0]

    # PILAR 5: ESPEJO ACUÁTICO
    v_str = str(fijos["Vertice_Simetria"])
    fijos["Espejo_Acuario"] = "00" if v_str in ["0", "10", "20"] else f"0{v_str[-1]}"

    # TRIPLETAS (Agrupando familias de los 3 fijos principales)
    t1 = int(fijos["Triangulacion_VIP"][-1])
    t2 = int(fijos["Mecanica_Ruptura"][-1])
    t3 = int(fijos["Vertice_Simetria"][-1])
    tripletas = [TERMINALES[t1][:3], TERMINALES[t2][:3], TERMINALES[t3][:3]]

    proyeccion = {
        "fecha_proyeccion": manana.isoformat(),
        "piramide": {"vertice": vertice, "bases": list(bases)},
        "saturadas": saturadas,
        "fijos": {k: {"numero": v, "animal": ANIMALITOS.get(v, "")} for k, v in fijos.items()},
        "tripletas": tripletas
    }
    
    db.collection('proyecciones').document(manana.isoformat()).set(proyeccion)
    print(f"✅ Cerebro ejecutado. Proyección para {manana.isoformat()} guardada.")

if __name__ == "__main__":
    generar_proyeccion()
