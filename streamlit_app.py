import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador Bio-LNG · Naturgy Jalisco",
    page_icon="🟢",
    layout="wide",
)

# ─── ESTILO ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #0A1420; }
    section[data-testid="stSidebar"] { background: #0F1D2D; }
    h1, h2, h3, h4 { color: #FFFFFF !important; font-family: Arial, sans-serif; }
    p, label, span, div { color: #C5D6E8; font-family: Arial, sans-serif; }
    .metric-card {
        background: #0F1D2D; border: 1px solid #1E3349; border-radius: 8px;
        padding: 16px 18px; margin-bottom: 8px;
    }
    .metric-label { font-size: 11px; color: #5A7B98; letter-spacing: 1px;
        text-transform: uppercase; font-family: monospace; }
    .metric-value { font-size: 30px; font-weight: 800; letter-spacing: -0.5px;
        font-family: monospace; line-height: 1.1; }
    .metric-unit { font-size: 12px; color: #5A7B98; }
    .badge-ok { background: #0D2818; border: 1px solid #1A8F4E; color: #2BD576;
        border-radius: 6px; padding: 10px; text-align: center; font-weight: 700;
        font-family: monospace; }
    .badge-no { background: #2A1015; border: 1px solid #E8506B; color: #E8506B;
        border-radius: 6px; padding: 10px; text-align: center; font-weight: 700;
        font-family: monospace; }
    .tag { font-size: 10px; font-weight: 700; letter-spacing: 3px; color: #2BD576;
        font-family: monospace; text-transform: uppercase; }
    .stSlider [data-baseweb="slider"] { padding-top: 8px; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

VERDE = "#2BD576"
AZUL = "#3DA5E8"
AMBAR = "#F5A623"
ROJO = "#E8506B"

# ─────────────────────────────────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="tag">● Sistema Operativo · Simulación en Tiempo Real</div>', unsafe_allow_html=True)
    st.markdown("## Simulador de Cadena de Valor Bio-LNG")
    st.markdown('<p style="color:#5A7B98; margin-top:-8px;">Lagos de Moreno, Jalisco · Naturgy México · Ref. Brimex Energy 2024</p>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="text-align:right; padding-top:20px;"><span class="tag">NATURGY MÉXICO</span><br><span style="color:#1A8F4E; font-family:monospace; font-size:11px;">DS3001B · TEC DE MONTERREY</span></div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# CONTROLES (SIDEBAR)
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown('<div class="tag">Parámetros de Operación</div>', unsafe_allow_html=True)
st.sidebar.markdown("### Ajusta los escenarios")

biomasa = st.sidebar.slider("Biomasa de entrada (t/día)", 200, 1600, 800, 50,
    help="Referente Brimex: 800 t/día")

st.sidebar.markdown("---")
st.sidebar.markdown("**Ruta del producto**")
ruta = st.sidebar.radio("", ["Bio-LNG (transporte en camión)", "Red Naturgy (inyección local)"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("**Mercado y precios**")
precio_lng = st.sidebar.slider("Precio Bio-LNG (USD/GJ)", 15.0, 45.0, 30.0, 0.5,
    help="Rango literatura: 21–40.5 USD/GJ (Gildea et al., 2025)")
feed_in = st.sidebar.slider("Feed-in tariff red (USD/GJ)", 0.0, 12.0, 0.0, 0.5,
    help="Francia: hasta ~11 USD/GJ. México: 0 actualmente")
precio_carbono = st.sidebar.slider("Crédito de carbono (USD/ton CO₂eq)", 0, 25, 0, 1,
    help="Mercado voluntario: 5–25 USD/ton")

st.sidebar.markdown("---")
st.sidebar.markdown("**Sustitución de diésel**")
clientes_diesel = st.sidebar.slider("Flotas/industrias cercanas (clientes)", 0, 20, 8, 1,
    help="Empresas que sustituyen diésel por Bio-LNG en la zona")

# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULOS
# ─────────────────────────────────────────────────────────────────────────────
factor = biomasa / 800.0

# Producción física
biogas = biomasa * 0.9
biometano_m3d = biomasa * 27.0          # 21,600 m³/d @ 800 t/d
digestato = biomasa * 0.1
co2_liq = biomasa * 16.5                 # L/día
biolng_m3d = biometano_m3d * 0.33

# Energía
GJ_por_m3_biometano = 0.0373
gj_anual = biometano_m3d * 365 * GJ_por_m3_biometano

# Economía Bio-LNG
costo_lng = 22.0
ingreso_carbono = co2_evitado_ton = factor * 18500
ingreso_carbono_musd = (co2_evitado_ton * precio_carbono) / 1_000_000
ganancia_lng = (precio_lng - costo_lng) * gj_anual * 0.33 / 1_000_000 + ingreso_carbono_musd
ganancia_lng_M = ganancia_lng * 1000  # a millones MXN aprox para impacto visual (mantener USD)
ganancia_lng_real = (precio_lng - costo_lng) * gj_anual * 0.33 / 1_000_000

# Economía Red
costo_bm = 15.0
precio_red = 3.34 + feed_in
ganancia_red = (precio_red - costo_bm) * gj_anual / 1_000_000 + ingreso_carbono_musd

# Sustitución diésel
# 1 m³ Bio-LNG ≈ 0.6 L diésel equivalente energético (simplificado)
diesel_sustituido_anual = biolng_m3d * 365 * 0.58 * (clientes_diesel / 8.0)  # litros/año
co2_diesel_evitado = diesel_sustituido_anual * 2.68 / 1000  # ton CO2

es_biolng = ruta.startswith("Bio-LNG")
ganancia_actual = ganancia_lng_real if es_biolng else ganancia_red
viable = ganancia_actual >= 0

# ─────────────────────────────────────────────────────────────────────────────
# FILA DE MÉTRICAS PRINCIPALES
# ─────────────────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

def metric(col, label, value, unit, color):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color};">{value}<span class="metric-unit"> {unit}</span></div>
    </div>
    """, unsafe_allow_html=True)

signo = "+" if ganancia_actual >= 0 else ""
metric(m1, "Ganancia anual estimada", f"{signo}{ganancia_actual:,.0f}", "M USD/año", VERDE if ganancia_actual >= 0 else ROJO)
metric(m2, "Biometano producido", f"{biometano_m3d:,.0f}", "m³/día", VERDE)
metric(m3, "Bio-LNG generado", f"{biolng_m3d:,.0f}", "m³/día", AZUL)
metric(m4, "CO₂ evitado", f"{co2_evitado_ton:,.0f}", "ton/año", AMBAR)

# ─────────────────────────────────────────────────────────────────────────────
# CUERPO: GRÁFICAS + MAPA
# ─────────────────────────────────────────────────────────────────────────────
left, right = st.columns([1.3, 1])

with left:
    st.markdown('<div class="tag">Producción vs Escala de Biomasa</div>', unsafe_allow_html=True)

    # Curva: cómo crece la producción y ganancia con la biomasa
    xs = np.arange(200, 1601, 50)
    prod = xs * 27 * 365 * GJ_por_m3_biometano * 0.33 / 1000  # GJ Bio-LNG (miles)
    gan_lng = (precio_lng - costo_lng) * (xs * 27 * 365 * GJ_por_m3_biometano * 0.33) / 1_000_000
    gan_red = (precio_red - costo_bm) * (xs * 27 * 365 * GJ_por_m3_biometano) / 1_000_000

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=gan_lng, name="Ganancia Bio-LNG",
        line=dict(color=VERDE, width=3), fill='tozeroy', fillcolor='rgba(43,213,118,0.1)'))
    fig.add_trace(go.Scatter(x=xs, y=gan_red, name="Ganancia Red (con feed-in)",
        line=dict(color=AZUL, width=2, dash='dot')))
    fig.add_hline(y=0, line_color="#5A7B98", line_width=1)
    fig.add_vline(x=biomasa, line_color=AMBAR, line_width=2, line_dash="dash",
        annotation_text=f"  {biomasa} t/d", annotation_font_color=AMBAR)
    fig.update_layout(
        plot_bgcolor="#0F1D2D", paper_bgcolor="#0F1D2D",
        font=dict(color="#C5D6E8", family="Arial"),
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.1),
        xaxis=dict(title="Biomasa (t/día)", gridcolor="#1E3349", zeroline=False),
        yaxis=dict(title="Ganancia (M USD/año)", gridcolor="#1E3349", zeroline=False),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Sustitución de diésel
    st.markdown('<div class="tag">Sustitución de Diésel en Clientes Cercanos</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    d1.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Diésel sustituido</div>
        <div class="metric-value" style="color:{AMBAR}; font-size:24px;">{diesel_sustituido_anual/1000:,.0f}<span class="metric-unit"> mil L/año</span></div>
    </div>""", unsafe_allow_html=True)
    d2.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">CO₂ evitado por sustitución</div>
        <div class="metric-value" style="color:{VERDE}; font-size:24px;">{co2_diesel_evitado:,.0f}<span class="metric-unit"> ton/año</span></div>
    </div>""", unsafe_allow_html=True)

with right:
    st.markdown('<div class="tag">Corredor de Distribución · Jalisco</div>', unsafe_allow_html=True)

    # Datos del mapa
    planta = {"lat": 21.3571, "lon": -101.9282, "name": "Planta Bio-LNG"}
    ciudades = pd.DataFrame([
        {"name": "Lagos de Moreno", "lat": 21.3571, "lon": -101.9282, "tipo": "Planta"},
        {"name": "León", "lat": 21.1250, "lon": -101.6860, "tipo": "Cliente"},
        {"name": "Aguascalientes", "lat": 21.8853, "lon": -102.2916, "tipo": "Cliente"},
        {"name": "Guadalajara", "lat": 20.6597, "lon": -103.3496, "tipo": "Cliente"},
    ])

    # Líneas de ruta
    rutas = pd.DataFrame([
        {"from_lat": 21.3571, "from_lon": -101.9282, "to_lat": 21.1250, "to_lon": -101.6860},
        {"from_lat": 21.1250, "from_lon": -101.6860, "to_lat": 21.8853, "to_lon": -102.2916},
        {"from_lat": 21.8853, "from_lon": -102.2916, "to_lat": 20.6597, "to_lon": -103.3496},
    ])

    layer_lines = pdk.Layer(
        "LineLayer", rutas,
        get_source_position=["from_lon", "from_lat"],
        get_target_position=["to_lon", "to_lat"],
        get_color=[43, 213, 118, 180], get_width=3,
    )
    layer_points = pdk.Layer(
        "ScatterplotLayer", ciudades,
        get_position=["lon", "lat"],
        get_color=[43, 213, 118, 200], get_radius=8000,
        pickable=True,
    )
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=pdk.ViewState(latitude=21.2, longitude=-102.3, zoom=7, pitch=40),
        layers=[layer_lines, layer_points],
        tooltip={"text": "{name}"},
    ), use_container_width=True)

    # Badge de viabilidad
    if viable:
        st.markdown(f'<div class="badge-ok">✓ VIABLE EN ESTE ESCENARIO · {signo}{ganancia_actual:,.0f} M USD/año</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge-no">✗ NO VIABLE · ajusta precio o feed-in tariff</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-card" style="margin-top:10px;">
        <div class="metric-label">Ruta seleccionada</div>
        <div style="color:#fff; font-weight:700; margin-top:4px;">{ruta}</div>
        <div style="color:#5A7B98; font-size:12px; margin-top:6px;">
            {"El Bio-LNG viaja en camión hasta 250 km — sustituye diésel en flotas e industria." if es_biolng else "El biometano se inyecta a la red local de Naturgy en zona Bajío Sur."}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PIE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p style="font-size:11px; color:#4A6178; font-family:monospace; text-align:center;">Modelo basado en referente operativo Brimex Energy (800 t/d, 21,600 m³/d) · IEA 2025 · EIA 2025 · Gildea et al. 2025 · Capra et al. 2019 · SIAP 2023 · Ajusta los controles de la izquierda para simular escenarios en vivo.</p>', unsafe_allow_html=True)
