import os
from datetime import datetime
import math

from nicegui import app, ui

# =========================================================
# PHYSICS LAB AI CONFIGURATION
# =========================================================

APP_NAME = "Physics Lab AI"

# Serve assets folder (Ensure 'logo.jpg' and 'Banner_2.jpg' exist in 'assets/')
app.add_static_files("/assets", "assets")

# Dark mode controller
dark_mode = ui.dark_mode(True)

# Navigation History Stack
navigation_history = []
current_view = None

# Global Storage for Saved Experiments
SAVED_LABS = [
    {
        "id": 1,
        "title": "Projectile Launch Analysis",
        "category": "Kinematics",
        "date": "2026-09-24",
        "notes": "Tested max range at 45 degree angle with 25 m/s initial speed.",
        "params": "v0=25 m/s, angle=45°, g=9.81 m/s²"
    }
]


# =========================================================
# TIME GREETING
# =========================================================

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"


# =========================================================
# GLOBAL CSS
# =========================================================

ui.add_head_html("""
<style>
    * {
        box-sizing: border-box;
    }

    html, body {
        margin: 0;
        min-height: 100vh;
        font-family: Arial, Helvetica, sans-serif;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("/assets/Banner_2.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        z-index: -2;
        transition: opacity 0.3s ease;
    }

    body::after {
        content: "";
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
        transition: background 0.3s ease;
    }

    body.body--dark {
        background-color: #020617 !important;
        color: #ffffff !important;
    }

    body.body--dark::before { opacity: 0.35; }

    body.body--dark::after {
        background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.15), transparent 40%),
                    radial-gradient(circle at bottom left, rgba(14, 165, 233, 0.10), transparent 40%),
                    rgba(2, 6, 23, 0.75);
    }

    body.body--dark .glass-card {
        background: rgba(15, 23, 42, 0.82) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(148, 163, 184, 0.18);
        color: #ffffff !important;
    }

    body.body--dark .topbar {
        background: rgba(2, 6, 23, 0.88) !important;
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }

    body.body--dark .physics-sidebar {
        background: rgba(2, 6, 23, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(148, 163, 184, 0.15);
    }

    body.body--dark .text-muted { color: #94a3b8 !important; }

    body.body--light {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    body.body--light::before { opacity: 0.15; }

    body.body--light::after {
        background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.08), transparent 40%),
                    rgba(248, 250, 252, 0.85);
    }

    body.body--light .glass-card {
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        color: #0f172a !important;
    }

    body.body--light .topbar {
        background: rgba(255, 255, 255, 0.90) !important;
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
    }

    body.body--light .physics-sidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(226, 232, 240, 0.8);
    }

    body.body--light .text-muted { color: #64748b !important; }

    .physics-main { max-width: 1400px; margin: auto; }

    .action-card {
        cursor: pointer;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .action-card:hover {
        transform: translateY(-4px);
        border-color: rgba(59, 130, 246, 0.5) !important;
    }

    .system-ready {
        background: rgba(34, 197, 94, 0.16) !important;
        color: #22c55e !important;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    .nav-button {
        width: 100%;
        justify-content: flex-start !important;
        border-radius: 10px !important;
        margin-top: 2px;
        margin-bottom: 2px;
        transition: background 0.2s ease, transform 0.2s ease;
    }

    .nav-button:hover { transform: translateX(3px); }

    .app-logo-img {
        height: 36px;
        width: auto;
        object-fit: contain;
        border-radius: 6px;
    }

    .canvas-box {
        background: #090d16;
        border: 1px solid #1e293b;
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""")

# =========================================================
# MAIN CONTAINER & ROUTING
# =========================================================

content = ui.column().classes("physics-main w-full min-h-screen px-4 md:px-8 py-8")

def navigate_to(func, addToHistory=True):
    global current_view
    if addToHistory and current_view and current_view != func:
        navigation_history.append(current_view)
    current_view = func
    content.clear()
    func()

def go_back():
    global current_view
    if navigation_history:
        prev_view = navigation_history.pop()
        current_view = prev_view
        content.clear()
        prev_view()
    else:
        ui.notify("Already at home page", type="info")

def page_title(title, subtitle=None):
    ui.label(title).classes("text-3xl md:text-4xl font-bold")
    if subtitle:
        ui.label(subtitle).classes("text-muted mt-1 text-base")


# =========================================================
# HOME PAGE
# =========================================================

def show_home():
    with content:
        with ui.column().classes("w-full pt-6 md:pt-12 pb-6"):
            ui.label(f"{get_greeting()}, Sir.").classes("text-blue-500 text-lg md:text-xl font-semibold mb-2")
            ui.label("Welcome to Physics Lab AI").classes("text-4xl md:text-6xl font-extrabold tracking-tight")
            ui.label("PhET & GeoGebra style interactive simulations, physics calculators, and lab experiment manager.").classes("text-muted text-base md:text-lg mt-3 max-w-2xl")

        with ui.grid(columns=1).classes("w-full md:grid-cols-2 lg:grid-cols-3 gap-5 mt-4"):
            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_simulations)):
                ui.icon("model_training").classes("text-4xl text-purple-500")
                ui.label("Interactive Simulations").classes("text-xl font-semibold mt-4")
                ui.label("PhET & GeoGebra style visual physics engines with real-time controls.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_physics_calculator)):
                ui.icon("functions").classes("text-4xl text-emerald-500")
                ui.label("Physics Calculator Suite").classes("text-xl font-semibold mt-4")
                ui.label("Calculate KE, PE, Force, Work, Momentum, Acceleration, Ohm's Law & Waves.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_experiment)):
                ui.icon("science").classes("text-4xl text-blue-500")
                ui.label("New Lab Experiment").classes("text-xl font-semibold mt-4")
                ui.label("Design, test, and save custom experimental observations.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_saved_labs)):
                ui.icon("folder").classes("text-4xl text-orange-500")
                ui.label("Saved Labs").classes("text-xl font-semibold mt-4")
                ui.label("Access and manage saved experiment records.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_ai_search)):
                ui.icon("auto_awesome").classes("text-4xl text-amber-500")
                ui.label("AI Physics Assistant").classes("text-xl font-semibold mt-4")
                ui.label("Solve complex physics problems and generate custom scenarios.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_calculator)):
                ui.icon("calculate").classes("text-4xl text-cyan-500")
                ui.label("Standard Calculator").classes("text-xl font-semibold mt-4")
                ui.label("Perform quick mathematical calculations.").classes("text-muted mt-1 text-sm")


# =========================================================
# PHET & GEOGEBRA STYLE SIMULATION MODULE
# =========================================================

def show_simulations():
    with content:
        page_title("PhET & GeoGebra Interactive Physics Visualizers", "Real-time canvas simulations with parameter inputs, validation, and live animations.")

        with ui.card().classes("glass-card w-full p-6 mt-6"):
            with ui.tabs().classes("w-full") as sim_tabs:
                proj_tab = ui.tab("1. Projectile Motion")
                pend_tab = ui.tab("2. Simple Pendulum")
                spring_tab = ui.tab("3. Spring-Mass Harmonic")
                grav_tab = ui.tab("4. Gravity & Free Fall")

            with ui.tab_panels(sim_tabs, value=proj_tab).classes("w-full bg-transparent mt-4"):

                # ---------------------------------------------
                # 1. PROJECTILE MOTION
                # ---------------------------------------------
                with ui.tab_panel(proj_tab):
                    ui.label("Projectile Motion Simulator").classes("text-2xl font-bold text-blue-400 mb-1")
                    ui.label("Adjust parameters and click 'Run Simulation' to trace projectile trajectory.").classes("text-sm text-muted mb-4")

                    with ui.grid(columns=1).classes("w-full md:grid-cols-3 gap-4 mb-4"):
                        p_v0 = ui.number(label="Initial Velocity v₀ (m/s)", value=25.0).props("outlined")
                        p_angle = ui.number(label="Launch Angle θ (°)", value=45.0).props("outlined")
                        p_g = ui.number(label="Gravity g (m/s²)", value=9.81).props("outlined")

                    err_box = ui.label().classes("text-red-400 font-semibold text-sm mb-2 hidden")
                    metrics_box = ui.label().classes("text-emerald-400 font-medium text-sm mb-4")

                    canvas_html = ui.html().classes("w-full h-80 canvas-box p-2")

                    def render_projectile():
                        v0 = p_v0.value or 0
                        ang = p_angle.value or 0
                        g = p_g.value or 0

                        # Input Validation
                        if v0 <= 0 or ang <= 0 or ang >= 90 or g <= 0:
                            err_box.text = "⚠️ Invalid Input! Please enter velocity > 0, angle between 1° and 89°, and gravity > 0."
                            err_box.classes(remove="hidden")
                            metrics_box.text = ""
                            return
                        else:
                            err_box.classes(add="hidden")

                        rad = math.radians(ang)
                        t_flight = (2 * v0 * math.sin(rad)) / g
                        max_h = ((v0 * math.sin(rad)) ** 2) / (2 * g)
                        max_r = ((v0 ** 2) * math.sin(2 * rad)) / g

                        metrics_box.text = f"Flight Time: {t_flight:.2f} s | Max Height: {max_h:.2f} m | Total Range: {max_r:.2f} m"

                        path_pts = []
                        steps = 60
                        for i in range(steps + 1):
                            t = (t_flight / steps) * i
                            x = v0 * math.cos(rad) * t
                            y = (v0 * math.sin(rad) * t) - (0.5 * g * (t ** 2))
                            cx = 30 + (x / max_r) * 440
                            cy = 260 - (y / max(max_h, 1)) * 210
                            path_pts.append(f"{cx:.1f},{cy:.1f}")

                        svg_code = f"""
                        <svg width="100%" height="100%" viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#06b6d4;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <line x1="20" y1="260" x2="480" y2="260" stroke="#475569" stroke-width="3"/>
                            <polyline points="{" ".join(path_pts)}" fill="none" stroke="url(#grad)" stroke-width="4" stroke-dasharray="6,4"/>
                            <circle cx="{path_pts[-1].split(',')[0]}" cy="{path_pts[-1].split(',')[1]}" r="8" fill="#ef4444"/>
                            <circle cx="{path_pts[0].split(',')[0]}" cy="{path_pts[0].split(',')[1]}" r="6" fill="#10b981"/>
                            <text x="30" y="275" fill="#94a3b8" font-size="12">0 m</text>
                            <text x="440" y="275" fill="#94a3b8" font-size="12">{max_r:.1f} m</text>
                        </svg>
                        """
                        canvas_html.content = svg_code

                    ui.button("▶ Run Simulation", icon="play_arrow", on_click=render_projectile).props("color=primary").classes("mt-2 mb-4")
                    render_projectile()

                # ---------------------------------------------
                # 2. SIMPLE PENDULUM
                # ---------------------------------------------
                with ui.tab_panel(pend_tab):
                    ui.label("Simple Pendulum Harmonic Visualizer").classes("text-2xl font-bold text-purple-400 mb-1")
                    ui.label("Set string length and gravity to compute oscillation metrics.").classes("text-sm text-muted mb-4")

                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4 mb-4"):
                        p_length = ui.number(label="String Length L (m)", value=2.0).props("outlined")
                        p_g_in = ui.number(label="Gravity g (m/s²)", value=9.81).props("outlined")

                    p_err = ui.label().classes("text-red-400 font-semibold text-sm mb-2 hidden")
                    p_res = ui.label().classes("text-purple-300 font-medium text-sm mb-4")

                    pend_canvas = ui.html().classes("w-full h-80 canvas-box p-2")

                    def render_pendulum():
                        L = p_length.value or 0
                        g = p_g_in.value or 0

                        if L <= 0 or g <= 0:
                            p_err.text = "⚠️ Invalid Input! Length L and Gravity g must both be positive numbers."
                            p_err.classes(remove="hidden")
                            p_res.text = ""
                            return
                        else:
                            p_err.classes(add="hidden")

                        T = 2 * math.pi * math.sqrt(L / g)
                        freq = 1 / T
                        p_res.text = f"Time Period T: {T:.3f} seconds | Oscillation Frequency f: {freq:.3f} Hz"

                        svg_code = f"""
                        <svg width="100%" height="100%" viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg">
                            <line x1="200" y1="20" x2="300" y2="20" stroke="#94a3b8" stroke-width="6"/>
                            <line x1="250" y1="20" x2="180" y2="200" stroke="#38bdf8" stroke-width="3"/>
                            <line x1="250" y1="20" x2="320" y2="200" stroke="#38bdf8" stroke-width="1" stroke-dasharray="4,4"/>
                            <circle cx="180" cy="200" r="18" fill="#a855f7"/>
                            <path d="M 180 225 Q 250 240 320 225" stroke="#f43f5e" stroke-width="2" fill="none"/>
                            <text x="210" y="260" fill="#cbd5e1" font-size="13">Period T = {T:.2f} s</text>
                        </svg>
                        """
                        pend_canvas.content = svg_code

                    ui.button("▶ Run Simulation", icon="play_arrow", on_click=render_pendulum).props("color=purple").classes("mt-2 mb-4")
                    render_pendulum()

                # ---------------------------------------------
                # 3. SPRING-MASS SYSTEM
                # ---------------------------------------------
                with ui.tab_panel(spring_tab):
                    ui.label("Spring-Mass Oscillator").classes("text-2xl font-bold text-emerald-400 mb-1")
                    ui.label("Simulate Hooke's law oscillations.").classes("text-sm text-muted mb-4")

                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4 mb-4"):
                        sm_m = ui.number(label="Mass m (kg)", value=2.0).props("outlined")
                        sm_k = ui.number(label="Spring Constant k (N/m)", value=50.0).props("outlined")

                    sm_err = ui.label().classes("text-red-400 font-semibold text-sm mb-2 hidden")
                    sm_res = ui.label().classes("text-emerald-300 font-medium text-sm mb-4")

                    spring_canvas = ui.html().classes("w-full h-80 canvas-box p-2")

                    def render_spring():
                        m = sm_m.value or 0
                        k = sm_k.value or 0

                        if m <= 0 or k <= 0:
                            sm_err.text = "⚠️ Invalid Input! Mass m and Spring Constant k must be positive values."
                            sm_err.classes(remove="hidden")
                            sm_res.text = ""
                            return
                        else:
                            sm_err.classes(add="hidden")

                        omega = math.sqrt(k / m)
                        T = 2 * math.pi / omega
                        sm_res.text = f"Angular Frequency ω: {omega:.2f} rad/s | Oscillation Period T: {T:.3f} s"

                        svg_code = f"""
                        <svg width="100%" height="100%" viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg">
                            <rect x="20" y="20" width="15" height="240" fill="#475569"/>
                            <polyline points="35,140 60,120 80,160 100,120 120,160 140,120 160,160 180,120 200,160 220,140" fill="none" stroke="#10b981" stroke-width="4"/>
                            <rect x="220" y="100" width="80" height="80" fill="#059669" rx="8"/>
                            <text x="248" y="145" fill="#ffffff" font-weight="bold" font-size="16">{m}kg</text>
                            <line x1="35" y1="200" x2="450" y2="200" stroke="#334155" stroke-width="2"/>
                            <text x="320" y="145" fill="#34d399" font-size="14">k = {k} N/m</text>
                        </svg>
                        """
                        spring_canvas.content = svg_code

                    ui.button("▶ Run Simulation", icon="play_arrow", on_click=render_spring).props("color=emerald").classes("mt-2 mb-4")
                    render_spring()

                # ---------------------------------------------
                # 4. GRAVITY & FREE FALL
                # ---------------------------------------------
                with ui.tab_panel(grav_tab):
                    ui.label("Gravity & Free Fall Visualizer").classes("text-2xl font-bold text-amber-400 mb-1")
                    ui.label("Calculate drop duration and velocity upon impact.").classes("text-sm text-muted mb-4")

                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4 mb-4"):
                        ff_h = ui.number(label="Drop Height h (m)", value=45.0).props("outlined")
                        ff_g = ui.number(label="Gravity g (m/s²)", value=9.81).props("outlined")

                    ff_err = ui.label().classes("text-red-400 font-semibold text-sm mb-2 hidden")
                    ff_res = ui.label().classes("text-amber-300 font-medium text-sm mb-4")

                    ff_canvas = ui.html().classes("w-full h-80 canvas-box p-2")

                    def render_freefall():
                        h = ff_h.value or 0
                        g = ff_g.value or 0

                        if h <= 0 or g <= 0:
                            ff_err.text = "⚠️ Invalid Input! Height h and Gravity g must be positive values."
                            ff_err.classes(remove="hidden")
                            ff_res.text = ""
                            return
                        else:
                            ff_err.classes(add="hidden")

                        t_fall = math.sqrt((2 * h) / g)
                        v_final = g * t_fall
                        ff_res.text = f"Fall Duration: {t_fall:.2f} seconds | Final Velocity at Impact: {v_final:.2f} m/s"

                        svg_code = f"""
                        <svg width="100%" height="100%" viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg">
                            <line x1="50" y1="240" x2="450" y2="240" stroke="#f59e0b" stroke-width="4"/>
                            <line x1="150" y1="40" x2="150" y2="240" stroke="#475569" stroke-width="2" stroke-dasharray="4,4"/>
                            <circle cx="150" cy="50" r="14" fill="#fbbf24"/>
                            <circle cx="150" cy="226" r="14" fill="#ef4444" opacity="0.6"/>
                            <text x="180" y="140" fill="#fcd34d" font-size="14">Height h = {h} m</text>
                            <text x="180" y="165" fill="#94a3b8" font-size="13">Impact v = {v_final:.1f} m/s</text>
                        </svg>
                        """
                        ff_canvas.content = svg_code

                    ui.button("▶ Run Simulation", icon="play_arrow", on_click=render_freefall).props("color=warning").classes("mt-2 mb-4")
                    render_freefall()


# =========================================================
# EXPANDED PHYSICS CALCULATOR SUITE WITH VALIDATION
# =========================================================

def show_physics_calculator():
    with content:
        page_title("Physics Calculator Suite", "Comprehensive physics equations with error validation.")

        with ui.card().classes("glass-card w-full p-6 mt-6"):
            with ui.tabs().classes("w-full") as calc_tabs:
                ke_tab = ui.tab("Kinetic Energy")
                pe_tab = ui.tab("Potential Energy")
                acc_tab = ui.tab("Acceleration")
                force_tab = ui.tab("Force & Work")
                p_tab = ui.tab("Momentum")
                ohm_tab = ui.tab("Ohm's Law")
                wave_tab = ui.tab("Wave Speed")
                press_tab = ui.tab("Pressure")

            with ui.tab_panels(calc_tabs, value=ke_tab).classes("w-full bg-transparent mt-4"):

                # Kinetic Energy
                with ui.tab_panel(ke_tab):
                    ui.label("Formula: KE = ½ × m × v²").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        ke_m = ui.number(label="Mass (kg)", value=10.0).props("outlined")
                        ke_v = ui.number(label="Velocity (m/s)", value=5.0).props("outlined")
                    ke_out = ui.label("Kinetic Energy: 125.00 Joules (J)").classes("text-xl font-bold text-emerald-400 mt-4")

                    def c_ke():
                        m, v = ke_m.value or 0, ke_v.value or 0
                        if m < 0:
                            ke_out.text = "⚠️ Error: Mass cannot be negative!"
                            ke_out.classes(replace="text-red-400")
                        else:
                            ke_out.text = f"Kinetic Energy: {(0.5 * m * (v ** 2)):.2f} Joules (J)"
                            ke_out.classes(replace="text-emerald-400")
                    ui.button("Calculate", icon="bolt", on_click=c_ke).props("color=primary").classes("mt-2")

                # Potential Energy
                with ui.tab_panel(pe_tab):
                    ui.label("Formula: PE = m × g × h").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-3 gap-4"):
                        pe_m = ui.number(label="Mass (kg)", value=10.0).props("outlined")
                        pe_g = ui.number(label="Gravity (m/s²)", value=9.81).props("outlined")
                        pe_h = ui.number(label="Height (m)", value=15.0).props("outlined")
                    pe_out = ui.label("Potential Energy: 1471.50 Joules (J)").classes("text-xl font-bold text-emerald-400 mt-4")

                    def c_pe():
                        m, g, h = pe_m.value or 0, pe_g.value or 0, pe_h.value or 0
                        if m < 0 or h < 0:
                            pe_out.text = "⚠️ Error: Mass and Height cannot be negative!"
                            pe_out.classes(replace="text-red-400")
                        else:
                            pe_out.text = f"Potential Energy: {(m * g * h):.2f} Joules (J)"
                            pe_out.classes(replace="text-emerald-400")
                    ui.button("Calculate", icon="bolt", on_click=c_pe).props("color=primary").classes("mt-2")

                # Acceleration
                with ui.tab_panel(acc_tab):
                    ui.label("Formula: a = (v - u) / t").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-3 gap-4"):
                        a_v = ui.number(label="Final Velocity v (m/s)", value=30.0).props("outlined")
                        a_u = ui.number(label="Initial Velocity u (m/s)", value=10.0).props("outlined")
                        a_t = ui.number(label="Time t (s)", value=5.0).props("outlined")
                    acc_out = ui.label("Acceleration: 4.00 m/s²").classes("text-xl font-bold text-blue-400 mt-4")

                    def c_acc():
                        v, u, t = a_v.value or 0, a_u.value or 0, a_t.value or 0
                        if t <= 0:
                            acc_out.text = "⚠️ Error: Time must be strictly greater than 0!"
                            acc_out.classes(replace="text-red-400")
                        else:
                            acc_out.text = f"Acceleration: {((v - u) / t):.2f} m/s²"
                            acc_out.classes(replace="text-blue-400")
                    ui.button("Calculate", icon="speed", on_click=c_acc).props("color=primary").classes("mt-2")

                # Force & Work
                with ui.tab_panel(force_tab):
                    ui.label("Formulas: Force F = m × a | Work W = F × d").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-3 gap-4"):
                        f_m = ui.number(label="Mass (kg)", value=12.0).props("outlined")
                        f_a = ui.number(label="Acceleration (m/s²)", value=2.5).props("outlined")
                        f_d = ui.number(label="Displacement (m)", value=10.0).props("outlined")
                    fw_out = ui.label("Force: 30.00 N | Work: 300.00 J").classes("text-xl font-bold text-cyan-400 mt-4")

                    def c_fw():
                        m, a, d = f_m.value or 0, f_a.value or 0, f_d.value or 0
                        if m < 0:
                            fw_out.text = "⚠️ Error: Mass cannot be negative!"
                            fw_out.classes(replace="text-red-400")
                        else:
                            f = m * a
                            w = f * d
                            fw_out.text = f"Force: {f:.2f} N | Work Done: {w:.2f} J"
                            fw_out.classes(replace="text-cyan-400")
                    ui.button("Calculate", icon="fitness_center", on_click=c_fw).props("color=primary").classes("mt-2")

                # Momentum
                with ui.tab_panel(p_tab):
                    ui.label("Formula: p = m × v").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        p_m = ui.number(label="Mass (kg)", value=15.0).props("outlined")
                        p_v = ui.number(label="Velocity (m/s)", value=4.0).props("outlined")
                    p_out = ui.label("Momentum: 60.00 kg·m/s").classes("text-xl font-bold text-purple-400 mt-4")

                    def c_p():
                        m, v = p_m.value or 0, p_v.value or 0
                        if m < 0:
                            p_out.text = "⚠️ Error: Mass cannot be negative!"
                            p_out.classes(replace="text-red-400")
                        else:
                            p_out.text = f"Momentum: {(m * v):.2f} kg·m/s"
                            p_out.classes(replace="text-purple-400")
                    ui.button("Calculate", icon="trending_up", on_click=c_p).props("color=primary").classes("mt-2")

                # Ohm's Law
                with ui.tab_panel(ohm_tab):
                    ui.label("Formula: V = I × R").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        o_i = ui.number(label="Current I (Amperes)", value=2.5).props("outlined")
                        o_r = ui.number(label="Resistance R (Ohms)", value=10.0).props("outlined")
                    ohm_out = ui.label("Voltage V: 25.00 Volts (V)").classes("text-xl font-bold text-amber-400 mt-4")

                    def c_ohm():
                        i, r = o_i.value or 0, o_r.value or 0
                        if r < 0:
                            ohm_out.text = "⚠️ Error: Resistance cannot be negative!"
                            ohm_out.classes(replace="text-red-400")
                        else:
                            ohm_out.text = f"Voltage V: {(i * r):.2f} Volts (V)"
                            ohm_out.classes(replace="text-amber-400")
                    ui.button("Calculate", icon="power", on_click=c_ohm).props("color=primary").classes("mt-2")

                # Wave Speed
                with ui.tab_panel(wave_tab):
                    ui.label("Formula: v = f × λ").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        w_f = ui.number(label="Frequency f (Hz)", value=440.0).props("outlined")
                        w_l = ui.number(label="Wavelength λ (m)", value=0.77).props("outlined")
                    wave_out = ui.label("Wave Speed v: 338.80 m/s").classes("text-xl font-bold text-pink-400 mt-4")

                    def c_wave():
                        f, l = w_f.value or 0, w_l.value or 0
                        if f <= 0 or l <= 0:
                            wave_out.text = "⚠️ Error: Frequency and Wavelength must be positive!"
                            wave_out.classes(replace="text-red-400")
                        else:
                            wave_out.text = f"Wave Speed v: {(f * l):.2f} m/s"
                            wave_out.classes(replace="text-pink-400")
                    ui.button("Calculate", icon="waves", on_click=c_wave).props("color=primary").classes("mt-2")

                # Pressure
                with ui.tab_panel(press_tab):
                    ui.label("Formula: P = F / A").classes("text-sm text-muted mb-4")
                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        pr_f = ui.number(label="Force F (N)", value=500.0).props("outlined")
                        pr_a = ui.number(label="Area A (m²)", value=2.0).props("outlined")
                    press_out = ui.label("Pressure P: 250.00 Pascals (Pa)").classes("text-xl font-bold text-indigo-400 mt-4")

                    def c_press():
                        f, a = pr_f.value or 0, pr_a.value or 0
                        if a <= 0:
                            press_out.text = "⚠️ Error: Area must be strictly greater than 0!"
                            press_out.classes(replace="text-red-400")
                        else:
                            press_out.text = f"Pressure P: {(f / a):.2f} Pascals (Pa)"
                            press_out.classes(replace="text-indigo-400")
                    ui.button("Calculate", icon="compress", on_click=c_press).props("color=primary").classes("mt-2")


# =========================================================
# EXPERIMENT & SAVED LABS ENGINE
# =========================================================

def show_experiment():
    with content:
        page_title("New Lab Experiment", "Set parameters, record observations, and save your experiments.")

        with ui.card().classes("glass-card w-full p-6 mt-6"):
            exp_title = ui.input(label="Experiment Title", placeholder="e.g. Free Fall Acceleration Test").props("outlined").classes("w-full mb-3")
            exp_category = ui.select(["Kinematics", "Dynamics", "Optics", "Thermodynamics", "Electromagnetism"], value="Kinematics", label="Category").props("outlined").classes("w-full mb-3")
            exp_params = ui.input(label="Test Parameters / Variables", placeholder="e.g. Height = 50m, Mass = 5kg").props("outlined").classes("w-full mb-3")
            exp_notes = ui.textarea(label="Observations & Results", placeholder="Enter experimental findings...").props("outlined").classes("w-full mb-4")

            def save_experiment_record():
                if not exp_title.value.strip():
                    ui.notify("Please enter an experiment title!", type="warning")
                    return

                new_entry = {
                    "id": len(SAVED_LABS) + 1,
                    "title": exp_title.value,
                    "category": exp_category.value,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "notes": exp_notes.value or "No notes provided.",
                    "params": exp_params.value or "N/A"
                }
                SAVED_LABS.append(new_entry)
                ui.notify(f"Experiment '{exp_title.value}' saved successfully!", type="positive")
                navigate_to(show_saved_labs)

            ui.button("💾 Save Experiment to Labs", icon="save", on_click=save_experiment_record).props("color=primary").classes("mt-2")


def show_saved_labs():
    with content:
        page_title("Saved Labs", "Review saved experiment logs and records.")

        if not SAVED_LABS:
            with ui.card().classes("glass-card w-full p-8 mt-6 items-center justify-center text-center"):
                ui.icon("folder_open").classes("text-6xl text-orange-400")
                ui.label("No Saved Labs Found").classes("text-xl font-semibold mt-4")
                ui.button("Create First Experiment", icon="add", on_click=lambda: navigate_to(show_experiment)).props("color=primary").classes("mt-4")
        else:
            with ui.column().classes("w-full gap-4 mt-6"):
                for lab in SAVED_LABS:
                    with ui.card().classes("glass-card w-full p-5"):
                        with ui.row().classes("w-full items-center justify-between"):
                            ui.label(lab["title"]).classes("text-xl font-bold text-blue-400")
                            ui.badge(lab["category"]).props("color=blue").classes("text-xs")

                        ui.label(f"📅 Date: {lab['date']} | Parameters: {lab['params']}").classes("text-xs text-muted mt-1")
                        ui.label(f"Observations: {lab['notes']}").classes("text-sm mt-3")


# =========================================================
# OTHER PAGES
# =========================================================

def show_calculator():
    with content:
        page_title("Standard Calculator", "Quick mathematical computations.")
        with ui.card().classes("glass-card w-full max-w-sm p-5 mt-6"):
            display = ui.input(value="").props("outlined readonly").classes("w-full text-right text-2xl font-bold")
            def add_val(v): display.value = str(display.value) + str(v)
            def clear_calc(): display.value = ""
            def compute():
                try: display.value = str(eval(str(display.value), {"__builtins__": {}}, {}))
                except Exception: display.value = "Error"

            btns = [["7", "8", "9", "/"], ["4", "5", "6", "*"], ["1", "2", "3", "-"], ["0", ".", "%", "+"]]
            with ui.column().classes("w-full gap-2 mt-4"):
                for row in btns:
                    with ui.row().classes("w-full gap-2"):
                        for b in row:
                            ui.button(b, on_click=lambda val=b: add_val(val)).props("outline").classes("flex-1 text-lg")
                with ui.row().classes("w-full gap-2 mt-2"):
                    ui.button("C", on_click=clear_calc).props("color=negative").classes("flex-1")
                    ui.button("=", on_click=compute).props("color=primary").classes("flex-1")

def show_ai_search():
    with content:
        page_title("AI Physics Assistant", "AI-driven physics scenario generator and concept solver.")
        with ui.card().classes("glass-card w-full p-6 mt-6"):
            ui.textarea(placeholder="Ask any physics question or request a custom scenario simulation...").props("outlined").classes("w-full")
            ui.button("Ask Assistant", icon="auto_awesome").props("color=primary").classes("mt-4").on(
                "click", lambda: ui.notify("AI response processing...", type="info")
            )

def show_settings():
    with content:
        page_title("Settings", "Customise interface preferences.")
        with ui.card().classes("glass-card w-full p-6 mt-6"):
            ui.switch("Dark Theme Mode", value=dark_mode.value, on_change=lambda e: dark_mode.set_value(e.value))


# =========================================================
# LAYOUT COMPONENTS
# =========================================================

drawer = ui.left_drawer(value=True).props("swipeable").classes("physics-sidebar w-64")

with drawer:
    with ui.column().classes("w-full px-4 pt-5 pb-4"):
        with ui.row().classes("w-full items-center gap-3"):
            ui.image("/assets/logo.jpg").classes("app-logo-img")
            with ui.column().classes("gap-0"):
                ui.label(APP_NAME).classes("text-lg font-bold")
                ui.label("Simulation Platform").classes("text-xs text-muted")

    ui.separator().classes("opacity-20")

    with ui.column().classes("w-full px-3 py-4"):
        ui.label("WORKSPACE").classes("text-xs text-muted px-2 mb-2 font-bold tracking-wider")
        ui.button("Home", icon="home", on_click=lambda: navigate_to(show_home)).props("flat").classes("nav-button")
        ui.button("Simulations", icon="model_training", on_click=lambda: navigate_to(show_simulations)).props("flat").classes("nav-button")
        ui.button("New Experiment", icon="science", on_click=lambda: navigate_to(show_experiment)).props("flat").classes("nav-button")

        ui.separator().classes("opacity-10 my-3")

        ui.label("TOOLS").classes("text-xs text-muted px-2 mb-2 font-bold tracking-wider")
        ui.button("Physics Calculator", icon="functions", on_click=lambda: navigate_to(show_physics_calculator)).props("flat").classes("nav-button")
        ui.button("Calculator", icon="calculate", on_click=lambda: navigate_to(show_calculator)).props("flat").classes("nav-button")
        ui.button("Saved Labs", icon="folder", on_click=lambda: navigate_to(show_saved_labs)).props("flat").classes("nav-button")
        ui.button("AI Assistant", icon="search", on_click=lambda: navigate_to(show_ai_search)).props("flat").classes("nav-button")

        ui.separator().classes("opacity-10 my-3")
        ui.button("Settings", icon="settings", on_click=lambda: navigate_to(show_settings)).props("flat").classes("nav-button")

with ui.header().classes("topbar items-center px-3 md:px-5"):
    ui.button(icon="menu", on_click=drawer.toggle).props("flat round").classes("text-current")
    with ui.row().classes("items-center gap-2 ml-2"):
        ui.image("/assets/logo.jpg").classes("app-logo-img")
        ui.label(APP_NAME).classes("text-lg md:text-xl font-semibold")

    ui.button("BACK", icon="arrow_back", on_click=go_back).props("flat dense").classes("text-current ml-4 text-xs font-bold")
    ui.space()

    with ui.column().classes("items-end gap-0 py-1"):
        ui.badge("● SYSTEM READY").classes("system-ready text-xs px-2 py-0.5 rounded-full font-medium")
        ui.label("MADE BY ISHAN SHARMA").classes("text-[10px] text-muted font-bold tracking-wider mt-1 uppercase")

navigate_to(show_home, addToHistory=False)

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8080"))
    ui.run(host="0.0.0.0", port=port, reload=False, title=APP_NAME)
