"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         VoltGuard AI — Digital Twin Simulation Dashboard            ║
║         Aravali College of Engineering and Management               ║
║         Smart Grid IoT Project · 1st Year ECE & IT Team             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Run with:
    streamlit run app.py

Dependencies:
    pip install streamlit plotly pandas numpy
"""


import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
from collections import deque

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIGURATION  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoltGuard AI — Digital Twin",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL DARK-MODE CSS INJECTION
# ─────────────────────────────────────────────────────────────────────────────
DARK_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700;900&display=swap');

/* ── Root palette ── */
:root {
    --bg-deep:    #050a0f;
    --bg-card:    #0d1b2a;
    --bg-panel:   #112035;
    --accent-1:   #00e5ff;   /* cyan  */
    --accent-2:   #ff6b35;   /* orange */
    --accent-3:   #39ff14;   /* neon green */
    --accent-warn:#ffd600;   /* amber */
    --accent-crit:#ff1744;   /* red */
    --text-hi:    #e0f7fa;
    --text-mid:   #80cbc4;
    --text-lo:    #37474f;
    --border:     #1e3a5f;
}

/* ── Global overrides ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: var(--bg-deep) !important;
    color: var(--text-hi) !important;
    font-family: 'Exo 2', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070e18 0%, #0a1628 100%) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
}
[data-testid="stMetricLabel"] p {
    color: var(--text-mid) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: var(--accent-1) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.6rem !important;
}

/* ── Headings ── */
h1, h2, h3 {
    font-family: 'Exo 2', sans-serif !important;
    color: var(--text-hi) !important;
    letter-spacing: 0.05em;
}

/* ── Dividers ── */
hr { border-color: var(--border) !important; }

/* ── Log window ── */
.log-box {
    background: var(--bg-deep);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-1);
    border-radius: 6px;
    padding: 10px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-mid);
    height: 220px;
    overflow-y: auto;
    line-height: 1.7;
}
.log-box .CRITICAL { color: var(--accent-crit) !important; font-weight: bold; }
.log-box .WARN     { color: var(--accent-warn) !important; }
.log-box .OK       { color: var(--accent-3) !important; }
.log-box .INFO     { color: var(--accent-1) !important; }

/* ── Relay badge ── */
.relay-on  { color: var(--accent-3); font-weight:700; }
.relay-off { color: var(--accent-crit); font-weight:700; text-decoration:line-through; opacity:.7; }

/* ── Sidebar sliders ── */
[data-testid="stSlider"] > div > div {
    color: var(--accent-1) !important;
}

/* ── Section titles ── */
.section-title {
    font-family: 'Exo 2', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent-1);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-bottom: 12px;
}

/* ── Footer ── */
.footer {
    text-align: center;
    font-size: 0.72rem;
    color: var(--text-lo);
    padding: 18px 0 6px 0;
    letter-spacing: 0.08em;
}
.footer span { color: var(--accent-1); }

/* ── Grid health bar ── */
.health-bar-wrap {
    background: #0a1628;
    border-radius: 4px;
    height: 8px;
    margin-top: 4px;
    overflow: hidden;
}

/* ── Alert banner ── */
.alert-critical {
    background: rgba(255,23,68,0.15);
    border: 1px solid var(--accent-crit);
    border-radius: 8px;
    padding: 10px 16px;
    color: var(--accent-crit);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    animation: pulse-border 1s infinite alternate;
}
@keyframes pulse-border { from{border-color:#ff1744;} to{border-color:#ff8a80;} }

.alert-ok {
    background: rgba(57,255,20,0.08);
    border: 1px solid var(--accent-3);
    border-radius: 8px;
    padding: 10px 16px;
    color: var(--accent-3);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS & CONFIG
# ─────────────────────────────────────────────────────────────────────────────
GRID_LIMIT_KW      = 80.0   # kW — hard grid limit
SHED_THRESHOLD_KW  = 72.0   # kW — trigger load-shedding at 90 % of limit
HISTORY_LEN        = 60     # data points to keep in rolling window (seconds)
VOLTAGE_NOMINAL    = 415.0  # V (3-phase campus supply)
REFRESH_INTERVAL   = 0.9    # seconds between simulation ticks

# ─── Sector baseline loads (kW) ────────────────────────────────────────────
SECTORS = {
    "Computer Labs":   {"base": 22.0, "essential": True,  "icon": "💻"},
    "Science Labs":    {"base": 15.0, "essential": True,  "icon": "🔬"},
    "Hostels":         {"base": 12.0, "essential": True,  "icon": "🏠"},
    "Canteen":         {"base":  8.0, "essential": True,  "icon": "🍽️"},
    "Admin Block":     {"base":  6.0, "essential": False, "icon": "🏢"},
    "Lobby Lights":    {"base":  3.5, "essential": False, "icon": "💡"},
    "Fountain Pumps":  {"base":  2.5, "essential": False, "icon": "⛲"},
    "Sports Ground":   {"base":  4.0, "essential": False, "icon": "🏟️"},
}

# ─── NILM load signatures ───────────────────────────────────────────────────
NILM_FREQ   = np.linspace(0, 50, 500)   # Hz axis for FFT view

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE  (persists across Streamlit reruns)
# ─────────────────────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "history_time":    deque(maxlen=HISTORY_LEN),
        "history_power":   deque(maxlen=HISTORY_LEN),
        "history_voltage": deque(maxlen=HISTORY_LEN),
        "history_current": deque(maxlen=HISTORY_LEN),
        "sector_history":  {k: deque(maxlen=HISTORY_LEN) for k in SECTORS},
        "relay_states":    {k: True for k in SECTORS},  # True = ON
        "event_log":       deque(maxlen=80),
        "total_savings_kwh": 0.0,
        "shed_active":     False,
        "tick":            0,
        "last_tick_time":  0.0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()

# ─────────────────────────────────────────────────────────────────────────────
#  SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def simulate_sector_load(sector_name: str, base_kw: float, manual_surge: float, tick: int) -> float:
    """
    Generate realistic fluctuating load for a campus sector.

    Strategy:
      • Slow sinusoidal "breathing" (class schedules)  → 8-min period
      • Fast random micro-noise (appliance toggling)   → tick-level
      • Manual surge factor from sidebar               → uniform scaling
      • Sector-specific patterns (e.g., Canteen peaks at lunch)
    """
    t = tick * REFRESH_INTERVAL  # seconds of simulation time

    # ── Sector-specific time pattern ──
    if sector_name == "Canteen":
        # Peaks around "lunch" every ~300 ticks
        phase_boost = 0.4 * np.sin(2 * np.pi * t / 300) ** 2
    elif sector_name == "Computer Labs":
        # Highest during "lab hours" — sawtooth ramp
        phase_boost = 0.2 * abs(np.sin(2 * np.pi * t / 480))
    elif sector_name == "Hostels":
        # Steady with evening peak
        phase_boost = 0.15 * (1 + np.sin(2 * np.pi * t / 600))
    else:
        phase_boost = 0.1 * np.sin(2 * np.pi * t / 360 + hash(sector_name) % 6)

    noise      = random.gauss(0, 0.03 * base_kw)          # ±3 % white noise
    surge_kw   = base_kw * (manual_surge / 100.0)         # surge contribution
    load       = base_kw + base_kw * phase_boost + noise + surge_kw

    return max(0.5, round(load, 2))                        # floor at 0.5 kW


def compute_voltage(total_kw: float) -> float:
    """
    Voltage sags under high load — simplified Thevenin model.
    V_terminal = V_nominal - I * Z_line  →  approximated as linear droop.
    """
    droop_factor = 0.5   # V per kW above 50 kW
    excess       = max(0, total_kw - 50)
    voltage      = VOLTAGE_NOMINAL - droop_factor * excess + random.gauss(0, 1.5)
    return max(360.0, round(voltage, 1))


def compute_current(total_kw: float, voltage: float) -> float:
    """
    I = P / (√3 × V × PF)  — 3-phase formula, PF ≈ 0.9
    """
    PF = 0.9
    current = (total_kw * 1000) / (1.732 * voltage * PF)
    return round(current, 2)


def grid_health_score(total_kw: float, voltage: float) -> int:
    """
    Heuristic score 0–100.  Green ≥ 70, Amber 40–69, Red < 40.
    """
    load_penalty    = max(0, (total_kw - SHED_THRESHOLD_KW) / (GRID_LIMIT_KW - SHED_THRESHOLD_KW)) * 50
    voltage_penalty = max(0, (VOLTAGE_NOMINAL - voltage) / VOLTAGE_NOMINAL) * 50
    score = int(100 - load_penalty - voltage_penalty)
    return max(0, min(100, score))


def auto_load_shedding(total_kw: float, relay_states: dict, log: deque) -> tuple[dict, float]:
    """
    Automated NILM-informed load-shedding algorithm.

    Rules:
      1. If total_kw > SHED_THRESHOLD → trip non-essential sectors (lowest
         priority first) until load drops below threshold.
      2. If total_kw < (SHED_THRESHOLD - 8 kW) → restore tripped sectors.

    Returns: (updated relay_states, power_saved_kw)
    """
    now_str = datetime.now().strftime("%H:%M:%S")
    saved   = 0.0
    new_states = dict(relay_states)

    non_essential = [k for k, v in SECTORS.items() if not v["essential"]]
    # Sort: trip cheapest-recovery sectors last (sort by base load desc)
    non_essential.sort(key=lambda k: SECTORS[k]["base"], reverse=False)

    if total_kw > SHED_THRESHOLD_KW:
        # ── TRIP phase ──
        if not st.session_state.shed_active:
            log.appendleft(f'<span class="CRITICAL">⚡ {now_str} | SURGE ALERT — Load {total_kw:.1f} kW exceeds {SHED_THRESHOLD_KW} kW threshold. Initiating Load-Shed Protocol.</span>')
            st.session_state.shed_active = True

        remaining_excess = total_kw - SHED_THRESHOLD_KW
        for sector in non_essential:
            if remaining_excess <= 0:
                break
            if new_states.get(sector, True):          # only trip if currently ON
                new_states[sector] = False
                shed_amt = SECTORS[sector]["base"]
                remaining_excess -= shed_amt
                saved += shed_amt
                log.appendleft(
                    f'<span class="WARN">🔌 {now_str} | SHED — {SECTORS[sector]["icon"]} {sector} TRIPPED '
                    f'({shed_amt:.1f} kW recovered). AI Relay R-{abs(hash(sector))%900+100}.</span>'
                )
    else:
        # ── RESTORE phase ──
        restore_margin = SHED_THRESHOLD_KW - 8.0
        if total_kw < restore_margin and st.session_state.shed_active:
            for sector in non_essential:
                if not new_states.get(sector, True):
                    new_states[sector] = True
                    log.appendleft(
                        f'<span class="OK">✅ {now_str} | RESTORE — {SECTORS[sector]["icon"]} {sector} '
                        f'relay closed. Grid stable.</span>'
                    )
            st.session_state.shed_active = False
            log.appendleft(f'<span class="OK">✅ {now_str} | SYSTEM NORMAL — All essential loads secured. Grid health restored.</span>')

    return new_states, saved


# ─────────────────────────────────────────────────────────────────────────────
#  NILM SIGNATURE DATA  (pre-computed waveforms for display)
# ─────────────────────────────────────────────────────────────────────────────
def nilm_inductive_waveform(t: np.ndarray) -> np.ndarray:
    """AC Motor (Inductive Load): current LAGS voltage by ~30°."""
    return np.sin(2 * np.pi * 50 * t - np.radians(30)) + 0.18 * np.sin(6 * np.pi * 50 * t)

def nilm_resistive_waveform(t: np.ndarray) -> np.ndarray:
    """Heater (Resistive Load): current IN PHASE with voltage."""
    return np.sin(2 * np.pi * 50 * t) + 0.04 * np.sin(6 * np.pi * 50 * t)

def nilm_voltage_waveform(t: np.ndarray) -> np.ndarray:
    """Reference voltage waveform."""
    return np.sin(2 * np.pi * 50 * t)

NILM_T = np.linspace(0, 0.04, 1000)  # 2 full cycles at 50 Hz


# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY THEME HELPER
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor = "rgba(5,10,15,0)",
    plot_bgcolor  = "rgba(13,27,42,0.85)",
    font          = dict(family="Share Tech Mono, monospace", color="#80cbc4", size=11),
    xaxis         = dict(gridcolor="#1e3a5f", zerolinecolor="#1e3a5f", color="#80cbc4"),
    yaxis         = dict(gridcolor="#1e3a5f", zerolinecolor="#1e3a5f", color="#80cbc4"),
    margin        = dict(l=40, r=20, t=40, b=40),
    hovermode     = "x unified",
    legend        = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#80cbc4")),
)


# ─────────────────────────────────────────────────────────────────────────────
#  ██████████  SIDEBAR  ██████████
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:10px 0 20px 0;'>
      <div style='font-family:"Exo 2",sans-serif; font-size:1.5rem;
                  font-weight:900; color:#00e5ff; letter-spacing:0.1em;'>
        ⚡ VOLTGUARD AI
      </div>
      <div style='font-size:0.65rem; color:#37474f; letter-spacing:0.15em;
                  text-transform:uppercase; margin-top:4px;'>
        Digital Twin · Smart Grid Module
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚙ Simulation Controls</div>', unsafe_allow_html=True)

    # ── Manual surge slider ──
    manual_surge = st.slider(
        "🔺 Campus Surge Load (%)",
        min_value=0, max_value=60, value=0, step=1,
        help="Simulates unexpected load spike (e.g., event day, generator failure)"
    )

    # ── Simulation speed ──
    sim_speed = st.select_slider(
        "⏱ Simulation Speed",
        options=["0.5×", "1×", "2×", "4×"],
        value="1×"
    )
    speed_map = {"0.5×": 1.8, "1×": 0.9, "2×": 0.45, "4×": 0.2}

    st.divider()
    st.markdown('<div class="section-title">🔧 Grid Parameters</div>', unsafe_allow_html=True)

    grid_limit_kw = st.number_input(
        "Grid Capacity (kW)", min_value=50, max_value=150,
        value=int(GRID_LIMIT_KW), step=5
    )
    shed_threshold = st.number_input(
        "Shed Threshold (kW)", min_value=40, max_value=int(grid_limit_kw),
        value=int(SHED_THRESHOLD_KW), step=2
    )

    st.divider()
    st.markdown('<div class="section-title">📡 Relay Override</div>', unsafe_allow_html=True)

    manual_relays = {}
    for sector, info in SECTORS.items():
        label_color = "#39ff14" if st.session_state.relay_states.get(sector, True) else "#ff1744"
        manual_relays[sector] = st.checkbox(
            f"{info['icon']} {sector}",
            value=st.session_state.relay_states.get(sector, True),
            key=f"relay_{sector}"
        )

    st.divider()
    if st.button("🔄 Reset Simulation", use_container_width=True):
        for key in ["history_time","history_power","history_voltage",
                    "history_current","sector_history","event_log",
                    "relay_states","total_savings_kwh","shed_active","tick"]:
            del st.session_state[key]
        _init_state()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  ██████████  TICK ENGINE  ██████████
# ─────────────────────────────────────────────────────────────────────────────
tick = st.session_state.tick
now  = datetime.now()

# ── Compute per-sector loads ──
sector_loads = {}
for sector, info in SECTORS.items():
    relay_on = manual_relays.get(sector, True)
    if relay_on:
        sector_loads[sector] = simulate_sector_load(
            sector, info["base"], manual_surge, tick
        )
    else:
        sector_loads[sector] = 0.0

total_kw = sum(sector_loads.values())
voltage  = compute_voltage(total_kw)
current  = compute_current(total_kw, voltage)
health   = grid_health_score(total_kw, voltage)

# ── Auto load-shedding ──
new_relay_states, saved_kw = auto_load_shedding(
    total_kw, manual_relays, st.session_state.event_log
)
st.session_state.relay_states = new_relay_states
st.session_state.total_savings_kwh += (saved_kw * REFRESH_INTERVAL / 3600)

# ── Periodic INFO logs ──
if tick % 20 == 0:
    st.session_state.event_log.appendleft(
        f'<span class="INFO">ℹ {now.strftime("%H:%M:%S")} | '
        f'Telemetry OK — V={voltage}V · I={current}A · '
        f'P={total_kw:.1f}kW · Health={health}%</span>'
    )
if tick % 45 == 0 and manual_surge > 20:
    st.session_state.event_log.appendleft(
        f'<span class="WARN">⚠ {now.strftime("%H:%M:%S")} | '
        f'High surge detected ({manual_surge}%) — monitoring critical sectors.</span>'
    )

# ── Append to rolling history ──
st.session_state.history_time.append(now)
st.session_state.history_power.append(total_kw)
st.session_state.history_voltage.append(voltage)
st.session_state.history_current.append(current)
for s in SECTORS:
    st.session_state.sector_history[s].append(sector_loads[s])

st.session_state.tick += 1


# ─────────────────────────────────────────────────────────────────────────────
#  ██████████  DASHBOARD HEADER  ██████████
# ─────────────────────────────────────────────────────────────────────────────
col_logo, col_title, col_status = st.columns([1, 5, 2])
with col_logo:
    st.markdown("""
    <div style='font-size:3.2rem; text-align:center; padding-top:8px;
                filter: drop-shadow(0 0 12px #00e5ff);'>⚡</div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <div style='padding-top:6px;'>
      <div style='font-family:"Exo 2",sans-serif; font-size:1.7rem; font-weight:900;
                  color:#e0f7fa; letter-spacing:0.08em;'>VOLTGUARD AI</div>
      <div style='font-size:0.7rem; color:#37474f; letter-spacing:0.18em;
                  text-transform:uppercase;'>
        Digital Twin Simulation · Aravali College of Engineering & Management
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    ts = now.strftime("%Y-%m-%d  %H:%M:%S")
    st.markdown(f"""
    <div style='text-align:right; padding-top:10px;
                font-family:"Share Tech Mono",monospace; font-size:0.75rem;
                color:#00e5ff;'>
        LIVE SIMULATION<br>
        <span style='color:#37474f;'>{ts}</span><br>
        <span style='color:#39ff14;'>● ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin:6px 0 16px 0;'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  ROW 1 — KPI METRICS
# ─────────────────────────────────────────────────────────────────────────────
pct_load = (total_kw / grid_limit_kw) * 100
kc1, kc2, kc3, kc4, kc5 = st.columns(5)

kc1.metric(
    "⚡ Total Load",
    f"{total_kw:.1f} kW",
    f"{pct_load:.1f}% of grid"
)
kc2.metric(
    "🔋 Grid Voltage",
    f"{voltage:.1f} V",
    f"{voltage - VOLTAGE_NOMINAL:+.1f} V droop"
)
kc3.metric(
    "〰 Line Current",
    f"{current:.1f} A",
    None
)
kc4.metric(
    "💾 Energy Saved",
    f"{st.session_state.total_savings_kwh:.3f} kWh",
    "via auto-shed"
)
kc5.metric(
    "🩺 Grid Health",
    f"{health} / 100",
    "CRITICAL" if health < 40 else ("WARN" if health < 70 else "OPTIMAL")
)

# ── Alert banner ──
if total_kw > shed_threshold:
    st.markdown(
        f'<div class="alert-critical">⛔ LOAD SHEDDING ACTIVE — '
        f'Total load {total_kw:.1f} kW exceeds threshold {shed_threshold} kW. '
        f'Non-essential relays TRIPPED to protect critical infrastructure.</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<div class="alert-ok">✅ GRID STABLE — '
        f'Load {total_kw:.1f} kW / {grid_limit_kw} kW  |  All essential systems nominal.</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  ROW 2 — MAIN POWER CHART  +  SECTOR BREAKDOWN
# ─────────────────────────────────────────────────────────────────────────────
c_chart, c_sectors = st.columns([3, 2])

with c_chart:
    st.markdown('<div class="section-title">📈 Real-Time Power Telemetry</div>',
                unsafe_allow_html=True)

    times  = list(st.session_state.history_time)
    powers = list(st.session_state.history_power)
    volts  = list(st.session_state.history_voltage)
    amps   = list(st.session_state.history_current)

    fig_main = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.08
    )

    # ── Power trace ──
    fig_main.add_trace(go.Scatter(
        x=times, y=powers, name="Total Power (kW)",
        line=dict(color="#00e5ff", width=2),
        fill="tozeroy", fillcolor="rgba(0,229,255,0.07)",
        hovertemplate="<b>%{y:.2f} kW</b>"
    ), row=1, col=1)

    # ── Threshold line ──
    fig_main.add_hline(
        y=shed_threshold, line_dash="dash", line_color="#ffd600",
        annotation_text=f"Shed Threshold {shed_threshold} kW",
        annotation_font_color="#ffd600", row=1, col=1
    )
    fig_main.add_hline(
        y=grid_limit_kw, line_dash="dot", line_color="#ff1744",
        annotation_text=f"Grid Limit {grid_limit_kw} kW",
        annotation_font_color="#ff1744", row=1, col=1
    )

    # ── Voltage trace ──
    fig_main.add_trace(go.Scatter(
        x=times, y=volts, name="Voltage (V)",
        line=dict(color="#ff6b35", width=1.5),
        hovertemplate="<b>%{y:.1f} V</b>"
    ), row=2, col=1)

    fig_main.update_layout(
        **PLOTLY_LAYOUT,
        height=340,
        title=dict(text="Live Power & Voltage — Rolling 60 s Window",
                   font=dict(color="#80cbc4", size=12)),
        showlegend=True
    )
    fig_main.update_yaxes(title_text="kW", row=1, col=1,
                          title_font=dict(color="#80cbc4"))
    fig_main.update_yaxes(title_text="Volt", row=2, col=1,
                          title_font=dict(color="#80cbc4"))

    st.plotly_chart(fig_main, use_container_width=True, config={"displayModeBar": False})

with c_sectors:
    st.markdown('<div class="section-title">🏫 Sector Load Distribution</div>',
                unsafe_allow_html=True)

    colors = [
        "#39ff14" if (SECTORS[s]["essential"] and st.session_state.relay_states.get(s, True))
        else ("#00e5ff" if st.session_state.relay_states.get(s, True)
              else "#ff1744")
        for s in sector_loads
    ]

    fig_bar = go.Figure(go.Bar(
        x=list(sector_loads.values()),
        y=[f"{SECTORS[s]['icon']} {s}" for s in sector_loads],
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(0,0,0,0.3)", width=1)
        ),
        hovertemplate="<b>%{y}</b><br>%{x:.2f} kW<extra></extra>"
    ))
    fig_bar.update_layout(
        **PLOTLY_LAYOUT,
        height=340,
        title=dict(text="Current Draw per Sector (kW)",
                   font=dict(color="#80cbc4", size=12)),
        xaxis_title="Power (kW)",
        bargap=0.25
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  ROW 3 — NILM SIGNATURE ANALYSIS  +  SECTOR TREND LINES
# ─────────────────────────────────────────────────────────────────────────────
n_col1, n_col2 = st.columns([3, 2])

with n_col1:
    st.markdown('<div class="section-title">🔬 Appliance Fingerprinting · NILM Signature Analysis</div>',
                unsafe_allow_html=True)

    t_wave = NILM_T
    v_wave = nilm_voltage_waveform(t_wave)
    i_ind  = nilm_inductive_waveform(t_wave)
    i_res  = nilm_resistive_waveform(t_wave)

    # ── Add small tick-based jitter for "live" feel ──
    jitter = 0.01 * np.sin(2 * np.pi * tick / 30 + t_wave * 200)

    fig_nilm = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Inductive Load — AC Motor", "Resistive Load — Heater"),
    )

    # ── Inductive (left) ──
    fig_nilm.add_trace(go.Scatter(
        x=t_wave * 1000, y=v_wave,
        name="V (ref)", line=dict(color="#ffd600", width=1.5, dash="dot"),
        showlegend=True
    ), row=1, col=1)
    fig_nilm.add_trace(go.Scatter(
        x=t_wave * 1000, y=i_ind + jitter,
        name="I — Inductive", line=dict(color="#ff6b35", width=2),
        fill="tozeroy", fillcolor="rgba(255,107,53,0.08)",
        showlegend=True
    ), row=1, col=1)

    # ── Resistive (right) ──
    fig_nilm.add_trace(go.Scatter(
        x=t_wave * 1000, y=v_wave,
        name="V (ref)", line=dict(color="#ffd600", width=1.5, dash="dot"),
        showlegend=False
    ), row=1, col=2)
    fig_nilm.add_trace(go.Scatter(
        x=t_wave * 1000, y=i_res,
        name="I — Resistive", line=dict(color="#39ff14", width=2),
        fill="tozeroy", fillcolor="rgba(57,255,20,0.08)",
        showlegend=True
    ), row=1, col=2)

    fig_nilm.update_layout(
        **PLOTLY_LAYOUT,
        height=260,
        title=dict(
            text="AI distinguishes appliance TYPE from current waveform shape & phase angle",
            font=dict(color="#80cbc4", size=11)
        ),
    )
    for col_idx in [1, 2]:
        fig_nilm.update_xaxes(title_text="Time (ms)", row=1, col=col_idx,
                               gridcolor="#1e3a5f", color="#80cbc4")
        fig_nilm.update_yaxes(title_text="Amplitude (p.u.)", row=1, col=col_idx,
                               gridcolor="#1e3a5f", color="#80cbc4")

    st.plotly_chart(fig_nilm, use_container_width=True, config={"displayModeBar": False})

    # ── NILM legend ──
    nc1, nc2, nc3 = st.columns(3)
    nc1.markdown("""
    <div style='background:#0d1b2a;border:1px solid #1e3a5f;border-radius:6px;
                padding:8px 12px;font-size:0.72rem;font-family:"Share Tech Mono",monospace;'>
        <span style='color:#ff6b35;'>◆</span> <b>Inductive</b><br>
        Phase lag ~30°<br>Harmonics: HIGH<br>PF: 0.6–0.85
    </div>
    """, unsafe_allow_html=True)
    nc2.markdown("""
    <div style='background:#0d1b2a;border:1px solid #1e3a5f;border-radius:6px;
                padding:8px 12px;font-size:0.72rem;font-family:"Share Tech Mono",monospace;'>
        <span style='color:#39ff14;'>◆</span> <b>Resistive</b><br>
        Phase lag ~0°<br>Harmonics: LOW<br>PF: ~1.0
    </div>
    """, unsafe_allow_html=True)
    nc3.markdown("""
    <div style='background:#0d1b2a;border:1px solid #1e3a5f;border-radius:6px;
                padding:8px 12px;font-size:0.72rem;font-family:"Share Tech Mono",monospace;'>
        <span style='color:#ffd600;'>◆</span> <b>Reference V</b><br>
        415 V / 50 Hz<br>3-phase supply<br>Nominal grid
    </div>
    """, unsafe_allow_html=True)

with n_col2:
    st.markdown('<div class="section-title">📊 Sector Trend — Last 60 s</div>',
                unsafe_allow_html=True)

    trend_colors = ["#00e5ff","#ff6b35","#39ff14","#ffd600",
                    "#ce93d8","#80deea","#ffab40","#f48fb1"]
    fig_trend = go.Figure()

    for i, (sector, hist) in enumerate(st.session_state.sector_history.items()):
        fig_trend.add_trace(go.Scatter(
            x=list(st.session_state.history_time),
            y=list(hist),
            name=f"{SECTORS[sector]['icon']} {sector}",
            line=dict(color=trend_colors[i % len(trend_colors)], width=1.5),
            hovertemplate=f"<b>{sector}</b><br>%{{y:.2f}} kW<extra></extra>"
        ))

    fig_trend.update_layout(
        **PLOTLY_LAYOUT,
        height=310,
        title=dict(text="Per-Sector Power Trend",
                   font=dict(color="#80cbc4", size=12)),
        yaxis_title="kW"
    )

# Modify legend separately
    fig_trend.update_layout(
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#80cbc4", size=9)
        )
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  ROW 4 — RELAY STATUS PANEL  +  AI DECISION LOG
# ─────────────────────────────────────────────────────────────────────────────
r_col, l_col = st.columns([2, 3])

with r_col:
    st.markdown('<div class="section-title">🔌 Virtual Relay Status Board</div>',
                unsafe_allow_html=True)

    relay_html = "<table style='width:100%;border-collapse:collapse;font-family:\"Share Tech Mono\",monospace;font-size:0.78rem;'>"
    relay_html += "<tr style='color:#37474f;border-bottom:1px solid #1e3a5f;'><th align='left'>Sector</th><th>Type</th><th>Load</th><th>Relay</th></tr>"

    for sector, info in SECTORS.items():
        relay_on   = st.session_state.relay_states.get(sector, True)
        ess_label  = "ESSENTIAL" if info["essential"] else "non-ess"
        ess_color  = "#00e5ff" if info["essential"] else "#37474f"
        relay_cls  = "relay-on" if relay_on else "relay-off"
        relay_txt  = "● CLOSED" if relay_on else "○ TRIPPED"
        load_val   = f"{sector_loads.get(sector,0):.1f} kW" if relay_on else "0.0 kW"

        relay_html += f"""
        <tr style='border-bottom:1px solid #0d1b2a;'>
          <td style='padding:5px 4px;'>{info['icon']} {sector}</td>
          <td style='color:{ess_color};font-size:0.65rem;'>{ess_label}</td>
          <td style='color:#80cbc4;'>{load_val}</td>
          <td class='{relay_cls}'>{relay_txt}</td>
        </tr>"""
    relay_html += "</table>"

    st.markdown(relay_html, unsafe_allow_html=True)

    # ── Grid health meter ──
    st.markdown("<br>", unsafe_allow_html=True)
    health_color = "#39ff14" if health >= 70 else ("#ffd600" if health >= 40 else "#ff1744")
    st.markdown(f"""
    <div style='font-family:"Share Tech Mono",monospace; font-size:0.7rem;
                color:#80cbc4; margin-bottom:4px;'>
      GRID HEALTH INDEX — <span style='color:{health_color};'>{health}/100</span>
    </div>
    <div style='background:#0a1628;border-radius:4px;height:10px;overflow:hidden;
                border:1px solid #1e3a5f;'>
      <div style='height:100%;width:{health}%;background:linear-gradient(90deg,
           {health_color}88,{health_color});border-radius:4px;
           transition:width 0.5s ease;'></div>
    </div>
    <div style='font-family:"Share Tech Mono",monospace; font-size:0.65rem;
                color:#37474f; margin-top:4px;'>
      Load: {total_kw:.1f}/{grid_limit_kw} kW · Voltage: {voltage:.0f} V · I: {current:.1f} A
    </div>
    """, unsafe_allow_html=True)

with l_col:
    st.markdown('<div class="section-title">🤖 AI Decision Engine — Event Log</div>',
                unsafe_allow_html=True)

    log_entries = list(st.session_state.event_log)
    log_html    = "<br>".join(log_entries) if log_entries else \
                  '<span style="color:#37474f;">Awaiting events…</span>'

    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

    # ── Mini stats ──
    st.markdown("<br>", unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    active_sectors = sum(1 for v in st.session_state.relay_states.values() if v)
    shed_count     = sum(1 for v in st.session_state.relay_states.values() if not v)

    sc1.metric("Active Sectors",   f"{active_sectors}/{len(SECTORS)}")
    sc2.metric("Tripped Relays",   str(shed_count))
    sc3.metric("Surge Override",   f"{manual_surge}%")


# ─────────────────────────────────────────────────────────────────────────────
#  ROW 5 — POWER FACTOR GAUGE  +  FREQUENCY DOMAIN (FFT)
# ─────────────────────────────────────────────────────────────────────────────
g_col, f_col = st.columns(2)

with g_col:
    st.markdown('<div class="section-title">⚙ Power Factor Gauge</div>', unsafe_allow_html=True)

    # Simulate PF degradation with high inductive load
    pf_base = 0.92
    pf = max(0.65, pf_base - 0.003 * manual_surge - random.gauss(0, 0.01))
    pf_color = "#39ff14" if pf > 0.85 else ("#ffd600" if pf > 0.75 else "#ff1744")

    fig_gauge = go.Figure(go.Indicator(
        mode   = "gauge+number+delta",
        value  = round(pf, 3),
        domain = {"x": [0, 1], "y": [0, 1]},
        title  = {"text": "Power Factor (cosφ)", "font": {"color": "#80cbc4", "size": 13}},
        delta  = {"reference": 0.90, "valueformat": ".3f",
                  "increasing": {"color": "#39ff14"}, "decreasing": {"color": "#ff1744"}},
        gauge  = {
            "axis":  {"range": [0.5, 1.0], "tickcolor": "#80cbc4",
                      "tickfont": {"color": "#80cbc4"}},
            "bar":   {"color": pf_color},
            "bgcolor": "#0d1b2a",
            "bordercolor": "#1e3a5f",
            "steps": [
                {"range": [0.5,  0.75], "color": "rgba(255,23,68,0.2)"},
                {"range": [0.75, 0.85], "color": "rgba(255,214,0,0.15)"},
                {"range": [0.85, 1.0],  "color": "rgba(57,255,20,0.1)"},
            ],
            "threshold": {
                "line": {"color": "#ffd600", "width": 3},
                "thickness": 0.8,
                "value": 0.85,
            },
        },
        number = {"font": {"color": pf_color, "family": "Share Tech Mono"}, "valueformat": ".3f"}
    ))
    fig_gauge.update_layout(
        **PLOTLY_LAYOUT,
        height=250,
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

with f_col:
    st.markdown('<div class="section-title">📡 Harmonic Spectrum — FFT Analysis</div>',
                unsafe_allow_html=True)

    # Synthetic harmonic signature: fundamental at 50 Hz with odd harmonics
    freqs     = np.array([50, 150, 250, 350, 450, 550])
    # Inductive loads add strong 3rd/5th harmonics; resistive loads are clean
    harm_amps = np.array([1.0, 0.28 + 0.004*manual_surge, 0.16, 0.08, 0.04, 0.02])
    harm_amps += np.random.normal(0, 0.005, size=len(harm_amps))

    fig_fft = go.Figure()
    for i, (f, a) in enumerate(zip(freqs, harm_amps)):
        bar_col = "#00e5ff" if i == 0 else "#ff6b35"
        fig_fft.add_trace(go.Bar(
            x=[f], y=[a],
            name=f"{f} Hz", marker_color=bar_col,
            width=18,
            hovertemplate=f"<b>{f} Hz</b><br>Amplitude: %{{y:.3f}} p.u.<extra></extra>"
        ))
    fig_fft.add_trace(go.Scatter(
        x=[0, 600], y=[0.05, 0.05],
        mode="lines", line=dict(color="#ffd600", dash="dash", width=1),
        name="THD Threshold", showlegend=True
    ))

    thd = np.sqrt(sum(a**2 for a in harm_amps[1:])) / harm_amps[0] * 100
    fig_fft.update_layout(
        **PLOTLY_LAYOUT,
        height=250,
        barmode="overlay",
        title=dict(
            text=f"Total Harmonic Distortion (THD) = {thd:.1f}%",
            font=dict(color="#80cbc4", size=12)
        ),
        xaxis_title="Frequency (Hz)",
        yaxis_title="Amplitude (p.u.)",
        showlegend=True,
        bargap=0.1
    )
    st.plotly_chart(fig_fft, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.markdown("""
<div class="footer">
  <span>⚡ VoltGuard AI</span> · Digital Twin Smart Grid Simulation ·
  Aravali College of Engineering & Management ·
  <span>1st Year ECE &amp; CS Team</span> · 2024–25<br>
  <span style='color:#1e3a5f;'>Built with Streamlit · Plotly · NumPy · IoT Architecture</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  AUTO-REFRESH  (drives the simulation tick loop)
# ─────────────────────────────────────────────────────────────────────────────
time.sleep(speed_map[sim_speed])
st.rerun()
