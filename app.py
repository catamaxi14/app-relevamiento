import streamlit as st
import pandas as pd
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from streamlit_geolocation import streamlit_geolocation 

# --- Función para buscar la calle ---
@st.cache_data
def obtener_direccion(lat, lon):
    geolocalizador = Nominatim(user_agent="app_relevamiento_terreno")
    try:
        ubicacion = geolocalizador.reverse((lat, lon), timeout=5, language='es')
        if ubicacion:
            return ubicacion.address
        return "Dirección no encontrada"
    except GeocoderTimedOut:
        return "Error al buscar calle"

# --- Configuración de la página ---
st.set_page_config(page_title="Relevamiento en Terreno", layout="wide")
st.title("⚡ App de Relevamiento (GPS)")

if 'punto_actual' not in st.session_state:
    st.session_state.punto_actual = 699

st.markdown("### 1. Siguiente Punto")
punto = st.number_input("📍 Número de Punto:", value=st.session_state.punto_actual, step=1)
st.divider()

col_izq, col_der = st.columns([1, 1])

with col_izq:
    st.markdown("### 2. Capturar Foto")
    foto_subida = st.file_uploader("Saca la foto o súbela", type=["jpg", "jpeg", "png"])
    if foto_subida:
        st.image(foto_subida, use_container_width=True)

with col_der:
    st.markdown("### 3. Ubicación GPS")
    st.info("Presiona para leer el GPS de tu celular.")
    ubicacion = streamlit_geolocation()
    
    lat, lon = None, None
    if ubicacion['latitude'] is not None and ubicacion['longitude'] is not None:
        lat = ubicacion['latitude']
        lon = ubicacion['longitude']
        st.success(f"✅ GPS: {lat}, {lon}")

if foto_subida is not None and lat is not None:
    st.divider()
    st.markdown("### 4. Datos del Poste")
    
    direccion = obtener_direccion(lat, lon)
    link_maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    
    st.write(f"**Ubicación:** {direccion}")
    st.markdown(f"**[🗺️ Ver en Google Maps]({link_maps})**")
    
    with st.form("formulario_datos", clear_on_submit=True):
        tarea = st.text_input("Tareas a realizar:")
        referencia = st.text_input("Referencia técnica:")
        interferencia = st.text_input("Interferencias:")
        observaciones = st.text_area("Observaciones adicionales:")
        
        boton_guardar = st.form_submit_button(f"💾 Guardar Punto {punto}")
        
        if boton_guardar:
            archivo_bd = "Relevamiento_Final.xlsx"
            nuevo_dato = {
                "Punto": punto, "Latitud": lat, "Longitud": lon,
                "Dirección": direccion, "Tareas": tarea, 
                "Referencia Técnica": referencia,
                "Interferencias": interferencia, "Observaciones": observaciones
            }
            df_nuevo = pd.DataFrame([nuevo_dato])
            
            if os.path.exists(archivo_bd):
                df_existente = pd.read_excel(archivo_bd)
                df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
            else:
                df_final = df_nuevo
                
            df_final.to_excel(archivo_bd, index=False)
            st.session_state.punto_actual = punto + 1
            st.success(f"¡Éxito! Se guardó el Punto {punto}.")

# --- BOTÓN PARA DESCARGAR EL EXCEL AL CELULAR ---
st.divider()
st.markdown("### 📥 Descargar Datos")
if os.path.exists("Relevamiento_Final.xlsx"):
    with open("Relevamiento_Final.xlsx", "rb") as file:
        st.download_button(
            label="⬇️ Descargar Excel con todos los postes",
            data=file,
            file_name="Relevamiento_Final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Aún no hay postes guardados para descargar.")