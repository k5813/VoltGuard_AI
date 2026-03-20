"""
VoltGuard AI — Digital Twin Simulation Dashboard
Aravali College of Engineering and Management
Run: streamlit run voltguard_app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import datetime
import random

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VoltGuard AI — Digital Twin",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Login Gate
# ─────────────────────────────────────────────
VALID_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "faculty": {"password": "faculty123", "role": "faculty"},
    "guest": {"password": "guest123", "role": "guest"},
}

USER_ROLES = {
    "admin": {"label": "Administrator", "can_override_relays": True, "can_adjust_grid_limit": True, "can_surge": True},
    "faculty": {"label": "Faculty", "can_override_relays": True, "can_adjust_grid_limit": False, "can_surge": True},
    "guest": {"label": "Guest (Read-Only)", "can_override_relays": False, "can_adjust_grid_limit": False, "can_surge": False},
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = "guest"

def show_login():
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        .login-box {
            max-width: 400px;
            margin: 8vh auto;
            background: linear-gradient(135deg, #1a1f2e 0%, #16192b 100%);
            border: 1px solid #2a2f42;
            border-radius: 16px;
            padding: 48px 36px 36px;
            text-align: center;
        }
        .login-title { font-size: 1.8rem; font-weight: 700; color: #e0e0e0; margin-bottom: 4px; }
        .login-sub { font-size: 0.85rem; color: #8892a4; margin-bottom: 28px; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-box">
            <div style="font-size:3rem; margin-bottom:12px;">⚡</div>
            <div class="login-title">VoltGuard AI</div>
            <div class="login-sub">Aravali College — Digital Twin Portal</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if username in VALID_USERS and VALID_USERS[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = VALID_USERS[username]["role"]
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.caption("Demo credentials: `guest` / `guest`")

if not st.session_state.authenticated:
    show_login()
    st.stop()

# Dark theme CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #16192b 100%);
        border: 1px solid #2a2f42;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #e0e0e0; }
    .metric-label { font-size: 0.85rem; color: #8892a4; margin-top: 4px; }
    .status-ok { color: #00e676; }
    .status-warn { color: #ffab00; }
    .status-crit { color: #ff1744; }
    .log-box {
        background: #0a0d14;
        border: 1px solid #1e2233;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Courier New', monospace;
        font-size: 0.78rem;
        color: #8892a4;
        max-height: 260px;
        overflow-y: auto;
    }
    .relay-on { color: #00e676; font-weight: 600; }
    .relay-off { color: #ff1744; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = {"time": [], "labs": [], "hostels": [], "canteen": [], "total": [], "voltage": [], "current": []}
if "logs" not in st.session_state:
    st.session_state.logs = []
if "tripped_relays" not in st.session_state:
    st.session_state.tripped_relays = set()
if "tick" not in st.session_state:
    st.session_state.tick = 0
if "total_savings_kwh" not in st.session_state:
    st.session_state.total_savings_kwh = 0.0

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
GRID_LIMIT_KW = 80.0
VOLTAGE_NOMINAL = 415  # 3-phase RMS

# Non-essential loads that can be shed (name, kW saved)
NON_ESSENTIAL = [
    ("Fountain Pump", 3.5),
    ("Lobby Lights — Block C", 2.8),
    ("Decorative Façade LEDs", 1.5),
    ("Parking Lot Lights", 4.0),
    ("Garden Irrigation Pump", 2.2),
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0e1117",
    font_color="#8892a4",
    margin=dict(l=40, r=20, t=30, b=30),
    xaxis=dict(gridcolor="#1e2233", showgrid=True),
    yaxis=dict(gridcolor="#1e2233", showgrid=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


# ─────────────────────────────────────────────
# Synthetic Data Generator
# ─────────────────────────────────────────────
def generate_load(tick: int, surge_pct: float):
    """Generate realistic fluctuating loads for three campus zones."""
    t = tick * 0.1
    labs = 22 + 6 * np.sin(t * 0.3) + random.gauss(0, 1.2)
    hostels = 18 + 4 * np.sin(t * 0.15 + 1) + random.gauss(0, 0.9)
    canteen = 10 + 3 * np.sin(t * 0.5 + 2) + random.gauss(0, 0.7)

    # Apply surge multiplier
    surge_mult = 1 + surge_pct / 100
    labs *= surge_mult
    hostels *= surge_mult
    canteen *= surge_mult

    total = labs + hostels + canteen
    voltage = VOLTAGE_NOMINAL + random.gauss(0, 3) - (surge_pct * 0.15)
    current = (total * 1000) / (voltage * 1.732)  # 3-phase I = P / (V√3)
    return round(labs, 2), round(hostels, 2), round(canteen, 2), round(total, 2), round(voltage, 1), round(current, 1)


# ─────────────────────────────────────────────
# Sidebar Controls
# ─────────────────────────────────────────────
role = st.session_state.role
perms = USER_ROLES[role]

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/lightning-bolt.png", width=48)
    st.markdown("## VoltGuard AI")
    st.caption(f"**{st.session_state.username}** · {perms['label']}")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.role = "guest"
        st.rerun()
    st.divider()

    # Surge control — admin & faculty only
    if perms["can_surge"]:
        surge_pct = st.slider("⚡ Campus Load Surge (%)", 0, 100, 0, 5,
                               help="Simulate increased demand across all zones.")
    else:
        surge_pct = 0
        st.markdown("⚡ Campus Load Surge: **Locked** _(read-only)_")
    st.divider()

    # Grid limit adjustment — admin only
    if perms["can_adjust_grid_limit"]:
        grid_limit_override = st.slider("🔧 Grid Limit (kW)", 40, 120, int(GRID_LIMIT_KW), 5,
                                         help="Admin override for the grid trip threshold.")
    else:
        grid_limit_override = GRID_LIMIT_KW

    st.markdown("### Virtual Relay Status")
    for name, kw in NON_ESSENTIAL:
        tripped = name in st.session_state.tripped_relays
        status = f'<span class="relay-off">TRIPPED</span>' if tripped else f'<span class="relay-on">ONLINE</span>'
        st.markdown(f"• {name} ({kw} kW) — {status}", unsafe_allow_html=True)

    # Manual relay override — admin & faculty
    if perms["can_override_relays"]:
        st.divider()
        st.markdown("### 🔧 Manual Relay Override")
        override_cols = st.columns(2)
        with override_cols[0]:
            if st.button("Trip All", use_container_width=True):
                for name, kw in NON_ESSENTIAL:
                    st.session_state.tripped_relays.add(name)
                now_ts = datetime.datetime.now().strftime("%H:%M:%S")
                st.session_state.logs.insert(0,
                    f"🟠 {now_ts} — MANUAL OVERRIDE by {st.session_state.username}: All non-essential relays tripped.")
                st.rerun()
        with override_cols[1]:
            if st.button("Restore All", use_container_width=True):
                st.session_state.tripped_relays.clear()
                now_ts = datetime.datetime.now().strftime("%H:%M:%S")
                st.session_state.logs.insert(0,
                    f"🟢 {now_ts} — MANUAL RESTORE by {st.session_state.username}: All relays back online.")
                st.rerun()

        st.caption("Toggle individual relays:")
        for name, kw in NON_ESSENTIAL:
            is_on = name not in st.session_state.tripped_relays
            if st.checkbox(name, value=is_on, key=f"relay_{name}"):
                st.session_state.tripped_relays.discard(name)
            else:
                st.session_state.tripped_relays.add(name)

    st.divider()
    auto_refresh = st.toggle("Auto-refresh (1 s)", value=True)

# ─────────────────────────────────────────────
# Generate tick data
# ─────────────────────────────────────────────
st.session_state.tick += 1
labs, hostels, canteen, total, voltage, current = generate_load(st.session_state.tick, surge_pct)

now_str = datetime.datetime.now().strftime("%H:%M:%S")
h = st.session_state.history
h["time"].append(now_str)
h["labs"].append(labs)
h["hostels"].append(hostels)
h["canteen"].append(canteen)
h["total"].append(total)
h["voltage"].append(voltage)
h["current"].append(current)

# Keep last 60 data points
MAX_PTS = 60
for k in h:
    h[k] = h[k][-MAX_PTS:]

# ─────────────────────────────────────────────
# Automated Load Shedding Logic
# ─────────────────────────────────────────────
effective_load = total
shed_this_tick = 0.0

active_limit = grid_limit_override

if total > active_limit:
    excess = total - active_limit
    for name, kw in NON_ESSENTIAL:
        if name not in st.session_state.tripped_relays and excess > 0:
            st.session_state.tripped_relays.add(name)
            excess -= kw
            shed_this_tick += kw
            st.session_state.logs.insert(0,
                f"🔴 {now_str} — SURGE {total:.1f} kW — Tripping '{name}' (−{kw} kW)")
    if shed_this_tick > 0:
        st.session_state.logs.insert(0,
            f"🟡 {now_str} — Load shedding saved {shed_this_tick:.1f} kW. Essential loads protected.")
    effective_load = total - sum(kw for n, kw in NON_ESSENTIAL if n in st.session_state.tripped_relays)
else:
    if total < active_limit * 0.9 and st.session_state.tripped_relays:
        restored = list(st.session_state.tripped_relays)
        st.session_state.tripped_relays.clear()
        st.session_state.logs.insert(0,
            f"🟢 {now_str} — Load normalised ({total:.1f} kW). Relays restored: {', '.join(restored)}")

st.session_state.total_savings_kwh += shed_this_tick * (1 / 3600)  # per-second approx
st.session_state.logs = st.session_state.logs[:80]  # cap log length

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("# ⚡ VoltGuard AI — Digital Twin Dashboard")
st.caption("Real-time power grid simulation for Aravali College of Engineering & Management")

# ─────────────────────────────────────────────
# Metric Cards
# ─────────────────────────────────────────────
health_pct = max(0, 100 - (max(0, total - active_limit) / active_limit) * 100)
health_class = "status-ok" if health_pct > 70 else ("status-warn" if health_pct > 40 else "status-crit")
load_class = "status-ok" if total < active_limit * 0.85 else ("status-warn" if total < active_limit else "status-crit")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value {load_class}">{effective_load:.1f} kW</div>
        <div class="metric-label">Effective Load</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{voltage:.0f} V / {current:.0f} A</div>
        <div class="metric-label">Bus Voltage / Current</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{st.session_state.total_savings_kwh:.3f} kWh</div>
        <div class="metric-label">Total Energy Saved</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value {health_class}">{health_pct:.0f}%</div>
        <div class="metric-label">Grid Health</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# ─────────────────────────────────────────────
# Live Power Chart
# ─────────────────────────────────────────────
col_chart, col_right = st.columns([3, 2])

with col_chart:
    st.markdown("### 📈 Live Power Consumption")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=h["time"], y=h["labs"], name="Labs", line=dict(color="#42a5f5", width=2)))
    fig.add_trace(go.Scatter(x=h["time"], y=h["hostels"], name="Hostels", line=dict(color="#ab47bc", width=2)))
    fig.add_trace(go.Scatter(x=h["time"], y=h["canteen"], name="Canteen", line=dict(color="#66bb6a", width=2)))
    fig.add_trace(go.Scatter(x=h["time"], y=h["total"], name="Total", line=dict(color="#ef5350", width=3, dash="dot")))
    fig.add_hline(y=active_limit, line_dash="dash", line_color="#ff9800",
                  annotation_text=f"Grid Limit ({active_limit:.0f} kW)", annotation_font_color="#ff9800")
    fig.update_layout(**PLOTLY_LAYOUT, height=370, yaxis_title="Power (kW)")
    st.plotly_chart(fig, use_container_width=True, key="power_chart")

with col_right:
    st.markdown("### 🔍 NILM Signature Analysis")
    st.caption("How VoltGuard AI distinguishes load types by their electrical fingerprint.")

    # Simulate one cycle of an AC waveform for two load types
    t_wave = np.linspace(0, 2 * np.pi, 200)
    v_wave = 325 * np.sin(t_wave)

    # Resistive load (heater): current in-phase with voltage
    i_resistive = 12 * np.sin(t_wave)
    # Inductive load (motor): current lags voltage by ~60°
    i_inductive = 10 * np.sin(t_wave - np.pi / 3)

    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         subplot_titles=("Resistive Load (Heater) — PF ≈ 1.0",
                                         "Inductive Load (AC Motor) — PF ≈ 0.5"),
                         vertical_spacing=0.18)
    fig2.add_trace(go.Scatter(x=t_wave, y=v_wave, name="Voltage", line=dict(color="#ffca28", width=1.5)), row=1, col=1)
    fig2.add_trace(go.Scatter(x=t_wave, y=i_resistive * 20, name="Current (×20)", line=dict(color="#26c6da", width=2)), row=1, col=1)
    fig2.add_trace(go.Scatter(x=t_wave, y=v_wave, name="Voltage", line=dict(color="#ffca28", width=1.5), showlegend=False), row=2, col=1)
    fig2.add_trace(go.Scatter(x=t_wave, y=i_inductive * 20, name="Current (×20)", line=dict(color="#ef5350", width=2)), row=2, col=1)
    fig2.update_layout(**{**PLOTLY_LAYOUT, "margin": dict(l=40, r=20, t=40, b=20)}, height=370)
    fig2.update_xaxes(showticklabels=False)
    fig2.update_yaxes(title_text="Amplitude", row=1, col=1)
    st.plotly_chart(fig2, use_container_width=True, key="nilm_chart")

# ─────────────────────────────────────────────
# Zone Breakdown & Log
# ─────────────────────────────────────────────
col_bar, col_log = st.columns([1, 1])

with col_bar:
    st.markdown("### 🏢 Zone Breakdown")
    fig3 = go.Figure(go.Bar(
        x=[labs, hostels, canteen],
        y=["Labs", "Hostels", "Canteen"],
        orientation="h",
        marker_color=["#42a5f5", "#ab47bc", "#66bb6a"],
        text=[f"{v:.1f} kW" for v in [labs, hostels, canteen]],
        textposition="auto",
    ))
    fig3.update_layout(**{**PLOTLY_LAYOUT, "yaxis": dict(gridcolor="rgba(0,0,0,0)")}, height=250, xaxis_title="Power (kW)")
    st.plotly_chart(fig3, use_container_width=True, key="bar_chart")

with col_log:
    st.markdown("### 📋 AI Decision Log")
    if not st.session_state.logs:
        log_html = '<span style="color:#4a5568;">Waiting for events…</span>'
    else:
        log_html = "<br>".join(st.session_state.logs[:20])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Auto-refresh
# ─────────────────────────────────────────────
if auto_refresh:
    time.sleep(1)
    st.rerun()
