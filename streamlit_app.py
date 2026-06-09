import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk

st.set_page_config(
    page_title="Simulador Bio-LNG · Naturgy Jalisco",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700;800&display=swap');

    .stApp { 
        background: #FFFFFF; 
    }

    * { 
        font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif !important; 
    }

    h1, h2 { 
        font-family: 'Source Sans 3', Georgia, serif !important; 
        letter-spacing: -0.5px !important; 
    }

    section[data-testid="stSidebar"] {
        background: #8A3F00;
        border-right: none;
        min-width: 330px;
    }

    section[data-testid="stSidebar"] * { 
        color: #FFF3E6 !important; 
    }

    section[data-testid="stSidebar"] h3 { 
        color: #FFFFFF !important; 
    }

    section[data-testid="stSidebar"] .eyebrow-side {
        color: #FFB86B !important;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: none;
    }

    section[data-testid="stSidebar"] hr { 
        border-color: #B85C12; 
    }

    [data-testid="collapsedControl"] {
        display: block !important;
        background: #8A3F00 !important;
        color: #FFFFFF !important;
        border-radius: 0 8px 8px 0;
    }

    [data-testid="collapsedControl"] svg { 
        color: #FFFFFF !important; 
    }

    h1, h2, h3, h4 { 
        color: #15241D !important; 
    }

    p, label, span, div { 
        color: #44525E; 
    }

    .eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.6px;
        color: #C96A13;
        text-transform: none;
    }

    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8E5;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .kpi-label {
        font-size: 12px;
        color: #7E8C86;
        letter-spacing: 0.1px;
        text-transform: none;
        font-weight: 600;
    }

    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1.1;
        margin-top: 4px;
    }

    .kpi-unit {
        font-size: 13px;
        color: #7E8C86;
        font-weight: 500;
    }

    .badge-ok {
        background: #FFF1E2;
        border: 1px solid #F28C28;
        color: #8A3F00;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 14px;
    }

    .badge-no {
        background: #FBECEF;
        border: 1px solid #C0264A;
        color: #A01E3C;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 14px;
    }

    .section-title {
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0px;
        color: #15241D;
        text-transform: none;
        margin-bottom: 8px;
    }

    .footer-note {
        font-size: 11px;
        color: #A3B1BC;
        text-align: center;
    }

    hr { 
        border-color: #E2E8E5; 
    }

    #MainMenu, footer, header { 
        visibility: hidden; 
    }

    [data-testid="collapsedControl"] {
        display: block !important;
        background: #8A3F00 !important;
        border-radius: 0 8px 8px 0;
        padding: 8px 6px !important;
    }

    [data-testid="collapsedControl"] span,
    [data-testid="collapsedControl"] p {
        font-size: 0 !important;
    }

    [data-testid="collapsedControl"]::after {
        content: "›";
        color: #FFFFFF;
        font-size: 24px;
        font-weight: 700;
    }

    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] p {
        font-size: 0 !important;
    }

    [data-testid="stSidebarCollapseButton"]::after {
        content: "‹";
        color: #FFF3E6;
        font-size: 22px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

NARANJA = "#F28C28"
NARANJA_OSC = "#C96A13"
AZUL = "#2E7DB8"
AMBAR = "#C98A2B"
ROJO = "#C0264A"
GRIS = "#7E8C86"

c1, c2 = st.columns([3, 1])

with c1:
    st.markdown(
        '<div class="eyebrow">Naturgy México · Simulación de escenarios</div>',
        unsafe_allow_html=True,
    )
    st.markdown("## Cadena de valor del Bio-LNG")
    st.markdown(
        '<p style="color:#7E8C86; margin-top:-10px;">'
        'Lagos de Moreno, Región Altos Norte de Jalisco · Referente operativo: Brimex Energy'
        '</p>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        '<div style="text-align:right; padding-top:18px;">'
        '<div class="eyebrow">DS3001B</div>'
        '<span style="color:#7E8C86; font-size:12px;">Tecnológico de Monterrey · 2026</span>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="eyebrow-side">Parámetros de operación</div>',
    unsafe_allow_html=True,
)

st.sidebar.markdown("### Ajusta los escenarios")

st.sidebar.markdown(
    '<p style="color:#FFE0BF; font-size:12px; margin-top:-8px;">'
    'Modifica los valores para simular distintos escenarios en tiempo real.'
    '</p>',
    unsafe_allow_html=True,
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

biomasa = st.sidebar.slider(
    "Biomasa de entrada (t/día)",
    200,
    1600,
    800,
    50,
    help="Referente Brimex: 800 t/día",
)

st.sidebar.markdown("**Ruta del producto**")

ruta = st.sidebar.radio(
    "ruta",
    ["Bio-LNG (transporte en camión)", "Red Naturgy (inyección local)"],
    label_visibility="collapsed",
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("**Mercado y precios**")

precio_lng = st.sidebar.slider(
    "Precio Bio-LNG (USD/GJ)",
    15.0,
    45.0,
    30.0,
    0.5,
    help="Rango: 21–40.5 USD/GJ",
)

feed_in = st.sidebar.slider(
    "Tarifa feed-in de red (USD/GJ)",
    0.0,
    12.0,
    0.0,
    0.5,
    help="Francia: hasta ~11. México: 0",
)

precio_carbono = st.sidebar.slider(
    "Crédito de carbono (USD/ton CO₂eq)",
    0,
    25,
    0,
    1,
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("**Sustitución de diésel**")

clientes_diesel = st.sidebar.slider(
    "Clientes cercanos que sustituyen diésel",
    0,
    20,
    8,
    1,
)

factor = biomasa / 800.0
biometano_m3d = biomasa * 27.0
digestato = biomasa * 0.1
biolng_m3d = biometano_m3d * 0.33

GJ_m3 = 0.0373
gj_anual = biometano_m3d * 365 * GJ_m3
co2_evitado_ton = factor * 18500
ingreso_carbono = (co2_evitado_ton * precio_carbono) / 1_000_000

costo_lng = 22.0
ganancia_lng = (precio_lng - costo_lng) * gj_anual * 0.33 / 1_000_000 + ingreso_carbono

costo_bm = 15.0
precio_red = 3.34 + feed_in
ganancia_red = (precio_red - costo_bm) * gj_anual / 1_000_000 + ingreso_carbono

diesel_sustituido = biolng_m3d * 365 * 0.58 * (clientes_diesel / 8.0)
co2_diesel = diesel_sustituido * 2.68 / 1000

es_biolng = ruta.startswith("Bio-LNG")
ganancia_actual = ganancia_lng if es_biolng else ganancia_red
viable = ganancia_actual >= 0
signo = "+" if ganancia_actual >= 0 else ""

def kpi(col, label, value, unit, color):
    col.markdown(
        f"""
        <div class="card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{color};">
                {value} <span class="kpi-unit">{unit}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

m1, m2, m3, m4 = st.columns(4)

kpi(
    m1,
    "Ganancia anual estimada",
    f"{signo}{ganancia_actual:,.1f}",
    "M USD/año",
    NARANJA if viable else ROJO,
)

kpi(
    m2,
    "Biometano producido",
    f"{biometano_m3d:,.0f}",
    "m³/día",
    NARANJA_OSC,
)

kpi(
    m3,
    "Bio-LNG generado",
    f"{biolng_m3d:,.0f}",
    "m³/día",
    AZUL,
)

kpi(
    m4,
    "CO₂ evitado",
    f"{co2_evitado_ton:,.0f}",
    "ton/año",
    AMBAR,
)

left, right = st.columns([1.3, 1])

with left:
    st.markdown(
        '<div class="section-title">Producción y ganancia según escala de biomasa</div>',
        unsafe_allow_html=True,
    )

    xs = np.arange(200, 1601, 50)

    gan_lng_x = (precio_lng - costo_lng) * (xs * 27 * 365 * GJ_m3 * 0.33) / 1_000_000
    gan_red_x = (precio_red - costo_bm) * (xs * 27 * 365 * GJ_m3) / 1_000_000

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=gan_lng_x,
            name="Bio-LNG",
            line=dict(color=NARANJA, width=3),
            fill="tozeroy",
            fillcolor="rgba(242,140,40,0.10)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=gan_red_x,
            name="Red Naturgy (con feed-in)",
            line=dict(color=AZUL, width=2, dash="dot"),
        )
    )

    fig.add_hline(
        y=0,
        line_color="#C5CFD6",
        line_width=1,
    )

    fig.add_vline(
        x=biomasa,
        line_color=AMBAR,
        line_width=2,
        line_dash="dash",
        annotation_text=f"  {biomasa} t/d",
        annotation_font_color=AMBAR,
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#44525E", family="Source Sans 3"),
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12),
        xaxis=dict(
            title="Biomasa (t/día)",
            gridcolor="#EDF1F4",
            zeroline=False,
        ),
        yaxis=dict(
            title="Ganancia (M USD/año)",
            gridcolor="#EDF1F4",
            zeroline=False,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="section-title">Sustitución de diésel en clientes cercanos</div>',
        unsafe_allow_html=True,
    )

    d1, d2 = st.columns(2)

    kpi(
        d1,
        "Diésel sustituido",
        f"{diesel_sustituido/1000:,.0f}",
        "mil L/año",
        AMBAR,
    )

    kpi(
        d2,
        "CO₂ evitado por sustitución",
        f"{co2_diesel:,.0f}",
        "ton/año",
        NARANJA,
    )

with right:
    st.markdown(
        '<div class="section-title">Corredor de distribución · Jalisco</div>',
        unsafe_allow_html=True,
    )

    ciudades = pd.DataFrame([
        {
            "name": "Lagos de Moreno",
            "lat": 21.3571,
            "lon": -101.9282,
        },
        {
            "name": "León",
            "lat": 21.1250,
            "lon": -101.6860,
        },
        {
            "name": "Aguascalientes",
            "lat": 21.8853,
            "lon": -102.2916,
        },
        {
            "name": "Guadalajara",
            "lat": 20.6597,
            "lon": -103.3496,
        },
    ])

    rutas = pd.DataFrame([
        {
            "fl": 21.3571,
            "fo": -101.9282,
            "tl": 21.1250,
            "to": -101.6860,
        },
        {
            "fl": 21.1250,
            "fo": -101.6860,
            "tl": 21.8853,
            "to": -102.2916,
        },
        {
            "fl": 21.8853,
            "fo": -102.2916,
            "tl": 20.6597,
            "to": -103.3496,
        },
    ])

    layer_lines = pdk.Layer(
        "LineLayer",
        rutas,
        get_source_position=["fo", "fl"],
        get_target_position=["to", "tl"],
        get_color=[242, 140, 40, 200],
        get_width=4,
    )

    layer_points = pdk.Layer(
        "ScatterplotLayer",
        ciudades,
        get_position=["lon", "lat"],
        get_color=[201, 106, 19, 220],
        get_radius=9000,
        pickable=True,
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style="road",
            initial_view_state=pdk.ViewState(
                latitude=21.2,
                longitude=-102.3,
                zoom=7,
                pitch=35,
            ),
            layers=[layer_lines, layer_points],
            tooltip={"text": "{name}"},
        ),
        use_container_width=True,
    )

    if viable:
        st.markdown(
            f'<div class="badge-ok">Viable en este escenario · {signo}{ganancia_actual:,.1f} M USD/año</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="badge-no">No viable en este escenario · ajusta precio o feed-in tariff</div>',
            unsafe_allow_html=True,
        )

    texto_ruta = (
        "El Bio-LNG viaja en camión hasta 250 km y sustituye diésel en flotas e industria cercanas."
        if es_biolng
        else "El biometano se inyecta a la red local de Naturgy en zona Bajío Sur."
    )

    st.markdown(
        f"""
        <div class="card" style="margin-top:10px;">
            <div class="kpi-label">Ruta seleccionada</div>
            <div style="color:#15241D; font-weight:700; margin-top:4px; font-size:15px;">
                {ruta}
            </div>
            <div style="color:#7E8C86; font-size:12px; margin-top:6px; line-height:1.5;">
                {texto_ruta}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown(
    '<p class="footer-note">'
    'Modelo basado en referente operativo Brimex Energy (800 t/d, 21,600 m³/d) · '
    'IEA 2025 · EIA 2025 · Gildea et al. 2025 · Capra et al. 2019 · SIAP 2023.'
    '</p>',
    unsafe_allow_html=True,
)
