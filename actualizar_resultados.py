<script type="module">
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
  import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

  const app = initializeApp({ projectId: "el-ojo-de-horus-bot" });
  const db = getFirestore(app);

  const ANIMALITOS = { "0": "Delfín", "00": "Ballena", "1": "Carnero", "2": "Toro", "3": "Ciempiés", "4": "Alacrán", "5": "León", "6": "Rana", "7": "Perico", "8": "Ratón", "9": "Águila", "10": "Tigre", "11": "Gato", "12": "Caballo", "13": "Mono", "14": "Paloma", "15": "Zorro", "16": "Oso", "17": "Pavo", "18": "Burro", "19": "Chivo", "20": "Cochino", "21": "Gallo", "22": "Camello", "23": "Cebra", "24": "Iguana", "25": "Gallina", "26": "Vaca", "27": "Perro", "28": "Zamuro", "29": "Elefante", "30": "Caimán", "31": "Lapa", "32": "Ardilla", "33": "Pescado", "34": "Venado", "35": "Jirafa", "36": "Culebra" };

  function etiquetaNum(num) {
    const n = String(num ?? "").trim();
    return `${n.padStart(2, "0")} ${ANIMALITOS[n] || ""}`;
  }

  const fechaHoy = new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString().slice(0, 10);

  // 1. ESCUCHAR PROYECCIONES (EL CEREBRO)
  onSnapshot(doc(db, "proyecciones", fechaHoy), (docSnap) => {
    if (!docSnap.exists()) return;
    const brain = docSnap.data();
    
    // Inyectar Fijos (Asegúrate de que estos IDs existan en tu HTML)
    if(document.getElementById("pilar-deuda")) document.getElementById("pilar-deuda").innerText = etiquetaNum(brain.fijos.Deuda_Historica.numero);
    if(document.getElementById("pilar-simetria")) document.getElementById("pilar-simetria").innerText = etiquetaNum(brain.fijos.Vertice_Simetria.numero);
    if(document.getElementById("pilar-triangulacion")) document.getElementById("pilar-triangulacion").innerText = etiquetaNum(brain.fijos.Triangulacion_VIP.numero);
    if(document.getElementById("pilar-ruptura")) document.getElementById("pilar-ruptura").innerText = etiquetaNum(brain.fijos.Mecanica_Ruptura.numero);
    if(document.getElementById("pilar-espejo")) document.getElementById("pilar-espejo").innerText = etiquetaNum(brain.fijos.Espejo_Acuario.numero);

    if(document.getElementById("datoCaliente")) {
      document.getElementById("datoCaliente").innerHTML = `🧠 <b>Análisis de Cinta:</b> Terminales saturadas ayer: <b>${brain.saturadas.join(", ") || 'Ninguna'}</b>. Pirámide de hoy: Vértice <b>${brain.piramide.vertice}</b>. Las jugadas de Ruptura están activas.`;
    }
  });

  // 2. ESCUCHAR RESULTADOS (ÚLTIMO SORTEO EN VIVO)
  onSnapshot(doc(db, "resultados", fechaHoy), (docSnap) => {
    if (!docSnap.exists()) return;
    const data = docSnap.data();
    const horas = ["07:00 PM","06:00 PM","05:00 PM","04:00 PM","03:00 PM","02:00 PM","01:00 PM","12:00 PM","11:00 AM","10:00 AM","09:00 AM","08:00 AM"];
    
    for (let h of horas) {
      if (data.lotto_activo?.[h]?.numero) {
        if(document.getElementById("cierre")) document.getElementById("cierre").innerText = `${h} (LA): ${etiquetaNum(data.lotto_activo[h].numero)}`;
        break;
      }
    }
  });
</script>
