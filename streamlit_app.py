import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk

# ==========================================================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================================================
st.set_page_config(
    page_title="Simulador Bio-LNG | Naturgy México",
    page_icon="naturgy_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================
# CONSTANTES DEL MODELO  (verificar contra el reporte antes de presentar)
# ==========================================================================
# Referencia operativa: planta Brimex Energy
BIOMASA_REF = 800.0          # t/día de biomasa (referencia Brimex)
BIOMETANO_REF = 21600.0      # m³/día de biometano (referencia Brimex)
RENDIMIENTO = BIOMETANO_REF / BIOMASA_REF   # m³ biometano por t de biomasa = 27

ENERGIA_BIOMETANO = 0.0373   # GJ por m³ de biometano (~96% CH4, PCI)
ENERGIA_LNG = 52.0           # GJ por tonelada de Bio-LNG (PCI ~50 MJ/kg)

# Costos (USD/GJ)
COSTO_PRODUCCION = 3.34      # costo de producción del biometano (cifra del estudio)
COSTO_LICUEFACCION = 2.50    # costo adicional de licuefacción por GJ
COSTO_TRANSPORTE = 1.20      # costo de transporte criogénico por GJ

# Ambiental
CO2_CAPTURADO = 18500.0      # t CO2/año (estimación escalada de Brimex)
FACTOR_DIESEL = 2.68         # kg CO2 por litro de diésel sustituido
DIESEL_POR_CLIENTE = 500000.0  # litros/año de diésel desplazado por cliente

DIAS_ANIO = 365

# ==========================================================================
# ESTILOS
# ==========================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');

    html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, div {
        font-family: 'Source Sans 3', sans-serif !important;
    }

    /* Fondo blanco del cuerpo */
    .stApp {
        background-color: #FFFFFF;
        color: #1A1A1A;
    }

    /* Sidebar verde Naturgy */
    [data-testid="stSidebar"] {
        background-color: #0E3A2A;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* Encabezados */
    h1, h2, h3 {
        color: #0E3A2A;
        font-weight: 700;
    }

    /* Arregla el botón de colapsar sidebar (oculta el texto 'keyboard_double') */
    [data-testid="collapsedControl"] {
        color: transparent !important;
    }
    [data-testid="collapsedControl"]::after {
        content: "›";
        color: #0E3A2A;
        font-size: 26px;
        font-weight: 700;
    }
    [data-testid="stSidebarCollapseButton"] {
        color: transparent !important;
    }
    [data-testid="stSidebarCollapseButton"]::after {
        content: "‹";
        color: #FFFFFF;
        font-size: 26px;
        font-weight: 700;
    }

    /* Badge de viabilidad */
    .badge {
        display: inline-block;
        padding: 10px 22px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 18px;
        margin-top: 6px;
    }
    .badge-ok { background-color: #1B7A4B; color: #FFFFFF; }
    .badge-no { background-color: #B23A48; color: #FFFFFF; }

    /* Tarjetas de métricas */
    [data-testid="stMetric"] {
        background-color: #F4F7F5;
        border: 1px solid #E0E6E2;
        border-radius: 8px;
        padding: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================================
# SIDEBAR — PARÁMETROS
# ==========================================================================
with st.sidebar:
    st.image("naturgy_logo.png", width=160)
    st.markdown("## Parámetros de la planta")

    biomasa = st.slider(
        "Entrada de biomasa (t/día)",
        min_value=200, max_value=1600, value=800, step=50,
        help="Referencia Brimex Energy: 800 t/día",
    )

    st.markdown("---")
    ruta = st.radio(
        "Ruta de valorización",
        options=["Bio-LNG (licuefacción)", "Red Naturgy (biometano gaseoso)"],
        index=0,
    )
    es_biolng = ruta.startswith("Bio-LNG")

    st.markdown("---")
    if es_biolng:
        precio_lng = st.slider(
            "Precio Bio-LNG (USD/ton)",
            min_value=400, max_value=1200, value=700, step=25,
        )
    else:
        tarifa = st.slider(
            "Tarifa de inyección a red (USD/GJ)",
            min_value=3.0, max_value=20.0, value=8.0, step=0.5,
            help="Umbral de viabilidad reportado: 10–20 USD/GJ",
        )

    st.markdown("---")
    st.markdown("### Beneficios adicionales")
    precio_carbono = st.slider(
        "Precio de bonos de carbono (USD/t CO₂)",
        min_value=0, max_value=120, value=30, step=5,
    )
    clientes_diesel = st.slider(
        "Clientes cercanos que sustituyen diésel",
        min_value=0, max_value=20, value=3, step=1,
    )

# ==========================================================================
# CÁLCULOS
# ==========================================================================
def calcular_ganancia(biomasa_t, es_lng, precio_o_tarifa, precio_co2, n_clientes):
    biometano_dia = biomasa_t * RENDIMIENTO          # m³/día
    energia_dia = biometano_dia * ENERGIA_BIOMETANO  # GJ/día
    energia_anio = energia_dia * DIAS_ANIO           # GJ/año

    if es_lng:
        lng_anio = energia_anio / ENERGIA_LNG        # toneladas/año
        ingreso = lng_anio * precio_o_tarifa
        costo = energia_anio * (COSTO_PRODUCCION + COSTO_LICUEFACCION + COSTO_TRANSPORTE)
    else:
        ingreso = energia_anio * precio_o_tarifa
        costo = energia_anio * COSTO_PRODUCCION

    # Beneficios ambientales
    ingreso_carbono = CO2_CAPTURADO * precio_co2
    co2_diesel = n_clientes * DIESEL_POR_CLIENTE * FACTOR_DIESEL / 1000.0  # t CO2/año
    ingreso_diesel = co2_diesel * precio_co2

    ganancia = ingreso + ingreso_carbono + ingreso_diesel - costo
    return {
        "biometano_dia": biometano_dia,
        "energia_anio": energia_anio,
        "ingreso": ingreso,
        "costo": costo,
        "ingreso_carbono": ingreso_carbono,
        "ingreso_diesel": ingreso_diesel,
        "co2_diesel": co2_diesel,
        "ganancia": ganancia,
    }


valor = precio_lng if es_biolng else tarifa
res = calcular_ganancia(biomasa, es_biolng, valor, precio_carbono, clientes_diesel)

# ==========================================================================
# CUERPO PRINCIPAL
# ==========================================================================
st.title("Simulador de la cadena de valor Bio-LNG")
st.markdown(
    "Modelo de coinversión para **Naturgy México** — Lagos de Moreno, Jalisco. "
    "Referencia operativa: planta Brimex Energy (800 t/día → 21,600 m³/día de biometano)."
)

# --- Cadena de valor con imágenes dinámicas ---
st.markdown("### Cadena de valor")

if es_biolng:
    pasos = [
        ("biomasa_img.png", "Biomasa"),
        ("biodigestor.png", "Biodigestión"),
        ("Upgrading.png", "Upgrading"),
        ("Licuefacción.png", "Licuefacción"),
        ("Transporte.png", "Transporte"),
    ]
else:
    # Ruta gaseosa: sin licuefacción
    pasos = [
        ("biomasa_img.png", "Biomasa"),
        ("biodigestor.png", "Biodigestión"),
        ("Upgrading.png", "Upgrading"),
        ("Transporte.png", "Inyección a red"),
    ]

cols = st.columns(len(pasos))
for col, (img, titulo) in zip(cols, pasos):
    with col:
        st.image(img, use_container_width=True)
        st.markdown(f"<p style='text-align:center;font-weight:600'>{titulo}</p>",
                    unsafe_allow_html=True)

st.markdown("---")

# --- Resultados económicos ---
st.markdown("### Resultados (anuales)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Biometano", f"{res['biometano_dia']:,.0f} m³/día")
c2.metric("Energía", f"{res['energia_anio']/1000:,.0f} mil GJ/año")
c3.metric("Ingresos", f"{(res['ingreso']+res['ingreso_carbono']+res['ingreso_diesel'])/1e6:,.1f} M USD")
c4.metric("Costos", f"{res['costo']/1e6:,.1f} M USD")

# --- Badge de viabilidad ---
ganancia_musd = res["ganancia"] / 1e6
if res["ganancia"] > 0:
    badge = f"<span class='badge badge-ok'>VIABLE · +{ganancia_musd:,.1f} M USD/año</span>"
else:
    badge = f"<span class='badge badge-no'>NO VIABLE · {ganancia_musd:,.1f} M USD/año</span>"
st.markdown(badge, unsafe_allow_html=True)

st.caption(
    f"Incluye bonos de carbono ({res['ingreso_carbono']/1e6:,.2f} M USD) y "
    f"sustitución de diésel ({res['ingreso_diesel']/1e6:,.2f} M USD, "
    f"{res['co2_diesel']:,.0f} t CO₂/año desplazadas). "
    "Las cifras de CO₂ son estimaciones de orden de magnitud."
)

st.markdown("---")

# ==========================================================================
# GRÁFICA: GANANCIA VS ESCALA
# ==========================================================================
st.markdown("### Ganancia según escala de planta")

escalas = list(range(200, 1601, 100))
g_lng, g_red = [], []
for b in escalas:
    g_lng.append(
        calcular_ganancia(b, True, precio_lng if es_biolng else 700,
                           precio_carbono, clientes_diesel)["ganancia"] / 1e6
    )
    g_red.append(
        calcular_ganancia(b, False, tarifa if not es_biolng else 8.0,
                           precio_carbono, clientes_diesel)["ganancia"] / 1e6
    )

fig = go.Figure()
fig.add_trace(go.Scatter(x=escalas, y=g_lng, mode="lines+markers",
                         name="Ruta Bio-LNG", line=dict(color="#1B7A4B", width=3)))
fig.add_trace(go.Scatter(x=escalas, y=g_red, mode="lines+markers",
                         name="Ruta red Naturgy", line=dict(color="#B23A48", width=3)))
fig.add_hline(y=0, line_dash="dash", line_color="#666666")
fig.add_vline(x=biomasa, line_dash="dot", line_color="#0E3A2A",
              annotation_text="Escala actual")
fig.update_layout(
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
    font=dict(family="Source Sans 3", color="#1A1A1A"),
    xaxis_title="Biomasa (t/día)", yaxis_title="Ganancia (M USD/año)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    height=420,
)
fig.update_xaxes(gridcolor="#EEEEEE")
fig.update_yaxes(gridcolor="#EEEEEE")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================================================
# MAPA DEL CORREDOR DE DISTRIBUCIÓN
# ==========================================================================
st.markdown("### Corredor de distribución (ilustrativo)")
st.caption("Corredor León – Aguascalientes – Guadalajara (~250 km). Rutas ilustrativas, no optimizadas.")

corredor = pd.DataFrame({
    "ciudad": ["Lagos de Moreno (planta)", "León", "Aguascalientes", "Guadalajara"],
    "lat": [21.3556, 21.1230, 21.8853, 20.6597],
    "lon": [-101.9419, -101.6804, -102.2916, -103.3496],
})

ruta_lineas = pd.DataFrame({
    "from_lat": [21.3556, 21.3556, 21.3556],
    "from_lon": [-101.9419, -101.9419, -101.9419],
    "to_lat": [21.1230, 21.8853, 20.6597],
    "to_lon": [-101.6804, -102.2916, -103.3496],
})

capa_puntos = pdk.Layer(
    "ScatterplotLayer",
    data=corredor,
    get_position="[lon, lat]",
    get_color="[14, 58, 42, 220]",
    get_radius=6000,
    pickable=True,
)
capa_lineas = pdk.Layer(
    "LineLayer",
    data=ruta_lineas,
    get_source_position="[from_lon, from_lat]",
    get_target_position="[to_lon, to_lat]",
    get_color="[178, 58, 72, 200]",
    get_width=4,
)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(latitude=21.2, longitude=-102.0, zoom=7, pitch=0),
    layers=[capa_lineas, capa_puntos],
    tooltip={"text": "{ciudad}"},
))

st.markdown("---")
st.caption(
    "Datos regionales: 2,813,595 cabezas porcinas en 5 municipios · 48% de la producción "
    "nacional de huevo · 2ª cuenca lechera del país (SIAP 2023). "
    "Fuente operativa: Brimex Energy (primer permiso federal de comercialización de biometano, 2024)."
)
