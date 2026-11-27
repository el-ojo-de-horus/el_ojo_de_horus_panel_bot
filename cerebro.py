<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>El Ojo de Horus - Panel de Proyecciones</title>
    <style>
        /* Estilos generales (Modo Oscuro) */
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #eab308; /* Dorado Horus */
            --danger: #ef4444;
            --success: #22c55e;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 { color: var(--accent); text-align: center; margin-bottom: 5px; }
        p.subtitle { color: var(--text-muted); text-align: center; margin-top: 0; margin-bottom: 30px; font-size: 0.9em; }
        
        /* Contenedor principal */
        .container { width: 100%; max-width: 600px; }

        /* Tarjeta de Análisis (Dato Caliente) */
        .analisis-card {
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1px solid var(--accent);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(234, 179, 8, 0.1);
        }
        .analisis-card h3 { margin-top: 0; color: var(--accent); font-size: 1.1em; }
        .analisis-card p { line-height: 1.5; font-size: 0.95em; color: #cbd5e1; margin-bottom: 0; }

        /* Lista de Pilares */
        .pilares-grid { display: flex; flex-direction: column; gap: 12px; margin-bottom: 30px; }
        .pilar-item {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid var(--accent);
            transition: transform 0.2s;
        }
        .pilar-item:hover { transform: translateX(5px); }
        .pilar-nombre { font-weight: 600; font-size: 0.9em; color: var(--text-muted); }
        .pilar-valor { font-size: 1.2em; font-weight: bold; color: var(--text-main); }

        /* Último sorteo */
        .ultimo-sorteo {
            background-color: #1e293b;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            margin-bottom: 30px;
            border: 1px dashed #475569;
        }
        .ultimo-sorteo span { color: var(--accent); font-weight: bold; }

        /* Botón Telegram */
        .btn-telegram {
            display: block;
            width: 100%;
            padding: 15px;
            background-color: #229ED9;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 1.1em;
            box-sizing: border-box;
            transition: background-color 0.3s;
        }
        .btn-telegram:hover { background-color: #1a7fb3; }

        /* Loader */
        .sincronizando { color: var(--text-muted); font-style: italic; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    </style>
</head>
<body>

    <div class="container">
        <h1>👁️ El Ojo de Horus</h1>
        <p class="subtitle">Panel de Proyecciones Estadísticas - Lotto Activo y La Granjita</p>

        <!-- Análisis de Cinta -->
        <div class="analisis-card">
            <h3>🔥 Dato Caliente de la Hora</h3>
            <p id="datoCaliente" class="sincronizando">Sincronizando con el Cerebro...</p>
        </div>

        <!-- Los 5 Pilares del Cerebro -->
        <h3 style="color: #cbd5e1; border-bottom: 1px solid #334155; padding-bottom: 10px;">Los 5 Fijos de Hoy</h3>
        <div class="pilares-grid">
            <div class="pilar-item">
                <span class="pilar-nombre">Pilar Deuda Histórica</span>
                <span class="pilar-valor" id="pilar-deuda">...</span>
            </div>
            <div class="pilar-item">
                <span class="pilar-nombre">Pilar Vértice / Simetría</span>
                <span class="pilar-valor" id="pilar-simetria">...</span>
            </div>
            <div class="pilar-item">
                <span class="pilar-nombre">Triangulación VIP</span>
                <span class="pilar-valor" id="pilar-triangulacion">...</span>
            </div>
            <div class="pilar-item">
                <span class="pilar-nombre">Mecánica de Ruptura</span>
                <span class="pilar-valor" id="pilar-ruptura">...</span>
            </div>
            <div class="pilar-item">
                <span class="pilar-nombre">Espejo y Simetría</span>
                <span class="pilar-valor" id="pilar-espejo">...</span>
            </div>
        </div>

        <!-- Último Sorteo en Vivo -->
        <div class="ultimo-sorteo">
            <span style="font-size: 0.8em; display: block; margin-bottom: 5px;">ÚLTIMO SORTEO REGISTRADO</span>
            <div id="cierre" class="sincronizando">Esperando resultados...</div>
        </div>

        <!-- Botón VIP -->
        <a href="https://t.me/TU_BOT_AQUI" target="_blank" class="btn-telegram">
            Ir al Bot en Telegram (Comunidad V.I.P.)
        </a>
    </div>

    <!-- SCRIPTS DE FIREBASE -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
        import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

        const firebaseConfig = { projectId: "el-ojo-de-horus-bot" };
        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);

        // Diccionario para mostrar el nombre del animalito
        const ANIMALITOS = {
            "0": "Delfín", "00": "Ballena", "1": "Carnero", "2": "Toro", "3": "Ciempiés",
            "4": "Alacrán", "5": "León", "6": "Rana", "7": "Perico", "8": "Ratón",
            "9": "Águila", "10": "Tigre", "11": "Gato", "12": "Caballo", "13": "Mono",
            "14": "Paloma", "15": "Zorro", "16": "Oso", "17": "Pavo", "18": "Burro",
            "19": "Chivo", "20": "Cochino", "21": "Gallo", "22": "Camello", "23": "Cebra",
            "24": "Iguana", "25": "Gallina", "26": "Vaca", "27": "Perro", "28": "Zamuro",
            "29": "Elefante", "30": "Caimán", "31": "Lapa", "32": "Ardilla", "33": "Pescado",
            "34": "Venado", "35": "Jirafa", "36": "Culebra"
        };

        function etiquetaNum(num) {
            const n = String(num ?? "").trim();
            return `${n.padStart(2, "0")} - ${ANIMALITOS[n] || "Desconocido"}`;
        }

        // Obtener fecha actual de Venezuela (UTC-4)
        const ahora = new Date();
        const vzla = new Date(ahora.getTime() - 4 * 60 * 60 * 1000);
        const fechaHoy = vzla.toISOString().slice(0, 10);

        // ─────────────────────────────────────────────────────────────
        // 1. ESCUCHAR AL CEREBRO (Proyecciones calculadas a las 8 PM ayer)
        // ─────────────────────────────────────────────────────────────
        onSnapshot(doc(db, "proyecciones", fechaHoy), (docSnap) => {
            if (!docSnap.exists()) {
                document.getElementById("datoCaliente").innerText = "El Cerebro aún no ha generado las proyecciones para hoy. Vuelve a las 8:30 PM.";
                document.getElementById("datoCaliente").classList.add("sincronizando");
                return;
            }

            const brain = docSnap.data();
            const fijos = brain.fijos;

            // Inyectar los 5 Fijos en la interfaz
            document.getElementById("pilar-deuda").innerText = etiquetaNum(fijos.Deuda_Historica.numero);
            document.getElementById("pilar-simetria").innerText = etiquetaNum(fijos.Vertice_Simetria.numero);
            document.getElementById("pilar-triangulacion").innerText = etiquetaNum(fijos.Triangulacion_VIP.numero);
            document.getElementById("pilar-ruptura").innerText = etiquetaNum(fijos.Mecanica_Ruptura.numero);
            document.getElementById("pilar-espejo").innerText = etiquetaNum(fijos.Espejo_Acuario.numero);

            // Escribir el Dato Caliente
            const elDatoCaliente = document.getElementById("datoCaliente");
            const saturadas = brain.saturadas.length > 0 ? brain.saturadas.join(", ") : "ninguna";
            elDatoCaliente.classList.remove("sincronizando");
            elDatoCaliente.innerHTML = `🧠 <b>Análisis de Cinta:</b> Ayer se saturaron las terminales <b>${saturadas}</b>. 
                                        La pirámide de hoy marca Vértice <b>${brain.piramide.vertice}</b> y Bases <b>${brain.piramide.bases.join(" y ")}</b>. 
                                        Las jugadas de Ruptura y las Tripletas están activas.`;
        });

        // ─────────────────────────────────────────────────────────────
        // 2. ESCUCHAR RESULTADOS EN VIVO (Último sorteo del día)
        // ─────────────────────────────────────────────────────────────
        onSnapshot(doc(db, "resultados", fechaHoy), (docSnap) => {
            if (!docSnap.exists()) return;
            const data = docSnap.data();
            
            const horas = ["07:00 PM","06:00 PM","05:00 PM","04:00 PM","03:00 PM","02:00 PM","01:00 PM","12:00 PM","11:00 AM","10:00 AM","09:00 AM","08:00 AM"];
            let encontrado = false;

            for (let h of horas) {
                if (data.lotto_activo?.[h]?.numero) {
                    document.getElementById("cierre").classList.remove("sincronizando");
                    document.getElementById("cierre").innerHTML = `<span>${h} (Lotto Activo)</span>: ${etiquetaNum(data.lotto_activo[h].numero)}`;
                    encontrado = true;
                    break;
                }
                if (data.la_granjita?.[h]?.numero) {
                    document.getElementById("cierre").classList.remove("sincronizando");
                    document.getElementById("cierre").innerHTML = `<span>${h} (La Granjita)</span>: ${etiquetaNum(data.la_granjita[h].numero)}`;
                    encontrado = true;
                    break;
                }
            }
            if (!encontrado) {
                document.getElementById("cierre").innerText = "Esperando el primer sorteo del día...";
            }
        });
    </script>
</body>
</html>
