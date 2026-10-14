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

# Procesar si viene un ítem por parámetro de voz (query params)
if "item" in st.query_params:
    nuevo_item = st.query_params["item"]
    if nuevo_item.strip():
        item_limpio = nuevo_item.strip().capitalize()
        item_limpio = " ".join(item_limpio.split())
        
        if item_limpio in st.session_state.inventario:
            st.session_state.inventario[item_limpio] += 1
        else:
            st.session_state.inventario[item_limpio] = 1
        
        # Limpiar query param para evitar duplicaciones al refrescar
        st.query_params.clear()
        st.rerun()

st.subheader("🎙️ Dictado Directo por Voz")
st.markdown("Tocá el botón grande de abajo, decí el nombre del ítem en voz alta (ej: *'Silla de madera'* o *'Proyector'*) y se registrará automáticamente sumando `+1`.")

# Componente HTML/JS con botón de reconocimiento de voz nativo del navegador
voice_component = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: sans-serif; text-align: center; background-color: transparent; margin: 0; padding: 5px; }
        .mic-btn {
            background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 18px 24px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin: 0 auto;
            width: 100%;
            max-width: 320px;
            transition: all 0.2s ease;
        }
        .mic-btn:active { transform: scale(0.96); background: linear-gradient(135deg, #e03b3b, #ef5350); }
        .status { margin-top: 10px; font-size: 13px; color: #888; font-weight: 500; }
    </style>
</head>
<body>
    <button class="mic-btn" onclick="startRecording()">
        🎙️ Tocar para Hablar
    </button>
    <div class="status" id="status">Listo para escuchar...</div>

    <script>
        function startRecording() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                document.getElementById('status').innerText = "Tu navegador no soporta voz. Usá Google Chrome o Safari.";
                return;
            }
            
            const recognition = new SpeechRecognition();
            recognition.lang = 'es-AR'; // Configurado para español
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            document.getElementById('status').innerText = "🎤 Escuchando... Hablá ahora.";

            recognition.onresult = function(event) {
                const speechResult = event.results[0][0].transcript;
                document.getElementById('status').innerText = "✅ Registrado: " + speechResult;
                // Recargar la app pasando el texto por URL
                window.parent.location.search = '?item=' + encodeURIComponent(speechResult);
            };

            recognition.onerror = function(event) {
                document.getElementById('status').innerText = "⚠️ Error de audio: " + event.error;
            };

            recognition.start();
        }
    </script>
</body>
</html>
"""

components.html(voice_component, height=110)

with st.expander("⌨️ ¿Preferís escribir o corregir manualmente?"):
    with st.form(key="form_item", clear_on_submit=True):
        nuevo_item_manual = st.text_input("Nombre del ítem:", placeholder="Ej: Mesa escolar, Computadora...")
        submitted = st.form_submit_button("➕ Agregar / Sumar 1")
        
        if submitted and nuevo_item_manual.strip():
            item_limpio = nuevo_item_manual.strip().capitalize()
            item_limpio = " ".join(item_limpio.split())
            
            if item_limpio in st.session_state.inventario:
                st.session_state.inventario[item_limpio] += 1
            else:
                st.session_state.inventario[item_limpio] = 1
            st.success(f"Registrado: **{item_limpio}** (+1)")
            st.rerun()

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
    st.info("Todavía no hay ítems cargados. Tocá el botón de voz o escribí arriba para comenzar.")
