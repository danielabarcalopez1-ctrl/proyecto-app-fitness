import streamlit as st
import sqlite3
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="App de Nutrición", page_icon="💪")
st.title("💪 Nutrición: Objetivo Ripiado")

# Conexión a DB
conn = sqlite3.connect('dieta.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS alimentos (nombre TEXT, prot REAL, kcal REAL)')
conn.commit()

# Sidebar para inputs
with st.sidebar:
    st.header("Registrar Comida")
    nombre = st.text_input("Alimento")
    prot = st.number_input("Proteína (g)", 0.0)
    kcal = st.number_input("Calorías (kcal)", 0.0)
    if st.button("Añadir"):
        c.execute('INSERT INTO alimentos VALUES (?,?,?)', (nombre, prot, kcal))
        conn.commit()
        st.success("Guardado!")

# Mostrar datos
st.subheader("Tu consumo de hoy")
df = pd.read_sql('SELECT * FROM alimentos', conn)
st.dataframe(df)

# Cálculos rápidos
if not df.empty:
    st.metric("Total Proteína", f"{df['prot'].sum()} g")
    st.metric("Total Calorías", f"{df['kcal'].sum()} kcal")