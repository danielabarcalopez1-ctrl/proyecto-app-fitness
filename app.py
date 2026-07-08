import streamlit as st
import sqlite3
import pandas as pd
import datetime
import plotly.graph_objects as go # Usaremos graph_objects para mayor control en los anillos

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cal.AI Style App", page_icon="🍎", layout="centered")

# --- CSS PERSONALIZADO (Estilo Cal.ai) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #f3f4f6; /* Gris muy claro */
    }
    
    /* Encabezado (Fecha y Logo) */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
    }
    .logo-text {
        font-size: 1.25rem;
        font-weight: bold;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #111827;
    }
    .date-selector {
        display: flex;
        gap: 15px;
        font-size: 0.875rem;
        color: #6b7280;
        cursor: pointer;
    }
    .selected-date {
        color: #111827;
        font-weight: 600;
        border-bottom: 2px solid #111827;
    }

    /* Tarjeta Principal (Calorías) */
    .main-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .calories-number {
        font-size: 3rem;
        font-weight: 800;
        color: #111827;
        line-height: 1;
    }
    .calories-label {
        font-size: 0.875rem;
        color: #6b7280;
        margin-top: 5px;
    }

    /* Tarjetas de Macros (Proteína, Carbs, Grasas) */
    .macros-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    .macro-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        flex: 1;
        text-align: center;
        position: relative;
    }
    .macro-label {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 8px;
    }
    .macro-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
    }

    /* Sección Recientemente Subidos */
    .section-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 15px;
    }
    .food-item-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .food-item-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .food-icon {
        font-size: 1.5rem;
    }
    .food-details {
        font-size: 0.875rem;
    }
    .food-name {
        font-weight: 600;
        color: #111827;
    }
    .food-kcal {
        color: #6b7280;
    }
    .food-time {
        font-size: 0.75rem;
        color: #9ca3af;
        text-align: right;
    }
    
    /* Botón Flotante '+') */
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
        z-index: 9999 !important;
    }
    .stButton > button.st-primary:hover {
        background-color: #1f2937 !important;
    }

    /* Ocultar el header/footer de Streamlit */
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha DATE)''')
conn.commit()

# --- LÓGICA DE DATOS ---
fecha_hoy = datetime.date.today()

def get_totals_for_today():
    # Asumimos que ya existe una columna fecha por los commits anteriores
    df = pd.read_sql(f"SELECT * FROM alimentos WHERE fecha = '{fecha_hoy}'", conn)
    if df.empty:
        return 0, 0, 0, 0
    return df['prot'].sum(), df['carbs'].sum(), df['grasas'].sum(), df['kcal'].sum()

total_p, total_c, total_g, total_k = get_totals_for_today()
meta_cal = 2500 # Meta de ejemplo

# --- INTERFAZ UI ---

# 1. Cabecera
st.markdown("""
<div class="header-container">
    <div class="logo-text">🍎 Cal AI</div>
    <div class="date-selector">
        <div>Today</div>
        <div>Yesterday</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Tarjeta Principal (Calorías)
st.markdown(f"""
<div class="main-card">
    <div>
        <div class="calories-number">{total_k:.0f}</div>
        <div class="calories-label">Calories left</div>
    </div>
    <div>
        {create_progress_donut(total_k, meta_cal, "#10b981")} </div>
</div>
""", unsafe_allow_html=True)

# 3. Tarjetas de Macros
def create_progress_donut(current, goal, color):
    # Función auxiliar para generar el anillo con Plotly
    value = min(current, goal)
    remaining = goal - value
    fig = go.Figure(data=[go.Pie(
        values=[value, remaining],
        hole=.85,
        marker_colors=[color, '#e5e7eb'], # Color de meta, color de fondo
        textinfo='none',
        hoverinfo='none',
        direction='clockwise',
        sort=False
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=70,
        width=70,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=False)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""<div class="macro-card">""", unsafe_allow_html=True)
    create_progress_donut(total_p, 150, "#ef4444") # Meta prot 150g
    st.markdown(f"""<div class="macro-label">Protein over</div><div class="macro-value">{total_p:.0f}g</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class="macro-card">""", unsafe_allow_html=True)
    create_progress_donut(total_c, 250, "#f97316") # Meta carbs 250g
    st.markdown(f"""<div class="macro-label">Carbs left</div><div class="macro-value">{total_c:.0f}g</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="macro-card">""", unsafe_allow_html=True)
    create_progress_donut(total_g, 65, "#3b82f6") # Meta grasas 65g
    st.markdown(f"""<div class="macro-label">Fats left</div><div class="macro-value">{total_g:.0f}g</div></div>""", unsafe_allow_html=True)


# 4. Sección Recientemente Subidos
st.markdown("""<div class="section-title">Recently uploaded</div>""", unsafe_allow_html=True)

# Obtener y mostrar los ítems recientes de hoy
df_recent = pd.read_sql(f"SELECT * FROM alimentos WHERE fecha = '{fecha_hoy}' ORDER BY timestamp DESC LIMIT 5", conn)

for index, row in df_recent.iterrows():
    # Usaremos un icono por defecto para la comida
    st.markdown(f"""
    <div class="food-item-card">
        <div class="food-item-left">
            <div class="food-icon">🍲</div>
            <div class="food-details">
                <div class="food-name">{row['nombre']}</div>
                <div class="food-kcal">{row['kcal']:.0f} calories</div>
            </div>
        </div>
        <div class="food-time">
            {pd.to_datetime(row['timestamp']).strftime('%I:%M %p')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. Botón Flotante '+' (Abre el panel lateral para loggear comida)
if st.button("+", type="primary"):
    st.session_state['show_log_modal'] = True

# --- PANEL DE ENTRADA (SIDEBAR MEJORADO) ---
with st.sidebar:
    st.header("Log Food")
    nombre_input = st.text_input("Food Name")
    c1, c2 = st.columns(2)
    with c1:
        prot_input = st.number_input("Protein (g)", min_value=0.0)
    with c2:
        carb_input = st.number_input("Carbs (g)", min_value=0.0)
    c3, c4 = st.columns(2)
    with c3:
        fat_input = st.number_input("Fat (g)", min_value=0.0)
    
    # Calculo automático simplificado de calorías
    kcal_calc = (prot_input * 4) + (carb_input * 4) + (fat_input * 9)
    st.write(f"**Estimated Calories: {kcal_calc:.0f} kcal**")

    if st.button("Add to Log"):
        c.execute("INSERT INTO alimentos (nombre, prot, carbs, grasas, kcal, fecha) VALUES (?,?,?,?,?,?)", 
                    (nombre_input, prot_input, carb_input, fat_input, kcal_calc, fecha_hoy))
        conn.commit()
        st.success("✅ Logged")
        st.rerun() # Actualizar la página

# --- PASOS TÉCNICOS PARA QUE FUNCIONE ---

# Si no lo hiciste antes, tu base de datos necesita la columna 'timestamp'
# Para solucionarlo, borra el archivo dieta.db de GitHub. Streamlit creará la base de datos con la nueva estructura al reiniciar.
# Además, asegúrate de añadir 'plotly' y 'pandas' a tu requirements.txt.
