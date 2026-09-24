import os
from datetime import datetime
import math

from nicegui import app, ui

# =========================================================
# PHYSICS LAB AI CONFIGURATION
# =========================================================

APP_NAME = "Physics Lab AI"

# Serve assets folder
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
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .action-card:hover {
        transform: translateY(-2px);
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

    .sim-canvas {
        width: 100%;
        height: 380px;
        background-color: #090d16;
        border: 1px solid #1e293b;
        border-radius: 12px;
    }
</style>
""")

# =========================================================
# MAIN CONTAINER & ROUTING
# =========================================================

content = ui.column().classes("physics-main w-full min-h-screen px-4 md:px-8 py-8")

def navigate_to(func, addToHistory=True, *args, **kwargs):
    global current_view
    if addToHistory and current_view:
        navigation_history.append(current_view)
    current_view = lambda: func(*args, **kwargs)
    content.clear()
    func(*args, **kwargs)

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
            ui.label("Interactive physics simulations, real-time 2D animated models, calculators, and lab experiment manager.").classes("text-muted text-base md:text-lg mt-3 max-w-2xl")

        with ui.grid(columns=1).classes("w-full md:grid-cols-2 lg:grid-cols-3 gap-5 mt-4"):
            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", lambda: navigate_to(show_simulations)):
                ui.icon("model_training").classes("text-4xl text-purple-500")
                ui.label("Physics Lab AI Simulations").classes("text-xl font-semibold mt-4")
                ui.label("Interactive visual 2D motion models with vector overlays and controls.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", lambda: navigate_to(show_physics_calculator)):
                ui.icon("functions").classes("text-4xl text-emerald-500")
                ui.label("Physics Calculator Suite").classes("text-xl font-semibold mt-4")
                ui.label("Calculate KE, PE, Force, Work, Momentum, Acceleration, Ohm's Law & Waves.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", lambda: navigate_to(show_experiment)):
                ui.icon("science").classes("text-4xl text-blue-500")
                ui.label("New Lab Experiment").classes("text-xl font-semibold mt-4")
                ui.label("Design, test, and save custom experimental observations.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", lambda: navigate_to(show_saved_labs)):
                ui.icon("folder").classes("text-4xl text-orange-500")
                ui.label("Saved Labs").classes("text-xl font-semibold mt-4")
                ui.label("Access and manage saved experiment records.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", lambda: navigate_to(show_ai_search)):
                ui.icon("auto_awesome").classes("text-4xl text-amber-500")
                ui.label("AI Physics Assistant").classes("text-xl font-semibold mt-4")
                ui.label("Solve complex physics problems and generate custom scenarios.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", lambda: navigate_to(show_calculator)):
                ui.icon("calculate").classes("text-4xl text-cyan-500")
                ui.label("Standard Calculator").classes("text-xl font-semibold mt-4")
                ui.label("Perform quick mathematical calculations.").classes("text-muted mt-1 text-sm")


# =========================================================
# PHYSICS LAB AI SIMULATIONS LIST VIEW
# =========================================================

def show_simulations():
    with content:
        page_title("Physics Lab AI Simulations", "Select a physics topic below and click 'Run Simulation' to start real-time interactive 2D animations.")

        simulations_list = [
            {
                "id": "projectile",
                "title": "Projectile Motion",
                "icon": "sports_baseball",
                "color": "text-blue-500",
                "description": "Simulate launch trajectory, velocity vectors, and component breakdowns (Vx & Vy) with real-time ball movement.",
                "action": lambda: navigate_to(run_projectile_simulation)
            },
            {
                "id": "pendulum",
                "title": "Simple Pendulum Oscillator",
                "icon": "swap_horizontal_circle",
                "color": "text-purple-500",
                "description": "Interactive harmonic pendulum motion with angle components, restoring force vectors, and angular velocity display.",
                "action": lambda: navigate_to(run_pendulum_simulation)
            },
            {
                "id": "spring",
                "title": "Spring-Mass Harmonic Oscillator",
                "icon": "reorder",
                "color": "text-emerald-500",
                "description": "Hooke's Law spring oscillation animation with force vectors and real-time displacement tracking.",
                "action": lambda: navigate_to(run_spring_simulation)
            },
            {
                "id": "gravity",
                "title": "Gravity & Free Fall Motion",
                "icon": "south",
                "color": "text-amber-500",
                "description": "Vertical drop simulation under gravitational acceleration with real-time velocity vector and distance counters.",
                "action": lambda: navigate_to(run_gravity_simulation)
            }
        ]

        with ui.column().classes("w-full gap-4 mt-6"):
            for sim in simulations_list:
                with ui.card().classes("glass-card action-card w-full p-6"):
                    with ui.row().classes("w-full items-center justify-between gap-4"):
                        with ui.row().classes("items-center gap-4 flex-1"):
                            ui.icon(sim["icon"]).classes(f"text-4xl {sim['color']}")
                            with ui.column().classes("gap-1"):
                                ui.label(sim["title"]).classes("text-xl font-bold")
                                ui.label(sim["description"]).classes("text-muted text-sm")
                        
                        ui.button("▶ Run Simulation", on_click=sim["action"]).props("color=primary rounded").classes("px-6 py-2 font-bold shadow-md")


# =========================================================
# 2D ANIMATED SIMULATION RUNNERS
# =========================================================

# --- 1. PROJECTILE MOTION RUNNER ---
def run_projectile_simulation():
    with content:
        with ui.row().classes("items-center justify-between w-full mb-4"):
            page_title("Projectile Motion 2D Simulation", "Adjust values, toggle vectors, and click Play to start motion.")
            ui.button("Back to List", icon="arrow_back", on_click=lambda: navigate_to(show_simulations)).props("flat color=primary")

        err_banner = ui.label().classes("text-red-400 font-bold text-sm mb-3 hidden")

        with ui.card().classes("glass-card w-full p-5 mb-4"):
            with ui.grid(columns=1).classes("w-full md:grid-cols-3 gap-4"):
                v0_in = ui.number(label="Initial Velocity v₀ (m/s)", value=30.0, min=1, max=100).props("outlined")
                ang_in = ui.number(label="Launch Angle θ (°)", value=45.0, min=1, max=89).props("outlined")
                g_in = ui.number(label="Gravity g (m/s²)", value=9.81, min=0.1, max=30).props("outlined")

            with ui.row().classes("items-center gap-6 mt-4 flex-wrap"):
                ui.label("Display Overlays:").classes("font-semibold text-sm")
                chk_v = ui.checkbox("Velocity Vector (Green)", value=True)
                chk_vx = ui.checkbox("Horizontal Vx (Cyan)", value=True)
                chk_vy = ui.checkbox("Vertical Vy (Pink)", value=True)

            with ui.row().classes("items-center gap-3 mt-4"):
                btn_play = ui.button("▶ Start", props="color=positive")
                btn_pause = ui.button("⏸ Pause", props="color=warning")
                btn_reset = ui.button("↺ Reset", props="color=negative")

        metrics_label = ui.label("Ready to launch.").classes("text-blue-400 font-semibold mb-2 text-sm")

        # HTML5 Canvas for real-time 2D Animation
        canvas_id = "projCanvas"
        ui.html(f'<canvas id="{canvas_id}" class="sim-canvas"></canvas>').classes("w-full")

        js_script = f"""
        (function() {{
            const canvas = document.getElementById('{canvas_id}');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            
            let animId = null;
            let running = false;
            let t = 0;
            const dt = 0.03;

            function resize() {{
                canvas.width = canvas.clientWidth;
                canvas.height = canvas.clientHeight;
            }}
            resize();

            window.runProj = function(v0, ang, g, showV, showVx, showVy) {{
                cancelAnimationFrame(animId);
                t = 0;
                running = true;
                const rad = ang * Math.PI / 180;
                const vx0 = v0 * Math.cos(rad);
                const vy0 = v0 * Math.sin(rad);
                const t_total = (2 * vy0) / g;
                const max_x = vx0 * t_total;
                const max_y = (vy0 * vy0) / (2 * g);

                const margin = 50;
                const scaleX = (canvas.width - 2 * margin) / Math.max(max_x, 10);
                const scaleY = (canvas.height - 2 * margin) / Math.max(max_y * 1.2, 10);
                const scale = Math.min(scaleX, scaleY);

                function draw() {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    // Draw Ground
                    ctx.beginPath();
                    ctx.moveTo(30, canvas.height - 40);
                    ctx.lineTo(canvas.width - 30, canvas.height - 40);
                    ctx.strokeStyle = '#475569';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Physics calculate
                    const x = vx0 * t;
                    const y = (vy0 * t) - (0.5 * g * t * t);
                    const current_vy = vy0 - (g * t);

                    const cx = 40 + x * scale;
                    const cy = (canvas.height - 40) - y * scale;

                    // Trajectory curve
                    ctx.beginPath();
                    for(let i=0; i<=t; i+=0.02) {{
                        let ix = vx0 * i;
                        let iy = (vy0 * i) - (0.5 * g * i * i);
                        let px = 40 + ix * scale;
                        let py = (canvas.height - 40) - iy * scale;
                        if(i===0) ctx.moveTo(px, py);
                        else ctx.lineTo(px, py);
                    }}
                    ctx.strokeStyle = 'rgba(59, 130, 246, 0.6)';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([4, 4]);
                    ctx.stroke();
                    ctx.setLineDash([]);

                    // Ball
                    if (cy <= canvas.height - 40) {{
                        ctx.beginPath();
                        ctx.arc(cx, cy, 10, 0, Math.PI * 2);
                        ctx.fillStyle = '#ef4444';
                        ctx.fill();

                        // Vectors
                        const vLen = 2.5;
                        if(showVx) {{
                            ctx.beginPath();
                            ctx.moveTo(cx, cy);
                            ctx.lineTo(cx + vx0 * vLen, cy);
                            ctx.strokeStyle = '#06b6d4';
                            ctx.lineWidth = 3;
                            ctx.stroke();
                        }}
                        if(showVy) {{
                            ctx.beginPath();
                            ctx.moveTo(cx, cy);
                            ctx.lineTo(cx, cy - current_vy * vLen);
                            ctx.strokeStyle = '#ec4899';
                            ctx.lineWidth = 3;
                            ctx.stroke();
                        }}
                        if(showV) {{
                            ctx.beginPath();
                            ctx.moveTo(cx, cy);
                            ctx.lineTo(cx + vx0 * vLen, cy - current_vy * vLen);
                            ctx.strokeStyle = '#22c55e';
                            ctx.lineWidth = 3;
                            ctx.stroke();
                        }}
                    }}

                    if (running && y >= 0) {{
                        t += dt;
                        animId = requestAnimationFrame(draw);
                    }}
                }}
                draw();
            }};

            window.pauseProj = function() {{ running = false; }};
            window.resetProj = function() {{ running = false; ctx.clearRect(0, 0, canvas.width, canvas.height); }};
        }})();
        """
        ui.run_javascript(js_script)

        def start_sim():
            v0 = v0_in.value or 0
            ang = ang_in.value or 0
            g = g_in.value or 0

            if v0 <= 0 or ang <= 0 or ang >= 90 or g <= 0:
                err_banner.text = "⚠️ Input Error: Velocity & Gravity must be positive. Angle must be between 1° and 89°."
                err_banner.classes(remove="hidden")
                return
            else:
                err_banner.classes(add="hidden")

            rad = math.radians(ang)
            t_total = (2 * v0 * math.sin(rad)) / g
            max_r = ((v0 ** 2) * math.sin(2 * rad)) / g
            max_h = ((v0 * math.sin(rad)) ** 2) / (2 * g)
            metrics_label.text = f"Flight Time: {t_total:.2f}s | Max Height: {max_h:.2f}m | Total Distance: {max_r:.2f}m"

            ui.run_javascript(f"window.runProj({v0}, {ang}, {g}, {str(chk_v.value).lower()}, {str(chk_vx.value).lower()}, {str(chk_vy.value).lower()});")

        btn_play.on("click", start_sim)
        btn_pause.on("click", lambda: ui.run_javascript("window.pauseProj();"))
        btn_reset.on("click", lambda: ui.run_javascript("window.resetProj();"))


# --- 2. PENDULUM SIMULATION RUNNER ---
def run_pendulum_simulation():
    with content:
        with ui.row().classes("items-center justify-between w-full mb-4"):
            page_title("Simple Pendulum 2D Simulation", "Adjust string length and angle to observe harmonic motion.")
            ui.button("Back to List", icon="arrow_back", on_click=lambda: navigate_to(show_simulations)).props("flat color=primary")

        err_banner = ui.label().classes("text-red-400 font-bold text-sm mb-3 hidden")

        with ui.card().classes("glass-card w-full p-5 mb-4"):
            with ui.grid(columns=1).classes("w-full md:grid-cols-3 gap-4"):
                l_in = ui.number(label="String Length L (m)", value=2.0, min=0.5, max=10).props("outlined")
                a_in = ui.number(label="Initial Angle θ (°)", value=30.0, min=5, max=80).props("outlined")
                g_in = ui.number(label="Gravity g (m/s²)", value=9.81, min=0.1, max=30).props("outlined")

            with ui.row().classes("items-center gap-6 mt-4 flex-wrap"):
                chk_v = ui.checkbox("Velocity Vector (Green)", value=True)
                chk_f = ui.checkbox("Restoring Force Vector (Pink)", value=True)

            with ui.row().classes("items-center gap-3 mt-4"):
                btn_play = ui.button("▶ Start", props="color=positive")
                btn_pause = ui.button("⏸ Pause", props="color=warning")
                btn_reset = ui.button("↺ Reset", props="color=negative")

        metrics_label = ui.label("Ready to simulate.").classes("text-purple-400 font-semibold mb-2 text-sm")
        canvas_id = "pendCanvas"
        ui.html(f'<canvas id="{canvas_id}" class="sim-canvas"></canvas>').classes("w-full")

        js_script = f"""
        (function() {{
            const canvas = document.getElementById('{canvas_id}');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            let animId = null, running = false, angle = 0, angleVel = 0, angleAccel = 0;

            window.runPend = function(L, initAngle, g, showV, showF) {{
                cancelAnimationFrame(animId);
                running = true;
                angle = initAngle * Math.PI / 180;
                angleVel = 0;
                const dt = 0.03;

                function draw() {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    const pivotX = canvas.width / 2;
                    const pivotY = 40;
                    const armLen = 200;

                    angleAccel = (-1 * g / L) * Math.sin(angle);
                    angleVel += angleAccel * dt;
                    angle += angleVel * dt;

                    const bobX = pivotX + armLen * Math.sin(angle);
                    const bobY = pivotY + armLen * Math.cos(angle);

                    // Support Roof
                    ctx.beginPath();
                    ctx.moveTo(pivotX - 50, pivotY);
                    ctx.lineTo(pivotX + 50, pivotY);
                    ctx.strokeStyle = '#94a3b8';
                    ctx.lineWidth = 4;
                    ctx.stroke();

                    // String
                    ctx.beginPath();
                    ctx.moveTo(pivotX, pivotY);
                    ctx.lineTo(bobX, bobY);
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Bob
                    ctx.beginPath();
                    ctx.arc(bobX, bobY, 18, 0, Math.PI * 2);
                    ctx.fillStyle = '#a855f7';
                    ctx.fill();

                    // Vectors
                    if(showV) {{
                        const vx = angleVel * Math.cos(angle) * 40;
                        const vy = -angleVel * Math.sin(angle) * 40;
                        ctx.beginPath();
                        ctx.moveTo(bobX, bobY);
                        ctx.lineTo(bobX + vx, bobY + vy);
                        ctx.strokeStyle = '#22c55e';
                        ctx.lineWidth = 3;
                        ctx.stroke();
                    }}

                    if(showF) {{
                        const fx = -Math.sin(angle) * 30;
                        ctx.beginPath();
                        ctx.moveTo(bobX, bobY);
                        ctx.lineTo(bobX + fx, bobY);
                        ctx.strokeStyle = '#ec4899';
                        ctx.lineWidth = 3;
                        ctx.stroke();
                    }}

                    if(running) animId = requestAnimationFrame(draw);
                }}
                draw();
            }};

            window.pausePend = function() {{ running = false; }};
            window.resetPend = function() {{ running = false; ctx.clearRect(0, 0, canvas.width, canvas.height); }};
        }})();
        """
        ui.run_javascript(js_script)

        def start_pend():
            L = l_in.value or 0
            ang = a_in.value or 0
            g = g_in.value or 0

            if L <= 0 or g <= 0 or ang <= 0:
                err_banner.text = "⚠️ Input Error: Length L, Angle θ, and Gravity g must be positive numbers!"
                err_banner.classes(remove="hidden")
                return
            else:
                err_banner.classes(add="hidden")

            period = 2 * math.pi * math.sqrt(L / g)
            metrics_label.text = f"Oscillation Period T: {period:.3f} seconds | Frequency f: {(1/period):.3f} Hz"
            ui.run_javascript(f"window.runPend({L}, {ang}, {g}, {str(chk_v.value).lower()}, {str(chk_f.value).lower()});")

        btn_play.on("click", start_pend)
        btn_pause.on("click", lambda: ui.run_javascript("window.pausePend();"))
        btn_reset.on("click", lambda: ui.run_javascript("window.resetPend();"))


# --- 3. SPRING-MASS SIMULATION RUNNER ---
def run_spring_simulation():
    with content:
        with ui.row().classes("items-center justify-between w-full mb-4"):
            page_title("Spring-Mass Harmonic 2D Simulation", "Simulate Hooke's Law oscillations.")
            ui.button("Back to List", icon="arrow_back", on_click=lambda: navigate_to(show_simulations)).props("flat color=primary")

        err_banner = ui.label().classes("text-red-400 font-bold text-sm mb-3 hidden")

        with ui.card().classes("glass-card w-full p-5 mb-4"):
            with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                m_in = ui.number(label="Mass m (kg)", value=2.0, min=0.1, max=50).props("outlined")
                k_in = ui.number(label="Spring Constant k (N/m)", value=40.0, min=1, max=200).props("outlined")

            with ui.row().classes("items-center gap-3 mt-4"):
                btn_play = ui.button("▶ Start", props="color=positive")
                btn_pause = ui.button("⏸ Pause", props="color=warning")
                btn_reset = ui.button("↺ Reset", props="color=negative")

        metrics_label = ui.label("Ready to simulate.").classes("text-emerald-400 font-semibold mb-2 text-sm")
        canvas_id = "springCanvas"
        ui.html(f'<canvas id="{canvas_id}" class="sim-canvas"></canvas>').classes("w-full")

        js_script = f"""
        (function() {{
            const canvas = document.getElementById('{canvas_id}');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            let animId = null, running = false;

            window.runSpring = function(m, k) {{
                cancelAnimationFrame(animId);
                running = true;
                let x = 80;
                let v = 0;
                const dt = 0.03;

                function draw() {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    const wallX = 40;
                    const centerY = canvas.height / 2;

                    const a = (-k * x) / m;
                    v += a * dt;
                    x += v * dt;

                    const boxX = wallX + 180 + x;

                    // Wall
                    ctx.fillStyle = '#475569';
                    ctx.fillRect(20, centerY - 60, 20, 120);

                    // Spring
                    ctx.beginPath();
                    ctx.moveTo(wallX, centerY);
                    const coils = 12;
                    const step = (boxX - wallX) / coils;
                    for(let i = 0; i < coils; i++) {{
                        ctx.lineTo(wallX + step * i + step/2, centerY + (i % 2 === 0 ? -20 : 20));
                    }}
                    ctx.lineTo(boxX, centerY);
                    ctx.strokeStyle = '#10b981';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Mass Box
                    ctx.fillStyle = '#059669';
                    ctx.fillRect(boxX, centerY - 35, 70, 70);
                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 14px Arial';
                    ctx.fillText(m + 'kg', boxX + 20, centerY + 5);

                    if(running) animId = requestAnimationFrame(draw);
                }}
                draw();
            }};

            window.pauseSpring = function() {{ running = false; }};
            window.resetSpring = function() {{ running = false; ctx.clearRect(0, 0, canvas.width, canvas.height); }};
        }})();
        """
        ui.run_javascript(js_script)

        def start_spring():
            m = m_in.value or 0
            k = k_in.value or 0

            if m <= 0 or k <= 0:
                err_banner.text = "⚠️ Input Error: Mass m and Spring Constant k must be positive numbers!"
                err_banner.classes(remove="hidden")
                return
            else:
                err_banner.classes(add="hidden")

            omega = math.sqrt(k / m)
            metrics_label.text = f"Angular Frequency ω: {omega:.2f} rad/s | Period T: {(2 * math.pi / omega):.3f} s"
            ui.run_javascript(f"window.runSpring({m}, {k});")

        btn_play.on("click", start_spring)
        btn_pause.on("click", lambda: ui.run_javascript("window.pauseSpring();"))
        btn_reset.on("click", lambda: ui.run_javascript("window.resetSpring();"))


# --- 4. GRAVITY SIMULATION RUNNER ---
def run_gravity_simulation():
    with content:
        with ui.row().classes("items-center justify-between w-full mb-4"):
            page_title("Gravity & Free Fall 2D Simulation", "Observe vertical acceleration and impact metrics.")
            ui.button("Back to List", icon="arrow_back", on_click=lambda: navigate_to(show_simulations)).props("flat color=primary")

        err_banner = ui.label().classes("text-red-400 font-bold text-sm mb-3 hidden")

        with ui.card().classes("glass-card w-full p-5 mb-4"):
            with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                h_in = ui.number(label="Drop Height h (m)", value=50.0, min=5, max=200).props("outlined")
                g_in = ui.number(label="Gravity g (m/s²)", value=9.81, min=0.1, max=30).props("outlined")

            with ui.row().classes("items-center gap-3 mt-4"):
                btn_play = ui.button("▶ Start Drop", props="color=positive")
                btn_reset = ui.button("↺ Reset", props="color=negative")

        metrics_label = ui.label("Ready to drop.").classes("text-amber-400 font-semibold mb-2 text-sm")
        canvas_id = "gravCanvas"
        ui.html(f'<canvas id="{canvas_id}" class="sim-canvas"></canvas>').classes("w-full")

        js_script = f"""
        (function() {{
            const canvas = document.getElementById('{canvas_id}');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            let animId = null;

            window.runGrav = function(h, g) {{
                cancelAnimationFrame(animId);
                let t = 0;
                const dt = 0.03;
                const groundY = canvas.height - 30;

                function draw() {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    const yMeters = 0.5 * g * t * t;
                    const scale = (canvas.height - 80) / h;
                    const ballY = 40 + yMeters * scale;

                    // Floor
                    ctx.fillStyle = '#f59e0b';
                    ctx.fillRect(40, groundY, canvas.width - 80, 6);

                    if (ballY < groundY - 15) {{
                        ctx.beginPath();
                        ctx.arc(canvas.width / 2, ballY, 15, 0, Math.PI * 2);
                        ctx.fillStyle = '#fbbf24';
                        ctx.fill();

                        // Velocity Vector
                        ctx.beginPath();
                        ctx.moveTo(canvas.width / 2, ballY);
                        ctx.lineTo(canvas.width / 2, ballY + (g * t) * 2);
                        ctx.strokeStyle = '#ef4444';
                        ctx.lineWidth = 3;
                        ctx.stroke();

                        t += dt;
                        animId = requestAnimationFrame(draw);
                    }} else {{
                        ctx.beginPath();
                        ctx.arc(canvas.width / 2, groundY - 15, 15, 0, Math.PI * 2);
                        ctx.fillStyle = '#ef4444';
                        ctx.fill();
                    }}
                }}
                draw();
            }};

            window.resetGrav = function() {{ ctx.clearRect(0, 0, canvas.width, canvas.height); }};
        }})();
        """
        ui.run_javascript(js_script)

        def start_grav():
            h = h_in.value or 0
            g = g_in.value or 0

            if h <= 0 or g <= 0:
                err_banner.text = "⚠️ Input Error: Height h and Gravity g must be positive numbers!"
                err_banner.classes(remove="hidden")
                return
            else:
                err_banner.classes(add="hidden")

            t_fall = math.sqrt((2 * h) / g)
            v_impact = g * t_fall
            metrics_label.text = f"Fall Time: {t_fall:.2f}s | Final Impact Velocity: {v_impact:.2f} m/s"
            ui.run_javascript(f"window.runGrav({h}, {g});")

        btn_play.on("click", start_grav)
        btn_reset.on("click", lambda: ui.run_javascript("window.resetGrav();"))


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
