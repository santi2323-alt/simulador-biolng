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
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
    .stApp { background: #FFFFFF; }
    * { font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif !important; }
    h1, h2 { font-family: 'Source Sans 3', Georgia, serif !important; letter-spacing: -0.5px !important; }
 
    section[data-testid="stSidebar"] { background: #0E3A2A; border-right: none; min-width: 330px; }
    section[data-testid="stSidebar"] * { color: #DDEAE3 !important; }
    section[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .eyebrow-side { color: #6FD79E !important; font-size: 10px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; }
    section[data-testid="stSidebar"] hr { border-color: #1C5640; }
 
    [data-testid="collapsedControl"] { display: block !important; background: #0E3A2A !important; border-radius: 0 8px 8px 0; padding: 8px 6px !important; }
    [data-testid="collapsedControl"] span, [data-testid="collapsedControl"] p { font-size: 0 !important; }
    [data-testid="collapsedControl"]::after { content: "›"; color: #FFFFFF; font-size: 24px; font-weight: 700; }
    [data-testid="stSidebarCollapseButton"] span, [data-testid="stSidebarCollapseButton"] p { font-size: 0 !important; }
    [data-testid="stSidebarCollapseButton"]::after { content: "‹"; color: #DDEAE3; font-size: 22px; font-weight: 700; }
 
    h1, h2, h3, h4 { color: #15241D !important; }
    p, label, span, div { color: #44525E; }
    .eyebrow { font-size: 11px; font-weight: 700; letter-spacing: 2.5px; color: #0E3A2A; text-transform: uppercase; }
 
    /* Tarjetas estilo panel de instrumentos */
    .card { background: #FFFFFF; border: 1px solid #E2E8E5; border-radius: 6px; padding: 16px 18px; margin-bottom: 10px; }
    .panel-tech { background: #0F1C18; border: 1px solid #1C5640; border-radius: 6px; padding: 4px; }
    .kpi-label { font-size: 10px; color: #7E8C86; letter-spacing: 1px; text-transform: uppercase; font-weight: 700; font-family: 'JetBrains Mono', monospace !important; }
    .kpi-value { font-size: 30px; font-weight: 800; letter-spacing: -1px; line-height: 1.1; margin-top: 4px; font-family: 'JetBrains Mono', monospace !important; }
    .kpi-unit { font-size: 12px; color: #7E8C86; font-weight: 500; }
 
    .badge-ok { background: #E6F4EC; border: 1px solid #1C8C5A; color: #0E5E3A; border-radius: 6px; padding: 12px; text-align: center; font-weight: 700; font-size: 14px; font-family: 'JetBrains Mono', monospace !important; }
    .badge-no { background: #FBECEF; border: 1px solid #C0264A; color: #A01E3C; border-radius: 6px; padding: 12px; text-align: center; font-weight: 700; font-size: 14px; font-family: 'JetBrains Mono', monospace !important; }
    .section-title { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #15241D; text-transform: uppercase; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace !important; }
    .status-bar { background: #0F1C18; border-radius: 6px; padding: 8px 16px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
    .status-item { font-family: 'JetBrains Mono', monospace !important; font-size: 11px; color: #6FD79E; }
    .footer-note { font-size: 11px; color: #A3B1BC; text-align: center; font-family: 'JetBrains Mono', monospace !important; }
    hr { border-color: #E2E8E5; }
    #MainMenu, footer, header { visibility: hidden; }
 
    /* Encabezados de sección estilo reporte IEA */
    .ieahdr { display: flex; align-items: center; gap: 12px; border-bottom: 2px solid #0E3A2A; padding-bottom: 6px; margin-bottom: 14px; margin-top: 8px; }
    .ieanum { background: #0E3A2A; color: #FFFFFF !important; font-family: 'JetBrains Mono', monospace !important; font-size: 13px; font-weight: 700; padding: 3px 9px; border-radius: 3px; }
    .iealabel { font-family: 'Source Sans 3', sans-serif !important; font-size: 14px; font-weight: 700; color: #15241D !important; letter-spacing: 0.3px; text-transform: uppercase; flex: 1; }
    .iearef { font-family: 'JetBrains Mono', monospace !important; font-size: 10px; color: #A3B1BC !important; letter-spacing: 1px; }
 
    /* Animación de pulso en la barra de estado */
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
    .status-item:first-child { animation: pulse 2s ease-in-out infinite; }
 
    /* Animación de barrido en tarjetas KPI */
    @keyframes sweep { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
    .card { position: relative; overflow: hidden; }
    .card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #1C8C5A, transparent);
        background-size: 200% 100%; animation: sweep 3s linear infinite; }
 
    /* Líneas de escaneo sutiles en el fondo de la barra de estado */
    .status-bar { position: relative; overflow: hidden; }
    @keyframes scan { 0% { transform: translateX(-100%); } 100% { transform: translateX(400%); } }
    .status-bar::after { content: ""; position: absolute; top: 0; bottom: 0; width: 60px;
        background: linear-gradient(90deg, transparent, rgba(111,215,158,0.08), transparent);
        animation: scan 4s linear infinite; }
 
</style>
""", unsafe_allow_html=True)
 
VERDE = "#1C8C5A"; VERDE_OSC = "#0E5E3A"; AZUL = "#2E7DB8"
AMBAR = "#C98A2B"; ROJO = "#C0264A"; GRIS = "#7E8C86"
 
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="eyebrow">Naturgy México · Panel de Simulación</div>', unsafe_allow_html=True)
    st.markdown("## Cadena de Valor del Bio-LNG")
    st.markdown('<p style="color:#7E8C86; margin-top:-10px;">Lagos de Moreno, Región Altos Norte de Jalisco · Referente operativo: Brimex Energy</p>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="text-align:right; padding-top:22px;"><div style="display:inline-block; border:1.5px solid #0E3A2A; border-radius:6px; padding:6px 14px;"><span style="color:#0E3A2A; font-weight:700; font-size:13px; letter-spacing:0.5px;">DS3001B</span><br><span style="color:#7E8C86; font-size:10px;">Tec de Monterrey · 2026</span></div></div>', unsafe_allow_html=True)
 
# Sidebar
st.sidebar.markdown('<div class="eyebrow-side">Parámetros de operación</div>', unsafe_allow_html=True)
st.sidebar.markdown("### Ajusta los escenarios")
st.sidebar.markdown('<p style="color:#A8C5B8; font-size:12px; margin-top:-8px;">Modifica los valores para simular distintos escenarios en tiempo real.</p>', unsafe_allow_html=True)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
biomasa = st.sidebar.slider("Biomasa de entrada (t/día)", 200, 1600, 800, 50, help="Referente Brimex: 800 t/día")
st.sidebar.markdown("**Ruta del producto**")
ruta = st.sidebar.radio("ruta", ["Bio-LNG (transporte en camión)", "Red Naturgy (inyección local)"], label_visibility="collapsed")
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("**Mercado y precios**")
precio_lng = st.sidebar.slider("Precio Bio-LNG (USD/GJ)", 15.0, 45.0, 30.0, 0.5, help="Rango: 21–40.5 USD/GJ")
feed_in = st.sidebar.slider("Feed-in tariff red (USD/GJ)", 0.0, 12.0, 0.0, 0.5, help="Francia: hasta ~11. México: 0")
precio_carbono = st.sidebar.slider("Crédito de carbono (USD/ton CO₂eq)", 0, 25, 0, 1)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("**Sustitución de diésel**")
clientes_diesel = st.sidebar.slider("Clientes activos que sustituyen diésel", 0, 5, 3, 1, help="AKRON, Lala, 2 CEDIS Walmart, Bimbo")
 
# Cálculos
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
diesel_sustituido = biolng_m3d * 365 * 0.58 * (clientes_diesel / 3.0)
co2_diesel = diesel_sustituido * 2.68 / 1000
es_biolng = ruta.startswith("Bio-LNG")
ganancia_actual = ganancia_lng if es_biolng else ganancia_red
viable = ganancia_actual >= 0
signo = "+" if ganancia_actual >= 0 else ""
 
# Barra de estado tipo SCADA
estado = "● OPERANDO · BIO-LNG" if es_biolng else "● OPERANDO · RED"
st.markdown(f'''<div class="status-bar">
    <span class="status-item">{estado}</span>
    <span class="status-item">CARGA: {factor*100:.0f}%</span>
    <span class="status-item">REF: BRIMEX 800 t/d</span>
    <span class="status-item">{"STATUS: VIABLE" if viable else "STATUS: NO VIABLE"}</span>
</div>''', unsafe_allow_html=True)
 
# ─── GAUGES TIPO VELOCÍMETRO ─────────────────────────────────────────────────
def gauge(value, title, vmin, vmax, color, suffix="", ref=None):
    ind = dict(
        mode="gauge+number" + ("+delta" if ref is not None else ""),
        value=value,
        number={'suffix': suffix, 'font': {'size': 24, 'color': '#15241D', 'family': 'JetBrains Mono'}},
        title={'text': title, 'font': {'size': 11, 'color': '#7E8C86', 'family': 'JetBrains Mono'}},
        gauge={
            'axis': {'range': [vmin, vmax], 'tickcolor': '#C5CFD6', 'tickfont': {'size': 9, 'color': '#A3B1BC'}, 'tickwidth': 1},
            'bar': {'color': color, 'thickness': 0.30},
            'bgcolor': '#F4F7F5',
            'borderwidth': 1,
            'bordercolor': '#E2E8E5',
            'steps': [
                {'range': [vmin, vmin + (vmax-vmin)*0.33], 'color': '#F0F4F2'},
                {'range': [vmin + (vmax-vmin)*0.33, vmin + (vmax-vmin)*0.66], 'color': '#E7EFEA'},
                {'range': [vmin + (vmax-vmin)*0.66, vmax], 'color': '#DDE9E2'},
            ],
            'threshold': {'line': {'color': '#15241D', 'width': 2}, 'thickness': 0.85, 'value': value},
        }
    )
    if ref is not None:
        ind['delta'] = {'reference': ref, 'increasing': {'color': color}, 'decreasing': {'color': '#C0264A'},
                        'font': {'size': 12, 'family': 'JetBrains Mono'}}
    fig = go.Figure(go.Indicator(**ind))
    fig.update_layout(height=210, margin=dict(l=20, r=20, t=45, b=10),
        paper_bgcolor='#FFFFFF', font={'family': 'JetBrains Mono'},
        transition={'duration': 500, 'easing': 'cubic-in-out'})
    return fig
 
st.markdown('<div class="ieahdr"><span class="ieanum">01</span><span class="iealabel">Indicadores de operación · tiempo real</span><span class="iearef">FIG. 1.1</span></div>', unsafe_allow_html=True)
g1, g2, g3, g4 = st.columns(4)
with g1:
    st.plotly_chart(gauge(biomasa, "BIOMASA t/día", 200, 1600, VERDE, ref=800), use_container_width=True, key="g1")
with g2:
    st.plotly_chart(gauge(biometano_m3d, "BIOMETANO m³/día", 0, 43200, VERDE_OSC, ref=21600), use_container_width=True, key="g2")
with g3:
    st.plotly_chart(gauge(biolng_m3d, "BIO-LNG m³/día", 0, 14256, AZUL, ref=7128), use_container_width=True, key="g3")
with g4:
    gan_color = VERDE if viable else ROJO
    st.plotly_chart(gauge(ganancia_actual, "GANANCIA M USD/año", -8, 4, gan_color, ref=0), use_container_width=True, key="g4")
 
# ─── GRÁFICA + MAPA ──────────────────────────────────────────────────────────
left, right = st.columns([1.3, 1])
with left:
    st.markdown('<div class="ieahdr"><span class="ieanum">02</span><span class="iealabel">Curva de ganancia · escala de biomasa</span><span class="iearef">FIG. 2.1</span></div>', unsafe_allow_html=True)
    xs = np.arange(200, 1601, 50)
    gan_lng_x = (precio_lng - costo_lng) * (xs * 27 * 365 * GJ_m3 * 0.33) / 1_000_000
    gan_red_x = (precio_red - costo_bm) * (xs * 27 * 365 * GJ_m3) / 1_000_000
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=gan_lng_x, name="Bio-LNG", line=dict(color=VERDE, width=3), fill='tozeroy', fillcolor='rgba(28,140,90,0.08)'))
    fig.add_trace(go.Scatter(x=xs, y=gan_red_x, name="Red Naturgy (con feed-in)", line=dict(color=AZUL, width=2, dash='dot')))
    fig.add_hline(y=0, line_color="#C5CFD6", line_width=1)
    fig.add_vline(x=biomasa, line_color=AMBAR, line_width=2, line_dash="dash", annotation_text=f"  {biomasa} t/d", annotation_font_color=AMBAR)
    fig.update_layout(plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(color="#44525E", family="JetBrains Mono", size=11), height=290, margin=dict(l=10, r=10, t=10, b=10), legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12), xaxis=dict(title="Biomasa (t/día)", gridcolor="#EDF1F4", zeroline=False), yaxis=dict(title="Ganancia (M USD/año)", gridcolor="#EDF1F4", zeroline=False))
    st.plotly_chart(fig, use_container_width=True, key="curva")
    st.markdown('<div class="ieahdr"><span class="ieanum">03</span><span class="iealabel">Sustitución de diésel · clientes activos</span><span class="iearef">FIG. 3.1</span></div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    d1.markdown(f'<div class="card"><div class="kpi-label">DIÉSEL SUSTITUIDO</div><div class="kpi-value" style="color:{AMBAR};">{diesel_sustituido/1000:,.0f} <span class="kpi-unit">mil L/año</span></div></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="card"><div class="kpi-label">CO₂ EVITADO (SUST.)</div><div class="kpi-value" style="color:{VERDE};">{co2_diesel:,.0f} <span class="kpi-unit">ton/año</span></div></div>', unsafe_allow_html=True)
 
with right:
    st.markdown('<div class="ieahdr"><span class="ieanum">04</span><span class="iealabel">Corredor de distribución · Jalisco</span><span class="iearef">FIG. 4.1</span></div>', unsafe_allow_html=True)
    # PLANTA (origen) y 5 CLIENTES REALES con direcciones verificadas
    PLANTA = {"lat": 21.3795, "lon": -101.9180}  # Lagos de Moreno (zona industrial Conalep)
    clientes = pd.DataFrame([
        {"name": "AKRON · Lagos de Moreno", "lat": 21.3850, "lon": -101.9050, "km": 7, "tipo": "Industria"},
        {"name": "Grupo Lala · Aguascalientes", "lat": 21.8550, "lon": -102.2960, "km": 82, "tipo": "Industria láctea"},
        {"name": "Walmart CEDIS · Silao Bajío", "lat": 20.9480, "lon": -101.4280, "km": 92, "tipo": "Centro distribución"},
        {"name": "Walmart CEDIS · Tlajomulco GDL", "lat": 20.4700, "lon": -103.4450, "km": 197, "tipo": "Centro distribución"},
        {"name": "Grupo Bimbo · Zapopan GDL", "lat": 20.7060, "lon": -103.4530, "km": 198, "tipo": "Industria alimentaria"},
    ])
    # Punto de planta
    planta_df = pd.DataFrame([{"name": "PLANTA Bio-LNG · Lagos de Moreno", "lat": PLANTA["lat"], "lon": PLANTA["lon"]}])
    # Rutas desde planta a cada cliente
    rutas = pd.DataFrame([
        {"fl": PLANTA["lat"], "fo": PLANTA["lon"], "tl": r["lat"], "to": r["lon"]}
        for _, r in clientes.iterrows()
    ])
    layer_lines = pdk.Layer("LineLayer", rutas, get_source_position=["fo", "fl"], get_target_position=["to", "tl"], get_color=[28, 140, 90, 160], get_width=3)
    layer_clientes = pdk.Layer("ScatterplotLayer", clientes, get_position=["lon", "lat"], get_color=[200, 138, 43, 230], get_radius=7000, pickable=True)
    layer_planta = pdk.Layer("ScatterplotLayer", planta_df, get_position=["lon", "lat"], get_color=[14, 94, 58, 255], get_radius=11000, pickable=True)
    st.pydeck_chart(pdk.Deck(map_style="road", initial_view_state=pdk.ViewState(latitude=21.1, longitude=-102.6, zoom=6.5, pitch=40), layers=[layer_lines, layer_clientes, layer_planta], tooltip={"text": "{name}"}), use_container_width=True)
    # Lista de clientes con distancias
    st.markdown('<div style="font-size:10px; font-family:monospace; color:#7E8C86; margin-top:6px; line-height:1.8;">' +
        '<span style="color:#0E5E3A; font-weight:700;">● PLANTA</span> Lagos de Moreno → ' +
        ' · '.join([f"{r['name'].split(chr(183))[0].strip()} ({r['km']} km)" for _, r in clientes.iterrows()]) +
        '</div>', unsafe_allow_html=True)
    if viable:
        st.markdown(f'<div class="badge-ok">VIABLE · {signo}{ganancia_actual:,.1f} M USD/año</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge-no">NO VIABLE · ajusta precio o feed-in</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card" style="margin-top:10px;"><div class="kpi-label">RUTA SELECCIONADA</div><div style="color:#15241D; font-weight:700; margin-top:4px; font-size:15px;">{ruta}</div><div style="color:#7E8C86; font-size:12px; margin-top:6px; line-height:1.5;">{"El Bio-LNG viaja en camión hasta 250 km y sustituye diésel en flotas e industria cercanas." if es_biolng else "El biometano se inyecta a la red local de Naturgy en zona Bajío Sur."}</div></div>', unsafe_allow_html=True)
 
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<p class="footer-note">Modelo basado en referente operativo Brimex Energy (800 t/d, 21,600 m³/d) · IEA 2025 · EIA 2025 · Gildea et al. 2025 · Capra et al. 2019 · SIAP 2023</p>', unsafe_allow_html=True)
