import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Relevamiento de Inventario Escolar",
    page_icon="🏫",
    layout="centered"
)

st.title("🏫 Relevamiento Áulico por Voz")
st.markdown("---")

# Inicializar estado de sesión para el inventario
if "inventario" not in st.session_state:
    st.session_state.inventario = {}

# Procesar si viene un ítem por parámetro de URL (desde el componente web)
if "item" in st.query_params:
    raw_item = st.query_params["item"]
    nuevo_item = raw_item[0] if isinstance(raw_item, list) else raw_item
    if nuevo_item and str(nuevo_item).strip():
        item_limpio = str(nuevo_item).strip().capitalize()
        item_limpio = " ".join(item_limpio.split())
        
        if item_limpio in st.session_state.inventario:
            st.session_state.inventario[item_limpio] += 1
        else:
            st.session_state.inventario[item_limpio] = 1
        
        # Limpiar query param y recargar para evitar duplicados
        st.query_params.clear()
        st.rerun()

st.subheader("📝 Ingreso de Ítems (Voz o Teclado)")
st.markdown("Tocá el ícono de **micrófono 🎙️** dentro del cuadro para dictar el objeto, o escribilo manualmente. Se agregará al instante.")

# Componente HTML/JS con input integrado y botón de micrófono adentro
input_voice_component = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: sans-serif; background-color: transparent; margin: 0; padding: 5px; }
        .input-container {
            display: flex;
            align-items: center;
            background: white;
            border: 2px solid #ccc;
            border-radius: 12px;
            padding: 4px 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            max-width: 100%;
            transition: all 0.3s;
        }
        .input-container:focus-within {
            border-color: #ff4b4b;
            box-shadow: 0 0 8px rgba(255, 75, 75, 0.3);
        }
        .text-input {
            flex: 1;
            border: none;
            outline: none;
            font-size: 16px;
            padding: 10px;
            background: transparent;
            color: #31333F;
        }
        .mic-btn {
            background: #ff4b4b;
            color: white;
            border: none;
            border-radius: 8px;
            width: 44px;
            height: 44px;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s, transform 0.1s;
            flex-shrink: 0;
            margin-left: 5px;
        }
        .mic-btn:active { transform: scale(0.92); background: #e03b3b; }
        .mic-btn.listening { background: #28a745; animation: pulse 1.5s infinite; }
        .submit-btn {
            background: #2b313e;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0 16px;
            height: 44px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            margin-left: 5px;
            flex-shrink: 0;
        }
        .submit-btn:active { background: #000; }
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4); }
            70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
        }
        .status { font-size: 12px; color: #666; margin-top: 6px; text-align: center; }
    </style>
</head>
<body>
    <form id="itemForm" onsubmit="enviarItem(event)">
        <div class="input-container">
            <input type="text" id="itemInput" class="text-input" placeholder="Ej: Silla, Banco, Proyector..." autocomplete="off" required>
            <button type="button" class="mic-btn" id="micBtn" onclick="toggleSpeech()" title="Dictar por voz">🎙️</button>
            <button type="submit" class="submit-btn" title="Agregar ítem">➕</button>
        </div>
        <div class="status" id="statusMsg">Toca el micrófono para hablar o escribe el ítem</div>
    </form>

    <script>
        let recognition = null;
        let isListening = false;

        function toggleSpeech() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert("Tu navegador no soporta reconocimiento de voz. Usá Google Chrome.");
                return;
            }

            if (isListening) {
                if (recognition) recognition.stop();
                return;
            }

            recognition = new SpeechRecognition();
            recognition.lang = 'es-AR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            const micBtn = document.getElementById('micBtn');
            const statusMsg = document.getElementById('statusMsg');
            const inputField = document.getElementById('itemInput');

            recognition.onstart = function() {
                isListening = true;
                micBtn.classList.add('listening');
                micBtn.innerHTML = "⏹️";
                statusMsg.innerText = "🎤 Escuchando... Hablá ahora.";
            };

            recognition.onresult = function(event) {
                const speechResult = event.results[0][0].transcript;
                inputField.value = speechResult;
                statusMsg.innerText = "✅ ¡Reconocido! Agregando...";
                setTimeout(() => {
                    document.getElementById('itemForm').requestSubmit();
                }, 300);
            };

            recognition.onerror = function(event) {
                statusMsg.innerText = "⚠️ Error: " + event.error;
                stopListeningState();
            };

            recognition.onend = function() {
                stopListeningState();
            };

            recognition.start();
        }

        function stopListeningState() {
            isListening = false;
            const micBtn = document.getElementById('micBtn');
            micBtn.classList.remove('listening');
            micBtn.innerHTML = "🎙️";
        }

        function enviarItem(event) {
            event.preventDefault();
            const val = document.getElementById('itemInput').value.trim();
            if (val) {
                // Usar location.search en lugar de location.href para mantener la sesión activa en Streamlit
                window.parent.location.search = '?item=' + encodeURIComponent(val);
            }
        }
    </script>
</body>
</html>
"""

components.html(input_voice_component, height=95)

st.markdown("---")
st.subheader("📋 Planilla Actual en Tiempo Real")

if st.session_state.inventario:
    data = [
        {"Ítem / Descripción": k, "Cantidad": v} 
        for k, v in st.session_state.inventario.items()
    ]
    df = pd.DataFrame(data)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Reiniciar Todo"):
            st.session_state.inventario = {}
            st.rerun()
            
    with col2:
        output_filename = f"relevamiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
        
        st.download_button(
            label="📥 Descargar Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=output_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
else:
    st.info("Todavía no hay ítems cargados. Tocá el micrófono en la barra de arriba o dictá para comenzar.")
