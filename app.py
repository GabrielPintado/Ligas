import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Configuración de página ancha y limpia
st.set_page_config(
    page_title="Global Football Tracker",
    page_icon="⚽",
    layout="wide"
)

# Estilos CSS personalizados para la cabecera
st.markdown("""
    <style>
    .main-title {
        font-size: 38px !important;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 16px;
        color: #4B5563;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚽ Sistema Global de Tabla de Posiciones</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis interactivo de zonas de clasificación, descenso y rangos matemáticos potenciales.</p>', unsafe_allow_html=True)

# --- 1. GENERACIÓN SIMULADA E INTELIGENTE DE DATOS DE LAS LIGAS ---
@st.cache_data
def cargar_datos_liga(liga):
    # Equipos reales por liga
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
    
    # Simulación descendente realista de puntos
    puntos_base = np.linspace(n_equipos * 3.8, n_equipos * 0.8, n_equipos)
    puntos = np.round(puntos_base + np.random.normal(0, 1.5, n_equipos)).astype(int)
    puntos = np.sort(puntos)[::-1]
    
    df = pd.DataFrame({
        "Pos": range(1, n_equipos + 1),
        "Equipo": equipos,
        "PJ": [34 if "Alemania" in liga or "Francia" in liga else 38 for _ in range(n_equipos)],
        "Pts": puntos,
        "DG": np.sort(np.round(np.random.normal(12, 10, n_equipos)).astype(int))[::-1]
    })
    
    # --- CÁLCULO MATEMÁTICO DEL RANGO DE POSICIONES POSIBLES (Faltan 3 fechas = 9 Pts) ---
    pts_en_juego = 9
    rango_min = []
    rango_max = []
    
    for idx, row in df.iterrows():
        pts_actuales = row["Pts"]
        
        # Mejor posición matemática posible (Si sumas todo y el resto pierde)
        max_pos = 1
        for o_idx, o_row in df.iterrows():
            if o_idx != idx and o_row["Pts"] > (pts_actuales + pts_en_juego):
                max_pos += 1
                
        # Peor posición matemática posible (Si no sumas nada y el resto gana)
        min_pos = n_equipos
        for o_idx, o_row in df.iterrows():
            if o_idx != idx and (o_row["Pts"] + pts_en_juego) < pts_actuales:
                min_pos -= 1
                
        rango_min.append(max_pos)
        rango_max.append(min_pos)
        
    df["Rango Matemático"] = [f"{mi}° al {ma}°" for mi, ma in zip(rango_min, rango_max)]
    return df

# --- 2. CONFIGURACIÓN DE REGLAS DE CADA TORNEO ---
def obtener_reglas_liga(liga, total_equipos):
    if "Inglaterra" in liga or "España" in liga or "Italia" in liga:
        return {"campeon": [1], "champions": [2, 3, 4], "europa_league": [5], "conference": [6], "descenso": list(range(total_equipos-2, total_equipos+1))}
    elif "Alemania" in liga:
        return {"campeon": [1], "champions": [2, 3, 4], "europa_league": [5], "conference": [6], "descenso": list(range(total_equipos-1, total_equipos+1))}
    elif "Francia" in liga:
        return {"campeon": [1], "champions": [2, 3], "europa_league": [4], "conference": [5], "descenso": list(range(total_equipos-2, total_equipos+1))}
    elif "Brasil" in liga:
        return {"campeon": [1], "champions": list(range(2, 7)), "europa_league": list(range(7, 13)), "conference": [], "descenso": list(range(total_equipos-3, total_equipos+1))} # Libertadores y Sudamericana
    elif "Argentina" in liga:
        return {"campeon": [1], "champions": list(range(2, 5)), "europa_league": list(range(5, 10)), "conference": [], "descenso": [total_equipos]}
    elif "Arabia" in liga:
        return {"campeon": [1], "champions": [2, 3], "europa_league": [], "conference": [], "descenso": list(range(total_equipos-2, total_equipos+1))}
    else: # México (Clasificación a Liguilla Directa y Play-In)
        return {"campeon": [1], "champions": list(range(2, 7)), "europa_league": list(range(7, 11)), "conference": [], "descenso": []}

# --- 3. DISEÑO DE LAS PESTAÑAS ---
tab1, tab2 = st.tabs(["📊 Tablas Interactivas y Margen Matemático", "📈 Estadísticas Avanzadas"])

with tab1:
    # Selector Estilizado
    liga_seleccionada = st.selectbox(
        "🏆 Selecciona una Competición:",
        ["Premier League (Inglaterra)", "LaLiga (España)", "Serie A (Italia)", "Bundesliga (Alemania)", 
         "Ligue 1 (Francia)", "Brasileirão (Brasil)", "Liga Profesional (Argentina)", 
         "Saudi Pro League (Arabia Saudita)", "Liga MX (México)"]
    )
    
    df_liga = cargar_datos_liga(liga_seleccionada)
    reglas = obtener_reglas_liga(liga_seleccionada, len(df_liga))
    
    # Leyenda de Colores de las Filas
    st.markdown("""
    <div style="display: flex; gap: 15px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; font-size: 13px;">
        <span style="background-color: #D1FAE5; padding: 4px 10px; border-radius: 4px; font-weight: bold; color: #065F46;">🏆 Líder / Campeón</span>
        <span style="background-color: #DBEAFE; padding: 4px 10px; border-radius: 4px; font-weight: bold; color: #1E40AF;">🇪🇺/🌎 Competencia Principal</span>
        <span style="background-color: #FEF3C7; padding: 4px 10px; border-radius: 4px; font-weight: bold; color: #92400E;">🎟️ Competencia Secundaria</span>
        <span style="background-color: #FEE2E2; padding: 4px 10px; border-radius: 4px; font-weight: bold; color: #991B1B;">🔻 Zona de Descenso / Peligro</span>
    </div>
    """, unsafe_allow_html=True)

    # --- CONFIGURACIÓN DE AG-GRID CON JAVASCRIPT ---
    gb = GridOptionsBuilder.from_dataframe(df_liga)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    
    # JavaScript para pintar las filas según la posición real de la liga
    row_style_jscode = JsCode(f"""
    function(params) {{
        var pos = params.data.Pos;
        var reglas = {reglas};
        
        if (reglas.campeon.includes(pos)) {{
            return {{'backgroundColor': '#D1FAE5', 'color': '#065F46', 'fontWeight': 'bold'}};
        }}
        if (reglas.champions.includes(pos)) {{
            return {{'backgroundColor': '#DBEAFE', 'color': '#1E40AF'}};
        }}
        if (reglas.europa_league.includes(pos) || reglas.conference.includes(pos)) {{
            return {{'backgroundColor': '#FEF3C7', 'color': '#92400E'}};
        }}
        if (reglas.descenso.includes(pos)) {{
            return {{'backgroundColor': '#FEE2E2', 'color': '#991B1B'}};
        }}
        return null;
    }}
    """)
    
    # Activar Tooltip dinámico al pasar el mouse sobre el Equipo
    gb.configure_column("Equipo", cellTooltipField="Rango Matemático", headerTooltip="Pasa el mouse sobre el equipo para ver su rango")
    gb.configure_column("Rango Matemático", pin="right", cellStyle={'font-weight': 'bold', 'background-color': '#F3F4F6', 'text-align': 'center'})
    
    gridOptions = gb.build()
    gridOptions['getRowStyle'] = row_style_jscode

    st.markdown("💡 *Tip: Coloca el cursor sobre el nombre de cualquier **Equipo** para ver de forma flotante su rango matemático sin perder el orden.*")
    
    # Renderizado de la tabla interactiva
    AgGrid(
        df_liga,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True, 
        enable_enterprise_modules=False,  # Elimina avisos o marcas de agua comerciales
        theme='balham'
    )

with tab2:
    st.subheader("📈 Rendimiento y Métricas del Torneo")
    st.info("Pestaña de analítica en desarrollo. Aquí se integrarán gráficos de dispersión de ataque/defensa y evolución de jornadas.")
    
    # Métricas de diseño rápido para completar la vista premium
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Puntaje Máximo Registrado", value=f"{df_liga['Pts'].max()} Pts", delta="Puntero")
    with c2:
        st.metric(label="Promedio Diferencia de Goles", value=f"{round(df_liga['DG'].mean(), 1)}", delta="Competitividad")
    with c3:
        st.metric(label="Puntos Críticos de Salvación", value=f"{df_liga['Pts'].iloc[-4]} Pts", delta="Margen del Descenso")
