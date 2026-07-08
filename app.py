import streamlit as st
import sqlite3
import pandas as pd
import datetime
import plotly.express as px # Asegúrate de añadir 'plotly' a tu requirements.txt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cal.ai Style Dashboard", page_icon="🍎", layout="centered")

# --- ESTILO PERSONALIZADO (CSS para imitar la UI de Cal.ai) ---
# Fondo claro, tarjetas blancas con sombra, fuentes limpias
st.markdown("""
    <style>
    /* Fondo general muy claro */
    .stApp {
        background-color: #f9f9f9;
    }
    
    /* Encabezado */
    h1, h2, h3 {
        color: #111827;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Tarjeta principal flotante (estilo overlay) */
    .floating-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 25px;
    }
    
    /* Texto de números grandes */
    .big-number {
        font-size: 3rem;
        font-weight: 800;
        color: #111827;
        line-height: 1;
    }
    .small-label {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 5px;
    }

    /* Pequeñas tarjetas de macros */
    .macro-card {
        background-color: #f3f4f6;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }
    .macro-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
    }
    .macro-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    /* Barra de progreso (usaremos la nativa, pero estilizaremos su contenedor) */
    .stProgress > div > div {
        background-color: #10b981; /* Color verde de la meta */
    }
    
    /* Botón de acción flotante (estilo '+') */
    .stButton > button.st-primary {
        background-color: #111827 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 56px !important;
        height: 56px !important;
        font-size: 24px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: none !important;
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 999 !important;
    }
    .stButton > button.st-primary:hover {
        background-color: #1f2937 !important;
    }

    /* Ocultar el header y footer de Streamlit para una experiencia más app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
conn = sqlite3.connect('dieta.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS alimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                prot REAL,
                carbs REAL,
                grasas REAL,
                kcal REAL,
                fecha DATE)''')
conn.commit()

# Lógica para obtener datos de hoy
fecha_hoy = datetime.date.today()

def get_totals_for_today():
    df = pd.read_sql_query(f"SELECT * FROM alimentos WHERE fecha = '{fecha_hoy}'", conn)
    if df.empty:
        return 0, 0, 0, 0
    return df['prot'].sum(), df['carbs'].sum(), df['grasas'].sum(), df['kcal'].sum()

total_p, total_c, total_g, total_k = get_totals_for_today()
meta_cal = 2000 # Meta de ejemplo

# Título superior (como en la app)
st.markdown(f"### 🍎 Cal AI  |  {fecha_hoy.strftime('%a, %b %d')}")

# --- TARJETA FLOTANTE PRINCIPAL (Calorías) ---
st.markdown("""
<div class="floating-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="small-label">Calories earen</div>
            <div class="big-number">{:.0f}<span style="font-size: 1rem; color: #6b7280;">/{:.0f}</span></div>
        </div>
        <div>
            <div class="small-label" style="text-align: right;">Streak</div>
            <div class="big-number" style="text-align: right; color: #f59e0b;">🔥 15</div>
        </div>
    </div>
    <br>
    <div style="background-color: #e5e7eb; border-radius: 10px; height: 8px;">
        <div style="background-color: #10b981; width: {:.0f}%; height: 8px; border-radius: 10px;"></div>
    </div>
    <div class="small-label" style="text-align: center; margin-top: 5px;">{:.0f}% of goal</div>
</div>
""".format(total_k, meta_cal, (total_k / meta_cal) * 100 if meta_cal > 0 else 0, (total_k / meta_cal) * 100 if meta_cal > 0 else 0), unsafe_allow_html=True)


# --- PANELES DE RESUMEN DE MACROS (Estilo Cal.ai) ---
col1, col2, col3 = st.columns(3)

def macro_card(col, label, value, goal, color):
    percent = (value / goal * 100) if goal > 0 else 0
    col.markdown(f"""
    <div class="macro-card">
        <div class="macro-label" style="color: {color};">{label}</div>
        <div class="macro-value">{value:.0f}<span style="font-size: 1rem; color: #6b7280;">/{goal:.0f}g</span></div>
        <br>
        <div style="background-color: #d1d5db; border-radius: 10px; height: 6px;">
             <div style="background-color: {color}; width: {percent}%; height: 6px; border-radius: 10px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

macro_card(col1, "Protein", total_p, 150, "#ef4444") # Meta de proteína de ejemplo
macro_card(col2, "Carbs", total_c, 250, "#f97316") # Meta de carbohidratos de ejemplo
macro_card(col3, "Fat", total_g, 65, "#3b82f6") # Meta de grasas de ejemplo

st.write("---")

# --- SECCIÓN RECIENTEMENTE SUBIDOS (Tabla y gráfico) ---
st.subheader("Recently uploaded")

# Mostrar la tabla de datos debajo
df_hoy = pd.read_sql(f"SELECT nombre, kcal, prot, carbs, grasas FROM alimentos WHERE fecha = '{fecha_hoy}'", conn)
st.dataframe(df_hoy, use_container_width=True, hide_index=True)

# Gráfico visual (tipo anillo) para el día actual
if total_p + total_c + total_g > 0:
    macros_data = {
        'Macro': ['Protein', 'Carbs', 'Fat'],
        'Gramos': [total_p, total_c, total_g]
    }
    fig = px.pie(macros_data, values='Gramos', names='Macro', hole=0.8, color='Macro', 
                 color_discrete_map={'Protein': '#ef4444', 'Carbs': '#f97316', 'Fat': '#3b82f6'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Log your first meal of the day using the '+' button.")

# --- BOTÓN DE ACCIÓN FLOTANTE (El '+') ---
# Al hacer clic, esto abrirá una ventana modal (para un input más complejo)
if st.button("+", type="primary"):
    st.session_state['show_modal'] = True

# Lógica para mostrar un modal simple (usando st.dialog en versiones modernas de Streamlit, o un expansor/sidebar)
# Para mantenerlo simple y compatible con el diseño ahora mismo, usaremos el sidebar como panel lateral de entrada
# pero con un botón principal en el menú inferior.
with st.sidebar:
    st.header("Log Food")
    nombre = st.text_input("Food Name")
    c1, c2 = st.columns(2)
    with c1:
        prot_in = st.number_input("Protein (g)", min_value=0.0)
    with c2:
        carbs_in = st.number_input("Carbs (g)", min_value=0.0)
    c3, c4 = st.columns(2)
    with c3:
        fat_in = st.number_input("Fat (g)", min_value=0.0)
    
    # Calculo automático de calorías (simplificado)
    kcal_est = (prot_in * 4) + (carbs_in * 4) + (fat_in * 9)
    st.write(f"**Estimated Calories: {kcal_est:.0f} kcal**")

    if st.button("Add to Today's Log"):
        c.execute("INSERT INTO alimentos (nombre, prot, carbs, grasas, kcal, fecha) VALUES (?,?,?,?,?,?)", 
                    (nombre, prot_in, carbs_in, fat_in, kcal_est, fecha_hoy))
        conn.commit()
        st.success("✅ Logged")
        st.rerun() # Actualizar la página
