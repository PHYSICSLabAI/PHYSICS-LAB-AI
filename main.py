import os
import math
from datetime import datetime
from nicegui import app, ui
from dotenv import load_dotenv

#Load environment variables from the .env file
load_dotenv()

# Optional: Set your Gemini API key via environment variable: GEMINI_API_KEY
# If not present, the system seamlessly falls back to the embedded offline physics engine.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Initialize Google GenAI Client if API key is provided
ai_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"GenAI Client initialization skipped: {e}")

# =========================================================
# PHYSICS LAB AI CONFIGURATION
# =========================================================

APP_NAME = "PHYSICS Lab AI"

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

# Chat History Storage
chat_history = [
    ("ai", "Welcome! I am your Advanced Physics AI. Ask me anything about Newton's Laws, Kinematics, Black Holes, Quantum Mechanics, Energy, or Relativity!")
]


# =========================================================
# TIME GREETING & OFFLINE PHYSICS ENGINE
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

def get_offline_physics_response(query: str) -> str:
    """Fallback physics engine when GEMINI_API_KEY is not configured."""
    q = query.lower()

    if any(k in q for k in ['newton', "law of motion", 'inertia', 'f=ma']):
        if 'first' in q or 'inertia' in q:
            return "📌 Newton's First Law (Law of Inertia):\nAn object remains at rest or in uniform linear motion unless acted upon by a net external force.\n\nExample: A book on a table stays put until pushed."
        if 'second' in q or 'f=ma' in q or 'force' in q:
            return "📌 Newton's Second Law:\nAcceleration is directly proportional to net force and inversely proportional to mass.\nFormula: F = m × a (Force = Mass × Acceleration)."
        if 'third' in q or 'action' in q or 'reaction' in q:
            return "📌 Newton's Third Law:\nFor every action force, there is an equal and opposite reaction force.\nFormula: F_A = -F_B."
        return "📌 Newton's 3 Laws of Motion:\n1. Inertia: Objects maintain state unless acted on by external force.\n2. Acceleration: F = m × a.\n3. Action-Reaction: Equal & opposite force pairs."

    if any(k in q for k in ['kinematic', 'velocity', 'acceleration', 'displacement', 'projectile']):
        return "🚀 Kinematics Equations (Uniform Acceleration):\n1. v = u + at\n2. s = ut + ½at²\n3. v² = u² + 2as\n4. s = ½(u + v)t\n\nWhere:\n• u = Initial Velocity\n• v = Final Velocity\n• a = Acceleration\n• t = Time\n• s = Displacement"

    if any(k in q for k in ['black hole', 'event horizon', 'singularity', 'hawking', 'schwarzschild']):
        return "🌌 Black Hole Astrophysics:\n• Event Horizon: Boundary where escape velocity exceeds light speed (c).\n• Schwarzschild Radius: R_s = 2GM / c².\n• Singularity: Region of infinite density at the center.\n• Hawking Radiation: Quantum fluctuations causing black hole evaporation over cosmological timescales."

    if any(k in q for k in ['quantum', 'schrodinger', 'uncertainty', 'tunneling', 'superposition', 'photon']):
        return "⚛️ Quantum Mechanics Core Concepts:\n1. Wave-Particle Duality: Light and matter exhibit both wave and particle characteristics (E = hf, λ = h/p).\n2. Heisenberg Uncertainty Principle: Δx · Δp ≥ ℏ / 2.\n3. Schrödinger Equation: iℏ ∂Ψ/∂t = ĤΨ.\n4. Quantum Superposition: Systems exist in linear combinations of states prior to measurement.\n5. Quantum Tunneling: Particles penetrating energy barriers exceeding their kinetic energy."

    if any(k in q for k in ['relativity', 'einstein', 'e=mc', 'speed of light']):
        return "⚡ Relativity Theory:\n• Special Relativity: The speed of light c is invariant in all inertial frames. E = mc² represents mass-energy equivalence.\n• General Relativity: Gravity is the curvature of spacetime caused by mass and energy distribution."

    if any(k in q for k in ['thermodynamics', 'entropy', 'heat', 'temperature']):
        return "🔥 Laws of Thermodynamics:\n• 0th Law: Thermal equilibrium defines temperature.\n• 1st Law: Energy conservation (ΔU = Q - W).\n• 2nd Law: Entropy of an isolated system always increases (ΔS ≥ 0).\n• 3rd Law: Absolute zero (0 K) cannot be reached in finite steps."

    if any(k in q for k in ['energy', 'work', 'power']):
        return "💡 Work & Energy:\n• Work: W = F · d · cos(θ) [Joules]\n• Kinetic Energy: KE = ½mv²\n• Potential Energy: PE = mgh\n• Power: P = W / t [Watts]"

    return f"🌌 Physics Query Received for '{query}':\nFundamental physical laws describe phenomena across all scales—from quantum particles to cosmic black holes. Please ensure SI unit consistency (m, kg, s) during calculations!"


# =========================================================
# GLOBAL HEAD & STYLES INJECTION
# =========================================================

ui.add_head_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Rajdhani:wght@500;700&display=swap');

    * { box-sizing: border-box; }

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

    /* RESPONSIVE OPTIMIZED LOGO SPLASH ANIMATION */
    #splash-overlay {
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(circle at center, #0a1128 0%, #020617 100%);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 99999;
        animation: fadeOutSplash 0.7s ease-in-out 4.2s forwards;
        pointer-events: none;
    }

    .logo-frame {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        padding: 10px;
        max-width: 90vw;
    }

    .logo-top-row {
        display: flex;
        align-items: center;
        gap: clamp(10px, 3vw, 20px);
    }

    .blue-orb {
        width: clamp(36px, 8vw, 52px);
        height: clamp(36px, 8vw, 52px);
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #ffffff 0%, #38bdf8 35%, #1d4ed8 75%, #030712 100%);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.9), 0 0 40px rgba(29, 78, 216, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.8);
        opacity: 0;
        transform: scale(0) rotate(-45deg);
        animation: orbAppear 0.9s cubic-bezier(0.175, 0.885, 0.32, 1.275) 0.2s forwards, orbPulse 2s infinite ease-in-out 1.2s;
    }

    .logo-physics {
        display: flex;
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(1.8rem, 6.5vw, 2.8rem);
        font-weight: 900;
        letter-spacing: clamp(4px, 1.8vw, 10px);
        color: #ffffff;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.5), 0 0 30px rgba(59, 130, 246, 0.3);
    }

    .logo-physics span {
        display: inline-block;
        opacity: 0;
        transform: translateY(-30px) scale(0.6) rotate(-10deg);
        filter: blur(8px);
        animation: coolLetterReveal 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }

    .logo-physics span:nth-child(1) { animation-delay: 0.9s; }
    .logo-physics span:nth-child(2) { animation-delay: 1.05s; }
    .logo-physics span:nth-child(3) { animation-delay: 1.2s; }
    .logo-physics span:nth-child(4) { animation-delay: 1.35s; }
    .logo-physics span:nth-child(5) { animation-delay: 1.5s; }
    .logo-physics span:nth-child(6) { animation-delay: 1.65s; }
    .logo-physics span:nth-child(7) { animation-delay: 1.8s; }

    .logo-lab-ai {
        font-family: 'Rajdhani', sans-serif;
        font-size: clamp(1.2rem, 4vw, 1.7rem);
        font-weight: 700;
        letter-spacing: clamp(4px, 1.5vw, 8px);
        color: #38bdf8;
        margin-left: clamp(46px, 11vw, 72px);
        margin-top: -4px;
        opacity: 0;
        transform: translateY(15px);
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
        animation: labAiReveal 0.7s ease-out 2.3s forwards;
    }

    @keyframes orbAppear {
        0% { opacity: 0; transform: scale(0) rotate(-45deg); }
        100% { opacity: 1; transform: scale(1) rotate(0deg); }
    }
    @keyframes orbPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(56, 189, 248, 0.9), 0 0 40px rgba(29, 78, 216, 0.6); }
        50% { box-shadow: 0 0 30px rgba(56, 189, 248, 1), 0 0 55px rgba(29, 78, 216, 0.8); }
    }
    @keyframes coolLetterReveal {
        0% { opacity: 0; transform: translateY(-30px) scale(0.6) rotate(-10deg); filter: blur(8px); }
        100% { opacity: 1; transform: translateY(0) scale(1) rotate(0deg); filter: blur(0); }
    }
    @keyframes labAiReveal {
        0% { opacity: 0; transform: translateY(15px); filter: blur(4px); }
        100% { opacity: 1; transform: translateY(0); filter: blur(0); }
    }
    @keyframes fadeOutSplash {
        0% { opacity: 1; visibility: visible; }
        100% { opacity: 0; visibility: hidden; }
    }
</style>
""")

ui.add_body_html("""
<div id="splash-overlay">
  <div class="logo-frame">
    <div class="logo-top-row">
      <div class="blue-orb"></div>
      <div class="logo-physics">
        <span>P</span><span>H</span><span>Y</span><span>S</span><span>I</span><span>C</span><span>S</span>
      </div>
    </div>
    <div class="logo-lab-ai">Lab AI</div>
  </div>
</div>
""")


# =========================================================
# MAIN CONTENT CONTAINER & ROUTING
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
# NATIVE FUNCTIONAL AI CHAT DRAWER / WIDGET
# =========================================================

ai_drawer = ui.right_drawer(value=False).props("bordered width=400").classes("bg-slate-900 text-white p-4")

with ai_drawer:
    with ui.row().classes("w-full items-center justify-between mb-4 border-b border-slate-700 pb-2"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("auto_awesome").classes("text-blue-400 text-xl")
            ui.label("Physics AI Assistant").classes("font-bold text-lg")
        ui.button(icon="close", on_click=ai_drawer.toggle).props("flat round dense text-color=grey")

    chat_scroll = ui.column().classes("w-full h-[70vh] overflow-y-auto gap-3 pr-2")

    def render_chat_messages():
        chat_scroll.clear()
        with chat_scroll:
            for sender, text in chat_history:
                if sender == "user":
                    with ui.row().classes("w-full justify-end"):
                        ui.label(text).classes("bg-blue-600 text-white p-3 rounded-xl max-w-[85%] text-sm whitespace-pre-wrap")
                else:
                    with ui.row().classes("w-full justify-start"):
                        ui.label(text).classes("bg-slate-800 text-slate-200 border border-slate-700 p-3 rounded-xl max-w-[85%] text-sm whitespace-pre-wrap")

    render_chat_messages()

    async def send_ai_query(user_text_input):
        text = user_text_input.value.strip()
        if not text:
            return

        chat_history.append(("user", text))
        user_text_input.value = ""
        render_chat_messages()

        # Generate response using Gemini API if available, else offline engine
        if ai_client:
            try:
                prompt = (
                    "You are an expert Physics AI tutor. Provide precise, well-structured, "
                    "and clear explanations covering laws of motion, kinematics, black holes, "
                    "quantum mechanics, relativity, thermodynamics, or electromagnetism as requested.\n\n"
                    f"User question: {text}"
                )
                response = ai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                reply = response.text if response.text else "No response received."
            except Exception as ex:
                reply = f"⚠️ Gemini API Call Failed ({ex}). Using offline engine:\n\n" + get_offline_physics_response(text)
        else:
            reply = get_offline_physics_response(text)

        chat_history.append(("ai", reply))
        render_chat_messages()

    with ui.row().classes("w-full items-center gap-2 mt-4"):
        user_input = ui.input(placeholder="Ask Newton's laws, Quantum, Black holes...").props("outlined dense color=blue").classes("flex-1 text-sm bg-slate-800 text-white")
        user_input.on("keydown.enter", lambda: send_ai_query(user_input))
        ui.button(icon="send", on_click=lambda: send_ai_query(user_input)).props("color=primary dense")

# Floating AI Toggle Button
ui.button("🤖 Physics AI Assistant", on_click=ai_drawer.toggle).props("rounded color=primary icon=auto_awesome").classes("fixed bottom-6 right-6 z-50 shadow-2xl font-bold px-4 py-2")


# =========================================================
# HOME PAGE VIEW
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

            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", ai_drawer.toggle):
                ui.icon("auto_awesome").classes("text-4xl text-amber-500")
                ui.label("AI Physics Assistant").classes("text-xl font-semibold mt-4")
                ui.label("Solve complex physics problems and generate custom scenarios.").classes("text-muted mt-1 text-sm")

            with ui.card().classes("glass-card action-card p-6 cursor-pointer").on("click", lambda: navigate_to(show_calculator)):
                ui.icon("calculate").classes("text-4xl text-cyan-500")
                ui.label("Standard Calculator").classes("text-xl font-semibold mt-4")
                ui.label("Perform quick mathematical calculations.").classes("text-muted mt-1 text-sm")


# =========================================================
# SIMULATIONS LIST & 2D RUNNERS
# =========================================================

def show_simulations():
    with content:
        page_title("Physics Lab AI Simulations", "Select a topic to start interactive 2D physics models.")

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


def run_projectile_simulation():
    with content:
        with ui.row().classes("items-center justify-between w-full mb-4"):
            page_title("Projectile Motion 2D Simulation", "Adjust parameters, toggle vectors, and execute trajectory analysis.")
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
        canvas_id = "projCanvas"
        ui.html(f'<canvas id="{canvas_id}" class="sim-canvas"></canvas>').classes("w-full")

        js_script = f"""
        (function() {{
            const canvas = document.getElementById('{canvas_id}');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            let animId = null, running = false, t = 0;
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

                    ctx.beginPath();
                    ctx.moveTo(30, canvas.height - 40);
                    ctx.lineTo(canvas.width - 30, canvas.height - 40);
                    ctx.strokeStyle = '#475569';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    const x = vx0 * t;
                    const y = (vy0 * t) - (0.5 * g * t * t);
                    const current_vy = vy0 - (g * t);

                    const cx = 40 + x * scale;
                    const cy = (canvas.height - 40) - y * scale;

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

                    if (cy <= canvas.height - 40) {{
                        ctx.beginPath();
                        ctx.arc(cx, cy, 10, 0, Math.PI * 2);
                        ctx.fillStyle = '#ef4444';
                        ctx.fill();

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


def run_pendulum_simulation():
    with content:
        with ui.row().classes("items-center justify-between w-full mb-4"):
            page_title("Simple Pendulum 2D Simulation", "Adjust parameters to observe simple harmonic motion.")
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

                    ctx.beginPath();
                    ctx.moveTo(pivotX - 50, pivotY);
                    ctx.lineTo(pivotX + 50, pivotY);
                    ctx.strokeStyle = '#94a3b8';
                    ctx.lineWidth = 4;
                    ctx.stroke();

                    ctx.beginPath();
                    ctx.moveTo(pivotX, pivotY);
                    ctx.lineTo(bobX, bobY);
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    ctx.beginPath();
                    ctx.arc(bobX, bobY, 18, 0, Math.PI * 2);
                    ctx.fillStyle = '#a855f7';
                    ctx.fill();

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
                let x = 80, v = 0;
                const dt = 0.03;

                function draw() {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    const wallX = 40;
                    const centerY = canvas.height / 2;

                    const a = (-k * x) / m;
                    v += a * dt;
                    x += v * dt;

                    const boxX = wallX + 180 + x;

                    ctx.fillStyle = '#475569';
                    ctx.fillRect(20, centerY - 60, 20, 120);

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

                    ctx.fillStyle = '#f59e0b';
                    ctx.fillRect(40, groundY, canvas.width - 80, 6);

                    if (ballY < groundY - 15) {{
                        ctx.beginPath();
                        ctx.arc(canvas.width / 2, ballY, 15, 0, Math.PI * 2);
                        ctx.fillStyle = '#fbbf24';
                        ctx.fill();

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
# PHYSICS CALCULATOR SUITE
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

            with ui.tab_panels(calc_tabs, value=ke_tab).classes("w-full bg-transparent mt-4"):

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

def show_settings():
    with content:
        page_title("Settings", "Customise interface preferences.")
        with ui.card().classes("glass-card w-full p-6 mt-6"):
            ui.switch("Dark Theme Mode", value=dark_mode.value, on_change=lambda e: dark_mode.set_value(e.value))


# =========================================================
# LAYOUT NAVIGATION DRAWER & TOPBAR
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
        ui.button("AI Assistant", icon="auto_awesome", on_click=ai_drawer.toggle).props("flat").classes("nav-button")

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
        ui.label("MADE BY ISHAN SHARMA").classes("text-muted font-bold tracking-wider mt-1 uppercase").style("font-size: 10px;")

navigate_to(show_home, addToHistory=False)

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8080"))
    ui.run(host="0.0.0.0", port=port, reload=False, title=APP_NAME)
