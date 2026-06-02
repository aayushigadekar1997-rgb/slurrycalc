import streamlit as st
import matplotlib.pyplot as plt
import matplotlib

st.set_page_config(page_title="SlurryCalc", page_icon="🔧", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 2rem; }
    .metric-card {
        background-color: #1e2330;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        border: 1px solid #2a3040;
        margin-bottom: 10px;
    }
    .card-title { font-size: 13px; color: #6a7490; margin-bottom: 4px; font-family: monospace; text-transform: uppercase; letter-spacing: 0.05em; }
    .card-value { font-size: 26px; font-weight: 600; margin: 0; }
    .card-sub   { font-size: 12px; color: #6a7490; margin-top: 2px; }
    .ok     { color: #40b080; }
    .warn   { color: #d08030; }
    .danger { color: #e05040; }
    .section-head { font-size: 11px; color: #6a7490; letter-spacing: 0.1em; text-transform: uppercase; font-family: monospace; margin-bottom: 0.75rem; border-bottom: 1px solid #2a3040; padding-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("# 🔧 SlurryCalc")
st.markdown("**Pipeline Wear & Life Predictor** · Built by Aayushi Gadekar · Chemical Engineer & Graduate PM · Brisbane, AU")
st.divider()

# --- SIDEBAR INPUTS ---
st.sidebar.markdown("### Slurry Properties")
density  = st.sidebar.slider("Slurry density (kg/m³)",   1050, 2200, 1400, step=10)
velocity = st.sidebar.slider("Flow velocity (m/s)",       1.0,  6.0,  3.0,  step=0.1)
particle = st.sidebar.slider("Particle size (µm)",        50,   2000, 300,  step=10)
hardness = st.sidebar.slider("Particle hardness (Mohs)",  1.0,  9.0,  5.0,  step=0.5)

st.sidebar.markdown("### Pipe Properties")
wall     = st.sidebar.slider("Wall thickness (mm)",       5,    50,   12,   step=1)

st.sidebar.markdown("### Mineral Type")
mineral  = st.sidebar.selectbox("Select mineral", [
    ("Coal / Phosphate",  1.0),
    ("Copper / Zinc ore", 1.3),
    ("Gold / Nickel ore", 1.6),
    ("Iron ore",          2.0),
    ("Lithium / Silica",  2.5),
], format_func=lambda x: x[0])
mineral_factor = mineral[1]

# --- MATERIALS ---
materials = [
    {"name": "Carbon Steel",      "K": 2.80, "cost": 1.0},
    {"name": "HDPE",              "K": 0.80, "cost": 1.8},
    {"name": "Rubber-Lined",      "K": 0.55, "cost": 2.4},
    {"name": "Chrome White Iron", "K": 0.35, "cost": 3.2},
    {"name": "Ceramic-Lined",     "K": 0.18, "cost": 4.5},
]

def calc_wear(K):
    return K * (density/1000) * (velocity**2.8) * ((particle/1000)**0.4) * (hardness**1.2) * mineral_factor * 0.02

def status(life):
    if life >= 6:  return "ok",     "GOOD"
    if life >= 3:  return "warn",   "MODERATE"
    return              "danger", "HIGH RISK"

# --- KEY METRICS (rubber-lined as primary) ---
primary     = next(m for m in materials if m["name"] == "Rubber-Lined")
wear_rate   = calc_wear(primary["K"])
service_life = wall / wear_rate
inspect     = max(1, round(service_life * 12 * 0.3))
sc, sl      = status(service_life)

st.markdown('<div class="section-head">Key Metrics — Rubber-Lined Steel</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="card-title">Wear Rate</div>
        <div class="card-value {sc}">{round(wear_rate,2)} <span style="font-size:14px">mm/yr</span></div>
        <div class="card-sub">At pipe invert</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="card-title">Service Life</div>
        <div class="card-value {sc}">{round(service_life,1)} <span style="font-size:14px">yrs</span></div>
        <div class="card-sub">Based on wall thickness</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="card-title">Inspection Interval</div>
        <div class="card-value {sc}">{inspect} <span style="font-size:14px">months</span></div>
        <div class="card-sub">Recommended UT scanning</div>
    </div>""", unsafe_allow_html=True)

with c4:
    replacements = max(0, round(5 / service_life) - 1)
    st.markdown(f"""<div class="metric-card">
        <div class="card-title">Replacements (5yr)</div>
        <div class="card-value {sc}">{replacements}</div>
        <div class="card-sub">Estimated pipe replacements</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# --- MATERIAL COMPARISON TABLE + CHART SIDE BY SIDE ---
left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="section-head">Material Comparison</div>', unsafe_allow_html=True)
    for m in materials:
        wr   = calc_wear(m["K"])
        life = wall / wr
        sc2, sl2 = status(life)
        st.markdown(f"""<div class="metric-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="card-title">{m['name']}</div>
                    <div class="card-value {sc2}" style="font-size:20px">{round(wr,2)} mm/yr</div>
                    <div class="card-sub">Service life: {round(life,1)} yrs</div>
                </div>
                <div style="text-align:right">
                    <span style="font-size:11px; padding:3px 10px; border-radius:99px; font-weight:500;
                        background:{'#0d3320' if sc2=='ok' else '#3a2010' if sc2=='warn' else '#3a1010'};
                        color:{'#40b080' if sc2=='ok' else '#d08030' if sc2=='warn' else '#e05040'}">
                        {sl2}
                    </span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-head">Wall Loss Over Time</div>', unsafe_allow_html=True)
    matplotlib.rcParams['figure.facecolor'] = '#0f1117'
    matplotlib.rcParams['axes.facecolor']   = '#1e2330'
    matplotlib.rcParams['axes.edgecolor']   = '#2a3040'
    matplotlib.rcParams['text.color']       = '#e8eaf0'
    matplotlib.rcParams['xtick.color']      = '#6a7490'
    matplotlib.rcParams['ytick.color']      = '#6a7490'
    matplotlib.rcParams['grid.color']       = '#2a3040'

    colors = ["#e05040", "#f0a030", "#40b080", "#4090d0", "#a070d0"]
    fig, ax = plt.subplots(figsize=(6, 4))
    years   = list(range(0, 31))

    for i, m in enumerate(materials):
        wr        = calc_wear(m["K"])
        wall_loss = [wr * y for y in years]
        ax.plot(years, wall_loss, label=m["name"], color=colors[i], linewidth=2)

    ax.axhline(y=wall, color="#e05040", linestyle="--", linewidth=1.5, label="Failure threshold")
    ax.set_xlabel("Years in service", color="#6a7490")
    ax.set_ylabel("Wall loss (mm)",   color="#6a7490")
    ax.legend(fontsize=8, facecolor="#1e2330", edgecolor="#2a3040", labelcolor="#e8eaf0")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

st.divider()
st.caption("Based on Durand-Condolios wear model. For indicative purposes only — validate against field data before operational decisions.")