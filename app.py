import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(
    page_title="Relevamiento Escolar por Voz",
    page_icon="🏫",
    layout="centered"
)

st.title("🏫 Relevamiento Áulico Rápido")
st.markdown("---")

if "inventario" not in st.session_state:
    st.session_state.inventario = {}

st.info(
    "💡 **Consejo de velocidad:** Tocá el cuadro de texto y usá el **micrófono del teclado de tu celular** (la tecla de dictado de Gboard o iOS). "
    "Decí el ítem y presioná **Agregar**. Si repetís el nombre de un objeto, sumará `+1` automáticamente."
)

with st.form(key="form_inventario", clear_on_submit=True):
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        nuevo_item = st.text_input(
            "Nombre del ítem:",
            placeholder="Ej: Silla, Banco, Proyector...",
            label_visibility="collapsed"
        )
    with col_btn:
        submitted = st.form_submit_button("➕ Agregar", use_container_width=True)
    
    if submitted and nuevo_item.strip():
        item_limpio = nuevo_item.strip().capitalize()
        item_limpio = " ".join(item_limpio.split())
        
        if item_limpio in st.session_state.inventario:
            st.session_state.inventario[item_limpio] += 1
        else:
            st.session_state.inventario[item_limpio] = 1
        st.toast(f"✅ Registrado: {item_limpio} (+1)", icon="🎯")

st.markdown("---")
st.subheader("📋 Planilla en Tiempo Real")

if st.session_state.inventario:
    data = [
        {"Ítem / Descripción": k, "Cantidad": v} 
        for k, v in st.session_state.inventario.items()
    ]
    df = pd.DataFrame(data)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col_reset, col_export = st.columns(2)
    
    with col_reset:
        if st.button("🗑️ Reiniciar Todo", use_container_width=True):
            st.session_state.inventario = {}
            st.rerun()
            
    with col_export:
        output_filename = f"relevamiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
        
        st.download_button(
            label="📥 Descargar Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=output_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
else:
    st.warning("⚠️ Todavía no hay ítems registrados en este relevamiento.")
