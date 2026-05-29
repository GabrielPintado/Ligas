import streamlit as st
import pandas as pd
import numpy as np

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
st.markdown('<p class="subtitle">Análisis de zonas de clasificación, descenso y rangos matemáticos potenciales.</p>', unsafe_allow_html=True)

# --- 1. GENERACIÓN SIMULADA E INTELIGENTE DE DATOS DE LAS LIGAS ---
@st.cache_data
def cargar_datos_liga(liga):
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
    puntos = np.round(puntos_base + np.random.normal(0, 1.5, n_equipos)).astype(int)
    puntos = np.sort(puntos)[::-1]
    
    df = pd.DataFrame({
        "Pos": range(1, n_equipos + 1),
        "Equipo": equipos,
        "PJ": [34 if "Alemania" in liga or "Francia" in liga else 38 for _ in range(n_equipos)],
        "Pts": puntos,
        "DG": np.sort(np.round(np.random.normal(12, 10, n_equipos)).astype(int))[::-1]
    })
    
    # --- CÁLCULO MATEMÁTICO DEL RANGO (Faltan 3 fechas = 9 Pts) ---
    pts_en_juego = 9
    rango_min = []
    rango_max = []
    estados = []
    
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
                
        rango_min.append(max_pos)
        rango_max.append(min_pos)
        
        # Asignar estados de torneo para la etiqueta visual
        if pos_actual == 1:
            estados.append("🏆 Campeón")
        elif "Inglaterra" in liga or "España" in liga or "Italia" in liga:
            if pos_actual in [2, 3, 4]: estados.append("🇪🇺 Champions League")
            elif pos_actual == 5: estados.append("🇪🇺 Europa League")
            elif pos_actual == 6: estados.append("🇪🇺 Conference League")
            elif pos_actual >= (n_equipos - 2): estados.append("🔻 Zona Descenso")
            else: estados.append("⚪ Mitad de Tabla")
        elif "Alemania" in liga:
            if pos_actual in [2, 3, 4]: estados.append("🇪🇺 Champions League")
            elif pos_actual == 5: estados.append("🇪🇺 Europa League")
            elif pos_actual == 6: estados.append("🇪🇺 Conference League")
            elif pos_actual >= (n_equipos - 1): estados.append("🔻 Zona Descenso")
            else: estados.append("⚪ Mitad de Tabla")
        elif "Francia" in liga:
            if pos_actual in [2, 3]: estados.append("🇪🇺 Champions League")
            elif pos_actual == 4: estados.append("🇪🇺 Europa League")
            elif pos_actual == 5: estados.append("🇪🇺 Conference League")
            elif pos_actual >= (n_equipos - 2): estados.append("🔻 Zona Descenso")
            else: estados.append("⚪ Mitad de Tabla")
        elif "Brasil" in liga:
            if pos_actual in range(2, 7): estados.append("🌎 Copa Libertadores")
            elif pos_actual in range(7, 13): estados.append("🌎 Copa Sudamericana")
            elif pos_actual >= (n_equipos - 3): estados.append("🔻 Zona Descenso")
            else: estados.append("⚪ Mitad de Tabla")
        elif "Argentina" in liga:
            if pos_actual in range(2, 5): estados.append("🌎 Copa Libertadores")
            elif pos_actual in range(5, 10): estados.append("🌎 Copa Sudamericana")
            elif pos_actual == n_equipos: estados.append("🔻 Zona Descenso")
            else: estados.append("⚪ Mitad de Tabla")
        elif "Arabia" in liga:
            if pos_actual in [2, 3]: estados.append("🌏 AFC Champions League")
            elif pos_actual >= (n_equipos - 2): estados.append("🔻 Zona Descenso")
            else: estados.append("⚪ Mitad de Tabla")
        else: # México
            if pos_actual in range(2, 7): estados.append("🇲🇽 Liguilla Directa")
            elif pos_actual in range(7, 11): estados.append("🎟️ Zona Play-In")
            else: estados.append("⚪ Eliminado")

    df["Estado del Torneo"] = estados
    df["Rango Matemático"] = [f"{mi}° al {ma}°" for mi, ma in zip(rango_min, rango_max)]
    return df

# --- 2. DISEÑO DE LAS PESTAÑAS ---
tab1, tab2 = st.tabs(["📊 Tablas Interactivas y Margen Matemático", "📈 Estadísticas Avanzadas"])

with tab1:
    liga_seleccionada = st.selectbox(
        "🏆 Selecciona una Competición:",
        ["Premier League (Inglaterra)", "LaLiga (España)", "Serie A (Italia)", "Bundesliga (Alemania)", 
         "Ligue 1 (Francia)", "Brasileirão (Brasil)", "Liga Profesional (Argentina)", 
         "Saudi Pro League (Arabia Saudita)", "Liga MX (México)"]
    )
    
    df_liga = cargar_datos_liga(liga_seleccionada)
    
    st.markdown("💡 *Nota: El sistema calcula dinámicamente el **Rango Matemático** (peor y mejor escenario) basándose en los puntos restantes.*")
    
    # Renderizado optimizado con st.dataframe nativo y avanzado
    st.dataframe(
        df_liga,
        column_config={
            "Pos": st.column_config.NumberColumn("Posición", help="Puesto actual en la tabla", format="%d"),
            "Equipo": st.column_config.TextColumn("Equipo", help="Nombre del Club deportivo"),
            "PJ": st.column_config.NumberColumn("PJ", help="Partidos Jugados"),
            "Pts": st.column_config.NumberColumn("Pts", help="Puntos Totales"),
            "DG": st.column_config.NumberColumn("DG", help="Diferencia de Goles"),
            "Estado del Torneo": st.column_config.SelectColumn(
                "Estado y Clasificación",
                help="Situación de clasificación internacional o descenso",
                width="medium"
            ),
            "Rango Matemático": st.column_config.TextColumn(
                "Rango Matemático Potencial",
                help="Rango de posiciones al que puede ascender o descender matemáticamente"
            )
        },
        hide_index=True,
        use_container_width=True,
        height=650
    )

with tab2:
    st.subheader("📈 Rendimiento y Métricas del Torneo")
    st.info("Pestaña de analítica en desarrollo. Aquí se integrarán gráficos de dispersión de ataque/defensa y evolución de jornadas.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Puntaje Máximo Registrado", value=f"{df_liga['Pts'].max()} Pts", delta="Puntero")
    with c2:
        st.metric(label="Promedio Diferencia de Goles", value=f"{round(df_liga['DG'].mean(), 1)}", delta="Competitividad")
    with c3:
        st.metric(label="Puntos Críticos de Salvación", value=f"{df_liga['Pts'].iloc[-4]} Pts", delta="Margen del Descenso")
