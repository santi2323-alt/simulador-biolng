import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk
import base64, os
 
def _load_logo():
    try:
        with open("naturgy_logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None
LOGO_B64 = _load_logo()
 
 
st.set_page_config(page_title="Naturgy · Simulador Bio-LNG Jalisco", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
 
# ════════════════════════════════════════════════════════════════════════════
#  IDENTIDAD VISUAL NATURGY
#  Azul corporativo Pantone 302C ≈ #00497B  ·  Naranja 144C ≈ #ED8B00
# ════════════════════════════════════════════════════════════════════════════
AZUL = "#00497B"
AZUL_CLARO = "#0073B7"
NARANJA = "#ED8B00"
VERDE = "#5BA829"
ROJO = "#C0264A"
GRIS_TX = "#3C4A57"
GRIS_SUAVE = "#6B7A88"
GRIS_BG = "#F4F6F8"
 
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=Archivo+Narrow:wght@600;700&display=swap');
 
    .stApp {{ background: #FFFFFF; }}
    * {{ font-family: 'Archivo', 'Helvetica Neue', Arial, sans-serif !important; }}
    h1, h2, h3 {{ font-family: 'Archivo', sans-serif !important; }}
 
    .ng-topbar {{
        background: {AZUL}; margin: -1.5rem -4rem 0 -4rem; padding: 16px 48px;
        display: flex; align-items: center; justify-content: space-between;
    }}
    .ng-logo {{ display: flex; align-items: center; gap: 10px; }}
    .ng-logo img {{ display: block; }}
    .ng-logo-mark {{ width: 30px; height: 30px; background: {NARANJA};
        border-radius: 50% 50% 50% 0; transform: rotate(-45deg); display: inline-block; }}
    .ng-logo-text {{ color: #FFFFFF !important; font-family: 'Archivo' !important;
        font-weight: 800; font-size: 24px; letter-spacing: -0.5px; }}
    .ng-nav {{ color: #B8D4E8 !important; font-size: 13px; font-weight: 500; }}
 
    .ng-hero {{ background: {AZUL}; margin: 0 -4rem 24px -4rem; padding: 34px 48px 40px;
        color: #fff; }}
    .ng-eyebrow {{ color: {NARANJA} !important; font-size: 12px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; }}
    .ng-title {{ color: #FFFFFF !important; font-family: 'Archivo' !important;
        font-size: 40px; font-weight: 800; line-height: 1.05; margin: 8px 0 6px; letter-spacing: -0.5px; }}
    .ng-sub {{ color: #B8D4E8 !important; font-size: 15px; font-weight: 400; }}
 
    section[data-testid="stSidebar"] {{ background: {AZUL}; border: none; min-width: 320px; }}
    section[data-testid="stSidebar"] * {{ color: #DCEAF4 !important; }}
    section[data-testid="stSidebar"] h3 {{ color: #FFFFFF !important; font-family: 'Archivo' !important; }}
    section[data-testid="stSidebar"] hr {{ border-color: #1A5C87; }}
    .side-eyebrow {{ color: {NARANJA} !important; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }}
 
    [data-testid="collapsedControl"] {{ display: block !important; background: {AZUL} !important; border-radius: 0 8px 8px 0; padding: 8px 6px !important; }}
    [data-testid="collapsedControl"] span, [data-testid="collapsedControl"] p {{ font-size: 0 !important; }}
    [data-testid="collapsedControl"]::after {{ content: "›"; color: #FFFFFF; font-size: 24px; font-weight: 700; }}
    [data-testid="stSidebarCollapseButton"] span, [data-testid="stSidebarCollapseButton"] p {{ font-size: 0 !important; }}
    [data-testid="stSidebarCollapseButton"]::after {{ content: "‹"; color: #DCEAF4; font-size: 22px; font-weight: 700; }}
 
    h1, h2, h3, h4 {{ color: {AZUL} !important; }}
    p, label, span, div {{ color: {GRIS_TX}; }}
 
    .ng-section {{ display: flex; align-items: baseline; gap: 12px; margin: 22px 0 14px; }}
    .ng-section-bar {{ width: 4px; height: 22px; background: {NARANJA}; border-radius: 2px; }}
    .ng-section-title {{ font-family: 'Archivo' !important; font-size: 19px; font-weight: 700; color: {AZUL} !important; }}
    .ng-section-ref {{ font-size: 11px; color: {GRIS_SUAVE} !important; letter-spacing: 1px; margin-left: auto; }}
 
    .card {{ background: #FFFFFF; border: 1px solid #E3E9EE; border-radius: 10px; padding: 18px 20px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,73,123,0.06); }}
    .kpi-label {{ font-size: 11px; color: {GRIS_SUAVE}; letter-spacing: 0.5px; text-transform: uppercase; font-weight: 600; }}
    .kpi-value {{ font-family: 'Archivo' !important; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; margin-top: 4px; }}
    .kpi-unit {{ font-size: 13px; color: {GRIS_SUAVE}; font-weight: 500; }}
 
    .badge-ok {{ background: #EDF7E6; border: 1px solid {VERDE}; color: #3D7A12; border-radius: 8px; padding: 13px; text-align: center; font-weight: 700; font-size: 14px; }}
    .badge-no {{ background: #FBECEF; border: 1px solid {ROJO}; color: #A01E3C; border-radius: 8px; padding: 13px; text-align: center; font-weight: 700; font-size: 14px; }}
 
    .ng-status {{ background: {AZUL}; border-radius: 10px; padding: 12px 22px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }}
    .ng-status span {{ color: #B8D4E8 !important; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }}
    .ng-status .on {{ color: {NARANJA} !important; }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.45; }} }}
    .ng-status .on {{ animation: pulse 2s ease-in-out infinite; }}
 
    .footer-note {{ font-size: 11px; color: #9AA8B4; text-align: center; }}
    hr {{ border-color: #E3E9EE; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
 
    @keyframes flowdot {{ 0% {{ left: 0%; opacity: 0; }} 12% {{ opacity: 1; }} 88% {{ opacity: 1; }} 100% {{ left: 100%; opacity: 0; }} }}
    .proc-wrap {{ display: flex; align-items: stretch; margin: 4px 0 8px; border: 1px solid #E3E9EE; border-radius: 10px; overflow: hidden; background: #FAFCFD; }}
    .proc-step {{ flex: 1; padding: 16px 8px; text-align: center; border-right: 1px solid #EDF1F4; }}
    .proc-step:last-child {{ border-right: none; }}
    .proc-name {{ font-size: 10px; font-weight: 700; color: {AZUL}; letter-spacing: 0.3px; margin-top: 7px; text-transform: uppercase; }}
    .proc-val {{ font-family: 'Archivo' !important; font-size: 14px; font-weight: 700; margin-top: 2px; }}
    .proc-conn {{ width: 40px; display: flex; align-items: center; }}
    .proc-line {{ width: 100%; height: 2px; background: #DDE7EE; position: relative; overflow: hidden; }}
    .proc-line::after {{ content: ""; position: absolute; top: -2px; width: 6px; height: 6px; border-radius: 50%; animation: flowdot 2.2s linear infinite; }}
</style>
""", unsafe_allow_html=True)
 
# ── BARRA SUPERIOR + HERO
if LOGO_B64:
    logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:34px; width:auto;" alt="Naturgy"/>'
else:
    logo_html = '<span class="ng-logo-mark"></span><span class="ng-logo-text">naturgy</span>'
st.markdown(f"""
<div class="ng-topbar">
    <div class="ng-logo">{logo_html}</div>
    <span class="ng-nav">México · Transición Energética · Biometano</span>
</div>
<div class="ng-hero">
    <div class="ng-eyebrow">Propuesta de Coinversión · Simulador de Escenarios</div>
    <div class="ng-title">Cadena de Valor del Bio-LNG</div>
    <div class="ng-sub">Lagos de Moreno, Región Altos Norte de Jalisco · Referente operativo: Brimex Energy · DS3001B Tec de Monterrey 2026</div>
</div>
""", unsafe_allow_html=True)
 
# ── SIDEBAR
st.sidebar.markdown('<div class="side-eyebrow">Parámetros de operación</div>', unsafe_allow_html=True)
st.sidebar.markdown("### Ajusta los escenarios")
st.sidebar.markdown('<p style="color:#9CC3DC; font-size:12px; margin-top:-8px;">Modifica los valores para simular distintos escenarios en tiempo real.</p>', unsafe_allow_html=True)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
biomasa = st.sidebar.slider("Biomasa de entrada (t/día)", 200, 1600, 800, 50, help="Referente Brimex: 800 t/día")
st.sidebar.markdown("*Ruta del producto*")
ruta = st.sidebar.radio("ruta", ["Bio-LNG (transporte en camión)", "Red Naturgy (inyección local)"], label_visibility="collapsed")
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("*Mercado y precios*")
precio_lng = st.sidebar.slider("Precio Bio-LNG (USD/GJ)", 15.0, 45.0, 30.0, 0.5, help="Rango: 21–40.5 USD/GJ")
feed_in = st.sidebar.slider("Feed-in tariff red (USD/GJ)", 0.0, 12.0, 0.0, 0.5, help="Francia: hasta ~11. México: 0")
precio_carbono = st.sidebar.slider("Crédito de carbono (USD/ton CO₂eq)", 0, 25, 0, 1)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("*Sustitución de diésel*")
clientes_diesel = st.sidebar.slider("Clientes activos que sustituyen diésel", 0, 5, 3, 1, help="AKRON, Lala, 2 CEDIS Walmart, Bimbo")
 
# ── CÁLCULOS
factor = biomasa / 800.0
biometano_m3d = biomasa * 27.0
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
diesel_sustituido = biolng_m3d * 365 * 0.58 * (clientes_diesel / 3.0)
co2_diesel = diesel_sustituido * 2.68 / 1000
es_biolng = ruta.startswith("Bio-LNG")
ganancia_actual = ganancia_lng if es_biolng else ganancia_red
viable = ganancia_actual >= 0
signo = "+" if ganancia_actual >= 0 else ""
 
# ── BARRA DE ESTADO
estado = "OPERANDO · RUTA BIO-LNG" if es_biolng else "OPERANDO · RUTA RED"
st.markdown(f'''<div class="ng-status">
    <span class="on">● {estado}</span>
    <span>CARGA {factor*100:.0f}%</span>
    <span>REFERENTE BRIMEX 800 t/d</span>
    <span>{"ESTADO: VIABLE" if viable else "ESTADO: NO VIABLE"}</span>
</div>''', unsafe_allow_html=True)
 
# ── TIRA DE PROCESO CON IMÁGENES
GITHUB_RAW = "https://raw.githubusercontent.com/santi2323-alt/simulador-biolng/main"
rc = VERDE if es_biolng else AZUL_CLARO
destino = "BIO-LNG · CAMIÓN" if es_biolng else "BIOMETANO · RED"

st.markdown(f"""
<div class="proc-wrap" style="align-items:flex-start;">
    <div class="proc-step">
        <img src="{GITHUB_RAW}/biomasa_img.png"
             style="width:100%; max-height:90px; object-fit:cover; border-radius:6px;"
             onerror="this.style.display='none'"/>
        <div class="proc-name">Biomasa</div>
        <div class="proc-val" style="color:{NARANJA};">{biomasa:.0f} t/d</div>
    </div>
    <div class="proc-conn"><div class="proc-line"></div></div>
    <div class="proc-step">
        <img src="{GITHUB_RAW}/biodigestor.png"
             style="width:100%; max-height:90px; object-fit:contain; border-radius:6px;"
             onerror="this.style.display='none'"/>
        <div class="proc-name">Biodigestor</div>
        <div class="proc-val" style="color:{rc};">{biomasa*0.9:.0f} t</div>
    </div>
    <div class="proc-conn"><div class="proc-line"></div></div>
    <div class="proc-step">
        <img src="{GITHUB_RAW}/Upgrading.png"
             style="width:100%; max-height:90px; object-fit:contain; border-radius:6px;"
             onerror="this.style.display='none'"/>
        <div class="proc-name">Upgrading</div>
        <div class="proc-val" style="color:{rc};">{biometano_m3d:,.0f} m³/d</div>
    </div>
    <div class="proc-conn"><div class="proc-line"></div></div>
    <div class="proc-step">
        <img src="{GITHUB_RAW}/Licuefaccion.png"
             style="width:100%; max-height:90px; object-fit:contain; border-radius:6px;"
             onerror="this.style.display='none'"/>
        <div class="proc-name">{"Licuefacción" if es_biolng else "Bifurcación"}</div>
        <div class="proc-val" style="color:{rc};">{biolng_m3d:,.0f} m³/d</div>
    </div>
    <div class="proc-conn"><div class="proc-line"></div></div>
    <div class="proc-step">
        <img src="{GITHUB_RAW}/Transporte.png"
             style="width:100%; max-height:90px; object-fit:contain; border-radius:6px;"
             onerror="this.style.display='none'"/>
        <div class="proc-name">{destino}</div>
        <div class="proc-val" style="color:{NARANJA};">{clientes_diesel} clientes</div>
    </div>
</div>
<style>.proc-line::after {{ background: {rc}; }}</style>
""", unsafe_allow_html=True)
 
# ── KPIs
st.markdown('<div class="ng-section"><div class="ng-section-bar"></div><div class="ng-section-title">Indicadores clave</div><div class="ng-section-ref">FIG. 1 · TIEMPO REAL</div></div>', unsafe_allow_html=True)
def kpi(col, label, value, unit, color):
    col.markdown(f'<div class="card"><div class="kpi-label">{label}</div><div class="kpi-value" style="color:{color};">{value} <span class="kpi-unit">{unit}</span></div></div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
kpi(m1, "Ganancia anual estimada", f"{signo}{ganancia_actual:,.1f}", "M USD/año", VERDE if viable else ROJO)
kpi(m2, "Biometano producido", f"{biometano_m3d:,.0f}", "m³/día", AZUL)
kpi(m3, "Bio-LNG generado", f"{biolng_m3d:,.0f}", "m³/día", AZUL_CLARO)
kpi(m4, "CO₂ evitado", f"{co2_evitado_ton:,.0f}", "ton/año", NARANJA)
 
# ── GAUGES
def gauge(value, title, vmin, vmax, color, ref=None):
    ind = dict(mode="gauge+number" + ("+delta" if ref is not None else ""), value=value,
        number={'font': {'size': 24, 'color': AZUL, 'family': 'Archivo'}},
        title={'text': title, 'font': {'size': 11, 'color': GRIS_SUAVE, 'family': 'Archivo'}},
        gauge={'axis': {'range': [vmin, vmax], 'tickcolor': '#C5D2DC', 'tickfont': {'size': 9, 'color': '#9AA8B4'}},
            'bar': {'color': color, 'thickness': 0.30}, 'bgcolor': '#F1F5F8', 'borderwidth': 1, 'bordercolor': '#E3E9EE',
            'steps': [{'range': [vmin, vmin+(vmax-vmin)*0.5], 'color': '#EAF1F6'}, {'range': [vmin+(vmax-vmin)*0.5, vmax], 'color': '#DFEAF2'}],
            'threshold': {'line': {'color': AZUL, 'width': 2}, 'thickness': 0.85, 'value': value}})
    if ref is not None:
        ind['delta'] = {'reference': ref, 'increasing': {'color': VERDE}, 'decreasing': {'color': ROJO}, 'font': {'size': 12, 'family': 'Archivo'}}
    fig = go.Figure(go.Indicator(**ind))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=42, b=8), paper_bgcolor='#FFFFFF', transition={'duration': 500, 'easing': 'cubic-in-out'})
    return fig
 
g1, g2, g3, g4 = st.columns(4)
g1.plotly_chart(gauge(biomasa, "BIOMASA t/día", 200, 1600, NARANJA, ref=800), use_container_width=True, key="g1")
g2.plotly_chart(gauge(biometano_m3d, "BIOMETANO m³/día", 0, 43200, AZUL, ref=21600), use_container_width=True, key="g2")
g3.plotly_chart(gauge(biolng_m3d, "BIO-LNG m³/día", 0, 14256, AZUL_CLARO, ref=7128), use_container_width=True, key="g3")
g4.plotly_chart(gauge(ganancia_actual, "GANANCIA M USD/año", -8, 4, VERDE if viable else ROJO, ref=0), use_container_width=True, key="g4")
 
# ── GRÁFICA + MAPA
left, right = st.columns([1.3, 1])
with left:
    st.markdown('<div class="ng-section"><div class="ng-section-bar"></div><div class="ng-section-title">Curva de ganancia por escala</div><div class="ng-section-ref">FIG. 2</div></div>', unsafe_allow_html=True)
    xs = np.arange(200, 1601, 50)
    gan_lng_x = (precio_lng - costo_lng) * (xs * 27 * 365 * GJ_m3 * 0.33) / 1_000_000
    gan_red_x = (precio_red - costo_bm) * (xs * 27 * 365 * GJ_m3) / 1_000_000
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=gan_lng_x, name="Bio-LNG", line=dict(color=VERDE, width=3), fill='tozeroy', fillcolor='rgba(91,168,41,0.08)'))
    fig.add_trace(go.Scatter(x=xs, y=gan_red_x, name="Red Naturgy (con feed-in)", line=dict(color=AZUL_CLARO, width=2, dash='dot')))
    fig.add_hline(y=0, line_color="#C5D2DC", line_width=1)
    fig.add_vline(x=biomasa, line_color=NARANJA, line_width=2, line_dash="dash", annotation_text=f"  {biomasa} t/d", annotation_font_color=NARANJA)
    fig.update_layout(plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(color=GRIS_TX, family="Barlow", size=12), height=290, margin=dict(l=10, r=10, t=10, b=10), legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12), xaxis=dict(title="Biomasa (t/día)", gridcolor="#EDF1F4", zeroline=False), yaxis=dict(title="Ganancia (M USD/año)", gridcolor="#EDF1F4", zeroline=False))
    st.plotly_chart(fig, use_container_width=True, key="curva")
    st.markdown('<div class="ng-section"><div class="ng-section-bar"></div><div class="ng-section-title">Sustitución de diésel</div><div class="ng-section-ref">FIG. 3</div></div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    kpi(d1, "Diésel sustituido", f"{diesel_sustituido/1000:,.0f}", "mil L/año", NARANJA)
    kpi(d2, "CO₂ evitado (sustitución)", f"{co2_diesel:,.0f}", "ton/año", VERDE)
 
with right:
    st.markdown('<div class="ng-section"><div class="ng-section-bar"></div><div class="ng-section-title">Corredor de distribución</div><div class="ng-section-ref">FIG. 4 · JALISCO</div></div>', unsafe_allow_html=True)
    PLANTA = {"lat": 21.3795, "lon": -101.9180}
    clientes = pd.DataFrame([
        {"name": "AKRON · Lagos de Moreno", "lat": 21.3850, "lon": -101.9050, "km": 7},
        {"name": "Grupo Lala · Aguascalientes", "lat": 21.8550, "lon": -102.2960, "km": 82},
        {"name": "Walmart CEDIS · Silao Bajío", "lat": 20.9480, "lon": -101.4280, "km": 92},
        {"name": "Walmart CEDIS · Tlajomulco GDL", "lat": 20.4700, "lon": -103.4450, "km": 197},
        {"name": "Grupo Bimbo · Zapopan GDL", "lat": 20.7060, "lon": -103.4530, "km": 198},
    ])
    planta_df = pd.DataFrame([{"name": "PLANTA Bio-LNG · Lagos de Moreno", "lat": PLANTA["lat"], "lon": PLANTA["lon"]}])
    rutas = pd.DataFrame([{"fl": PLANTA["lat"], "fo": PLANTA["lon"], "tl": r["lat"], "to": r["lon"]} for _, r in clientes.iterrows()])
    layer_lines = pdk.Layer("LineLayer", rutas, get_source_position=["fo", "fl"], get_target_position=["to", "tl"], get_color=[237, 139, 0, 180], get_width=3)
    layer_cli = pdk.Layer("ScatterplotLayer", clientes, get_position=["lon", "lat"], get_color=[0, 73, 123, 230], get_radius=7000, pickable=True)
    layer_pl = pdk.Layer("ScatterplotLayer", planta_df, get_position=["lon", "lat"], get_color=[237, 139, 0, 255], get_radius=11000, pickable=True)
    st.pydeck_chart(pdk.Deck(map_style="road", initial_view_state=pdk.ViewState(latitude=21.1, longitude=-102.6, zoom=6.5, pitch=40), layers=[layer_lines, layer_cli, layer_pl], tooltip={"text": "{name}"}), use_container_width=True)
    if viable:
        st.markdown(f'<div class="badge-ok">VIABLE · {signo}{ganancia_actual:,.1f} M USD/año</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge-no">NO VIABLE · ajusta precio o feed-in</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card" style="margin-top:10px;"><div class="kpi-label">Ruta seleccionada</div><div style="color:{AZUL}; font-weight:700; margin-top:4px; font-size:15px;">{ruta}</div><div style="color:{GRIS_SUAVE}; font-size:12px; margin-top:6px; line-height:1.5;">{"El Bio-LNG viaja en camión hasta 198 km y sustituye diésel en industria y centros de distribución." if es_biolng else "El biometano se inyecta a la red local de Naturgy en zona Bajío Sur."}</div></div>', unsafe_allow_html=True)
 
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<p class="footer-note">Modelo basado en referente operativo Brimex Energy (800 t/d, 21,600 m³/d) · IEA 2025 · EIA 2025 · Gildea et al. 2025 · Capra et al. 2019 · SIAP 2023 · Clientes: AKRON, Grupo Lala, Walmart CEDIS, Grupo Bimbo</p>', unsafe_allow_html=True)
