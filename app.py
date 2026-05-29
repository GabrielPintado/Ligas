import streamlit as st
import pandas as pd
import numpy as np

# Configuración de página ancha con un diseño limpio
st.set_page_config(
    page_title="Global Football Tracker",
    page_icon="⚽",
    layout="wide"
)

# Estilos CSS avanzados para replicar un layout de software deportivo premium
st.markdown("""
    <style>
    /* Títulos e Interfaz */
    .main-title {
        font-size: 36px !important;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2px;
    }
    .subtitle {
        font-size: 15px;
        color: #4B5563;
        text-align: center;
        margin-bottom: 15px;
    }
    .season-badge {
        background-color: #1E3A8A;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 15px;
    }
    
    /* Simulación de Tabla Avanzada en HTML */
    .table-container {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Source Sans Pro', sans-serif;
    }
    .th-custom {
        background-color: #F3F4F6;
        color: #1F2937;
        font-weight: 700;
        padding: 10px;
        text-align: left;
        border-bottom: 2px solid #E5E7EB;
        font-size: 13px;
    }
    .tr-custom {
        border-bottom: 1px solid #E5E7EB;
        height: 38px;
    }
    .tr-custom:hover {
        background-color: #F9FAFB;
    }
    .td-custom {
        padding: 8px 10px;
        font-size: 14px;
        color: #111827;
    }
    
    /* Indicadores de Clasificación a la Izquierda (Bordes de Color) */
    .border-campeon { border-left: 5px solid #10B981 !important; }
    .border-champions { border-left: 5px solid #3B82F6 !important; }
    .border-europa { border-left: 5px solid #F59E0B !important; }
    .border-conference { border-left: 5px solid #10B981 !important; }
    .border-descenso { border-left: 5px solid #EF4444 !important; }
    .border-normal { border-left: 5px solid #9CA3AF !important; }
    
    /* Panel de Rango Matemático a la Derecha */
    .rango-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        margin-top: 38px; /* Sincronizado con la altura del header de la tabla */
    }
    .rango-box {
        height: 39px; /* Sincronizado exactamente con cada fila */
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #F3F4F6;
        border-radius: 4px;
        margin-bottom: 1px;
        font-size: 12px;
        font-weight: 600;
        color: #374151;
        border: 1px solid #E5E7EB;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚽ Sistema Global de Tabla de Posiciones</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis de zonas de clasificación, descenso y rangos matemáticos potenciales.</p>', unsafe_allow_html=True)

# --- 1. PROCESAMIENTO E INTELIGENCIA DE LOS DATOS ---
@st.cache_data
def cargar_datos_y_logica(liga):
    # Formato de temporadas considerando el año actual 2026
    temporadas = {
        "Premier League (Inglaterra)": "Temporada 2025/2026",
        "LaLiga (España)": "Temporada 2025/2026",
        "Serie A (Italia)": "Temporada 2025/2026",
        "Bundesliga (Alemania)": "Temporada 2025/2026",
        "Ligue 1 (Francia)": "Temporada 2025/2026",
        "Brasileirão (Brasil)": "Temporada 2026",
        "Liga Profesional (Argentina)": "Temporada 2026",
        "Saudi Pro League (Arabia Saudita)": "Temporada 2025/2026",
        "Liga MX (México)": "Torneo Clausura 2026"
    }

    equipos_dict = {
        "Premier League (Inglaterra)": ["Arsenal", "Manchester City", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Manchester United", "Newcastle", "West Ham", "Bournemouth", "Brighton", "Wolves", "Fulham", "Everton", "Brentford", "Nottingham Forest", "Crystal Palace", "Ipswich Town", "Leicester City", "Southampton"],
        "LaLiga (España)": ["Real Madrid", "Barcelona", "Girona", "Atlético de Madrid", "Athletic Club", "Real Sociedad", "Real Betis", "Valencia", "Villarreal", "Getafe", "Osasuna", "Las Palmas", "Alavés", "Sevilla", "Mallorca", "Rayo Vallecano", "Celta de Vigo", "Valladolid", "Leganés", "Espanyol"],
        "Serie A (Italia)": ["Inter", "Milan", "Juventus", "Bologna", "Roma", "Atalanta", "Lazio", "Fiorentina", "Torino", "Napoli", "Genoa", "Monza", "Lecce", "Empoli", "Udinese", "Verona", "Cagliari", "Parma", "Como", "Venezia"],
        "Bundesliga (Alemania)": ["Bayer Leverkusen", "Bayern Munich", "Stuttgart", "RB Leipzig", "Borussia Dortmund", "Eintracht Frankfurt", "Hoffenheim", "Freiburg", "Heidenheim", "Werder Bremen", "Augsburg", "Wolfsburg", "Borussia M'gladbach", "Union Berlin", "Mainz 05", "Bochum", "St. Pauli", "Holstein Kiel"],
        "Ligue 1 (Francia)": ["PSG", "Monaco", "Lille", "Brest", "Nice", "Lens", "Lyon", "Marseille", "Reims", "Rennes", "Toulouse", "Montpellier", "Strasbourg", "Le Havre", "Nantes", "Auxerre", "Angers", "Saint-Étienne"],
        "Brasileirão (Brasil)": ["Palmeiras", "Grêmio", "Atlético Mineiro", "Flamengo", "Botafogo", "Bragantino", "Fluminense", "Athletico Paranaense", "Internacional", "Fortaleza", "São Paulo", "Cuiabá", "Corinthians", "Cruzeiro", "Vasco da Gama", "Bahia", "Vitória", "Juventude", "Criciúma", "Atlético Goianiense"],
        "Liga Profesional (Argentina)": ["River Plate", "Boca Juniors", "Racing Club", "Independiente", "San Lorenzo", "Talleres", "Defensa y Justicia", "Estudiantes", "Godoy Cruz", "Lanús", "Newell's", "Rosario Central", "Argentinos Juniors", "Vélez Sarsfield", "Huracán", "Belgrano", "Unión", "Platense", "Banfield", "Instituto"],
        "Saudi Pro League (Arabia Saudita)": ["Al-Hilal", "Al-Nassr", "Al-Ahli", "Al-Taawoun", "Al-Ittihad", "Al-Ettifaq", "Al-Fateh", "Al-Shabab", "Al-Fayha", "Damac", "Al-Khaleej", "Al-Wehda", "Al-Riyadh", "Al-Khoolod", "Al-Qadsiah", "Al-Orobah"],
        "Liga MX (México)": ["América", "Cruz Azul", "Toluca", "Monterrey", "Tigres", "Chivas", "Pachuca", "Pumas", "Necaxa", "Querétaro", "León", "Juárez", "Atlas", "San Luis", "Mazatlán", "Tijuana", "Puebla", "Santos Laguna"]
    }
    
    equipos = equipos_dict[liga]
    n_equipos = len(equipos)
    
    puntos_base = np.linspace(n_equipos * 3.8, n_equipos * 0.8, n_equipos)
    puntos = np.sort(np.round(puntos_base + np.random.normal(0, 1.2, n_equipos)).astype(int))[::-1]
    
    df = pd.DataFrame({
        "Pos": range(1, n_equipos + 1),
        "Equipo": equipos,
        "PJ": [34 if "Alemania" in liga or "Francia" in liga else 38 for _ in range(n_equipos)],
        "Pts": puntos,
        "DG": np.sort(np.round(np.random.normal(14, 9, n_equipos)).astype(int))[::-1]
    })
    
    # Cálculo Matemático del Rango
    pts_en_juego = 9
    rango_final = []
    clase_borde = []
    
    for idx, row in df.iterrows():
        pos_actual = row["Pos"]
        pts_actuales = row["Pts"]
        
        max_pos = 1
        for o_idx, o_row in df.iterrows():
            if o_idx != idx and o_row["Pts"] > (pts_actuales + pts_en_juego):
                max_pos += 1
        min_pos = n_equipos
        for o_idx, o_row in df.iterrows():
            if o_idx != idx and (o_row["Pts"] + pts_en_juego) < pts_actuales:
                min_pos -= 1
                
        rango_final.append(f"{max_pos}° - {min_pos}°")
        
        # Clasificación por colores para el adorno/borde izquierdo
        if pos_actual == 1:
            clase_borde.append("border-campeon")
        elif "Inglaterra" in liga or "España" in liga or "Italia" in liga:
            if pos_actual in [2, 3, 4]: clase_borde.append("border-champions")
            elif pos_actual == 5: clase_borde.append("border-europa")
            elif pos_actual == 6: clase_borde.append("border-conference")
            elif pos_actual >= (n_equipos - 2): clase_borde.append("border-descenso")
            else: clase_borde.append("border-normal")
        elif "Alemania" in liga:
            if pos_actual in [2, 3, 4]: clase_borde.append("border-champions")
            elif pos_actual == 5: clase_borde.append("border-europa")
            elif pos_actual == 6: clase_borde.append("border-conference")
            elif pos_actual >= (n_equipos - 1): clase_borde.append("border-descenso")
            else: clase_borde.append("border-normal")
        elif "Francia" in liga:
            if pos_actual in [2, 3]: clase_borde.append("border-champions")
            elif pos_actual == 4: clase_borde.append("border-europa")
            elif pos_actual == 5: clase_borde.append("border-conference")
            elif pos_actual >= (n_equipos - 2): clase_borde.append("border-descenso")
            else: clase_borde.append("border-normal")
        elif "Brasil" in liga:
            if pos_actual in range(2, 7): clase_borde.append("border-champions") # Libertadores
            elif pos_actual in range(7, 13): clase_borde.append("border-europa") # Sudamericana
            elif pos_actual >= (n_equipos - 3): clase_borde.append("border-descenso")
            else: clase_borde.append("border-normal")
        elif "Argentina" in liga:
            if pos_actual in range(2, 5): clase_borde.append("border-champions") # Libertadores
            elif pos_actual in range(5, 10): clase_borde.append("border-europa") # Sudamericana
            elif pos_actual == n_equipos: clase_borde.append("border-descenso")
            else: clase_borde.append("border-normal")
        elif "Arabia" in liga:
            if pos_actual in [2, 3]: clase_borde.append("border-champions") # AFC
            elif pos_actual >= (n_equipos - 2): clase_borde.append("border-descenso")
            else: clase_borde.append("border-normal")
        else: # México
            if pos_actual in range(2, 7): clase_borde.append("border-champions") # Liguilla
            elif pos_actual in range(7, 11): clase_borde.append("border-europa") # Play-In
            else: clase_borde.append("border-normal")

    df["BordeClase"] = clase_borde
    df["RangoMat"] = rango_final
    return df, temporadas[liga]

# --- 2. ESTRUCTURA DE LAS PESTAÑAS ---
tab1, tab2 = st.tabs(["📊 Tablas Interactivas y Margen Matemático", "📈 Estadísticas Avanzadas"])

with tab1:
    liga_seleccionada = st.selectbox(
        "🏆 Selecciona una Competición:",
        ["Premier League (Inglaterra)", "LaLiga (España)", "Serie A (Italia)", "Bundesliga (Alemania)", 
         "Ligue 1 (Francia)", "Brasileirão (Brasil)", "Liga Profesional (Argentina)", 
         "Saudi Pro League (Arabia Saudita)", "Liga MX (México)"]
    )
    
    df_liga, temporada_texto = cargar_datos_logica(liga_seleccionada)
    
    # 1. Indicador de Temporada arriba de la tabla
    st.markdown(f'<div class="season-badge">🗓️ {temporada_texto}</div>', unsafe_allow_html=True)
    
    # Leyenda Integrada Orientativa
    st.markdown("""
    <div style="display: flex; gap: 15px; margin-bottom: 15px; font-size: 12px; font-weight: bold;">
        <span style="border-left: 4px solid #10B981; padding-left: 5px; color: #065F46;">🟢 Campeón / Playoffs</span>
        <span style="border-left: 4px solid #3B82F6; padding-left: 5px; color: #1E40AF;">🔵 Competencia Internac. Principal</span>
        <span style="border-left: 4px solid #F59E0B; padding-left: 5px; color: #92400E;">🟡 Competencia Internac. Secundaria</span>
        <span style="border-left: 4px solid #EF4444; padding-left: 5px; color: #991B1B;">🔴 Peligro / Descenso</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Creación del layout dividido: Tabla a la izquierda (83%) y Rango matemático a la derecha (17%)
    col_tabla, col_rango = st.columns([83, 17])
    
    with col_tabla:
        # 2. Renderización de la tabla con estilos CSS puros (Inyección del adorno a la izquierda)
        html_table = '<table class="table-container"><thead><tr>'
        html_table += '<th class="th-custom" style="width: 80px;">Posición</th>'
        html_table += '<th class="th-custom">Equipo</th>'
        html_table += '<th class="th-custom" style="width: 80px;">PJ</th>'
        html_table += '<th class="th-custom" style="width: 80px;">DG</th>'
        html_table += '<th class="th-custom" style="width: 100px;">Puntos</th>'
        html_table += '</tr></thead><tbody>'
        
        for _, row in df_liga.iterrows():
            html_table += f'<tr class="tr-custom">'
            html_table += f'<td class="td-custom {row["BordeClase"]}" style="font-weight: bold; text-align: center;">{row["Pos"]}°</td>'
            html_table += f'<td class="td-custom" style="font-weight: 500;">{row["Equipo"]}</td>'
            html_table += f'<td class="td-custom">{row["PJ"]}</td>'
            html_table += f'<td class="td-custom" style="color: {"#10B981" if row["DG"] >= 0 else "#EF4444"}">{row["DG"]}</td>'
            html_table += f'<td class="td-custom" style="font-weight: bold; background-color: #F9FAFB;">{row["Pts"]}</td>'
            html_table += '</tr>'
            
        html_table += '</tbody></table>'
        st.markdown(html_table, unsafe_allow_html=True)
        
    with col_rango:
        # Header alineado del panel derecho
        st.markdown('<div style="font-weight: 700; font-size: 13px; color: #1F2937; padding: 10px 0; border-bottom: 2px solid #E5E7EB; text-align: center; height: 40px;">Rango Pos.</div>', unsafe_allow_html=True)
        
        # 3. Línea exterior acoplada que muestra el rango matemático por cada fila
        rango_html = '<div class="rango-container">'
        for _, row in df_liga.iterrows():
            rango_html += f'<div class="rango-box" title="Límites matemáticos actuales para {row["Equipo"]}">{row["RangoMat"]}</div>'
        rango_html += '</div>'
        st.markdown(rango_html, unsafe_allow_html=True)

with tab2:
    st.subheader(" McKinley Analítica Gráfica")
    st.info("Pestaña de analítica en desarrollo. Aquí se integrarán gráficos de dispersión de ataque/defensa y evolución de jornadas.")
