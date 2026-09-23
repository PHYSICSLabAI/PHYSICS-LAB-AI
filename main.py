import os
from datetime import datetime

from nicegui import app, ui


# =========================================================
# PHYSICS LAB AI
# =========================================================

APP_NAME = "Physics Lab AI"

# Serve assets folder (Ensure 'Banner_2.jpg' is placed inside 'assets/' directory)
app.add_static_files("/assets", "assets")

# Dark mode controller
dark_mode = ui.dark_mode(True)

# Navigation History Stack for Back functionality
navigation_history = []
current_view = None


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
# GLOBAL CSS (THEME & BANNER ADAPTIVE)
# =========================================================

ui.add_head_html("""
<style>

    /* =====================================================
       GLOBAL BASE & BACKGROUND BANNER
       ===================================================== */

    * {
        box-sizing: border-box;
    }

    html, body {
        margin: 0;
        min-height: 100vh;
        font-family: Arial, Helvetica, sans-serif;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    /* Fixed Background Banner Overlay */
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

    /* Gradient overlay for contrast */
    body::after {
        content: "";
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
        transition: background 0.3s ease;
    }


    /* =====================================================
       DARK MODE THEME
       ===================================================== */

    body.body--dark {
        background-color: #020617 !important;
        color: #ffffff !important;
    }

    body.body--dark::before {
        opacity: 0.35;
    }

    body.body--dark::after {
        background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.15), transparent 40%),
                    radial-gradient(circle at bottom left, rgba(14, 165, 233, 0.10), transparent 40%),
                    rgba(2, 6, 23, 0.75);
    }

    body.body--dark .glass-card {
        background: rgba(15, 23, 42, 0.78) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(148, 163, 184, 0.15);
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

    body.body--dark .text-muted {
        color: #94a3b8 !important;
    }

    body.body--dark .nav-button:hover {
        background: rgba(59, 130, 246, 0.18) !important;
    }


    /* =====================================================
       LIGHT MODE THEME
       ===================================================== */

    body.body--light {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    body.body--light::before {
        opacity: 0.15;
    }

    body.body--light::after {
        background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.08), transparent 40%),
                    rgba(248, 250, 252, 0.85);
    }

    body.body--light .glass-card {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        color: #0f172a !important;
    }

    body.body--light .topbar {
        background: rgba(255, 255, 255, 0.90) !important;
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
        color: #0f172a !important;
    }

    body.body--light .physics-sidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(226, 232, 240, 0.8);
        color: #0f172a !important;
    }

    body.body--light .text-muted {
        color: #64748b !important;
    }

    body.body--light .nav-button {
        color: #334155 !important;
    }

    body.body--light .nav-button:hover {
        background: rgba(59, 130, 246, 0.10) !important;
        color: #1e40af !important;
    }


    /* =====================================================
       SHARED COMPONENT STYLES
       ===================================================== */

    .physics-main {
        max-width: 1400px;
        margin: auto;
    }

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

    .nav-button:hover {
        transform: translateX(3px);
    }

    @media (max-width: 700px) {
        .physics-main {
            padding-left: 12px !important;
            padding-right: 12px !important;
        }
    }

</style>
""")


# =========================================================
# MAIN CONTENT CONTAINER
# =========================================================

content = ui.column().classes(
    "physics-main w-full min-h-screen px-4 md:px-8 py-8"
)


# =========================================================
# NAVIGATION & ROUTING HELPERS
# =========================================================

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

        # Greeting Section
        with ui.column().classes("w-full pt-6 md:pt-12 pb-6"):
            ui.label(
                f"{get_greeting()}, Sir."
            ).classes("text-blue-500 text-lg md:text-xl font-semibold mb-2")

            ui.label(
                "Welcome to Physics Lab AI"
            ).classes("text-4xl md:text-6xl font-extrabold tracking-tight")

            ui.label(
                "Explore physics through experiments, calculations, simulations, and AI-powered reasoning."
            ).classes("text-muted text-base md:text-lg mt-3 max-w-2xl")

        # Quick Actions Grid
        with ui.grid(columns=1).classes("w-full md:grid-cols-2 lg:grid-cols-3 gap-5 mt-4"):

            # New Experiment
            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_experiment)):
                ui.icon("science").classes("text-4xl text-blue-500")
                ui.label("New Experiment").classes("text-xl font-semibold mt-4")
                ui.label("Create a physics experiment and explore its behaviour.").classes("text-muted mt-1 text-sm")

            # Simulations
            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_simulations)):
                ui.icon("model_training").classes("text-4xl text-purple-500")
                ui.label("Simulations").classes("text-xl font-semibold mt-4")
                ui.label("Visualise physical systems and interactive models.").classes("text-muted mt-1 text-sm")

            # Calculator
            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_calculator)):
                ui.icon("calculate").classes("text-4xl text-cyan-500")
                ui.label("Calculator").classes("text-xl font-semibold mt-4")
                ui.label("Perform mathematical calculations.").classes("text-muted mt-1 text-sm")

            # Physics Calculator
            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_physics_calculator)):
                ui.icon("functions").classes("text-4xl text-emerald-500")
                ui.label("Physics Calculator").classes("text-xl font-semibold mt-4")
                ui.label("Compute Kinetic Energy, Velocity, Momentum, and Force equations.").classes("text-muted mt-1 text-sm")

            # AI Search
            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_ai_search)):
                ui.icon("auto_awesome").classes("text-4xl text-amber-500")
                ui.label("AI Search").classes("text-xl font-semibold mt-4")
                ui.label("Ask questions and explore physics concepts.").classes("text-muted mt-1 text-sm")

            # Saved Labs
            with ui.card().classes("glass-card action-card p-6").on("click", lambda: navigate_to(show_saved_labs)):
                ui.icon("folder").classes("text-4xl text-orange-500")
                ui.label("Saved Labs").classes("text-xl font-semibold mt-4")
                ui.label("Access saved experiments and historical projects.").classes("text-muted mt-1 text-sm")


# =========================================================
# EXPERIMENT PAGE
# =========================================================

def show_experiment():
    with content:
        page_title("New Experiment", "Create and analyse a physics experiment.")

        with ui.card().classes("glass-card w-full p-6 mt-6"):
            ui.label("Experiment Description").classes("text-lg font-semibold")

            experiment_input = ui.textarea(
                placeholder="Example: A car travels around a circular road at high speed..."
            ).props("outlined").classes("w-full mt-4")

            ui.button("Run Experiment", icon="play_arrow").props("color=primary").classes("mt-4").on(
                "click",
                lambda: ui.notify("Experiment analysis engine is under development.", type="warning")
            )


# =========================================================
# SIMULATIONS PAGE (IN DEVELOPMENT MODULES)
# =========================================================

def show_simulations():
    simulations_list = [
        {
            "title": "Projectile Motion",
            "icon": "sports_baseball",
            "color": "text-blue-500",
            "desc": "Simulate 2D trajectory motion under gravity, air resistance, and launch angle adjustments."
        },
        {
            "title": "Elastic & Inelastic Collisions",
            "icon": "sports_kabaddi",
            "color": "text-purple-500",
            "desc": "Analyze momentum conservation and kinetic energy loss between colliding objects in 1D and 2D."
        },
        {
            "title": "Orbital Mechanics & Gravity",
            "icon": "public",
            "color": "text-indigo-500",
            "desc": "Model planetary orbits, Kepler's laws, satellite paths, and gravitational force vectors."
        },
        {
            "title": "Spring-Mass Dynamics (Hooke's Law)",
            "icon": "waves",
            "color": "text-emerald-500",
            "desc": "Explore Simple Harmonic Motion (SHM), damping coefficients, resonance, and spring force."
        }
    ]

    with content:
        page_title("Physics Simulations", "Interactive graphical models for key physics concepts.")

        with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-6 mt-6"):
            for sim in simulations_list:
                with ui.card().classes("glass-card p-6 flex flex-col justify-between"):
                    with ui.column().classes("gap-2"):
                        with ui.row().classes("items-center gap-3"):
                            ui.icon(sim["icon"]).classes(f"text-3xl {sim['color']}")
                            ui.label(sim["title"]).classes("text-xl font-bold")

                        ui.label(sim["desc"]).classes("text-muted text-sm mt-2")

                    with ui.row().classes("w-full items-center justify-between mt-6 pt-4 border-t border-slate-700/20"):
                        ui.badge("IN DEVELOPMENT").props("outline color=warning").classes("text-xs px-2 py-1")

                        ui.button(
                            "Launch Simulation",
                            icon="play_arrow",
                            on_click=lambda name=sim["title"]: ui.notify(
                                f"'{name}' simulation module is currently in development stage.",
                                type="warning",
                                icon="construction"
                            )
                        ).props("color=primary flat")


# =========================================================
# WORKING PHYSICS CALCULATOR MODULE
# =========================================================

def show_physics_calculator():
    with content:
        page_title("Physics Calculator", "Solve physical formulas and calculate properties.")

        with ui.card().classes("glass-card w-full p-6 mt-6"):
            with ui.tabs().classes("w-full") as tabs:
                ke_tab = ui.tab("Kinetic Energy (KE = ½mv²)")
                v_tab = ui.tab("Velocity (v = d / t)")
                p_tab = ui.tab("Momentum (p = m × v)")

            with ui.tab_panels(tabs, value=ke_tab).classes("w-full bg-transparent mt-4"):

                # ---------------------------------------------
                # 1. KINETIC ENERGY CALCULATOR
                # ---------------------------------------------
                with ui.tab_panel(ke_tab):
                    ui.label("Formula: Kinetic Energy = ½ × Mass × Velocity²").classes("text-sm text-muted mb-4")

                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        ke_mass = ui.number(label="Mass (kg)", value=10, format="%.2f").props("outlined")
                        ke_vel = ui.number(label="Velocity (m/s)", value=5, format="%.2f").props("outlined")

                    ke_res = ui.label("Kinetic Energy: 125.00 Joules (J)").classes("text-xl font-bold text-emerald-500 mt-6")

                    def calc_ke():
                        m = ke_mass.value or 0
                        v = ke_vel.value or 0
                        ke = 0.5 * m * (v ** 2)
                        ke_res.text = f"Kinetic Energy: {ke:.2f} Joules (J)"

                    ui.button("Calculate KE", icon="bolt", on_click=calc_ke).props("color=primary").classes("mt-2")

                # ---------------------------------------------
                # 2. VELOCITY CALCULATOR
                # ---------------------------------------------
                with ui.tab_panel(v_tab):
                    ui.label("Formula: Velocity = Distance / Time").classes("text-sm text-muted mb-4")

                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        v_dist = ui.number(label="Distance (meters)", value=100, format="%.2f").props("outlined")
                        v_time = ui.number(label="Time (seconds)", value=10, format="%.2f").props("outlined")

                    v_res = ui.label("Velocity: 10.00 m/s").classes("text-xl font-bold text-blue-500 mt-6")

                    def calc_v():
                        d = v_dist.value or 0
                        t = v_time.value or 0
                        if t == 0:
                            v_res.text = "Velocity: Cannot divide by zero time!"
                        else:
                            v = d / t
                            v_res.text = f"Velocity: {v:.2f} m/s"

                    ui.button("Calculate Velocity", icon="speed", on_click=calc_v).props("color=primary").classes("mt-2")

                # ---------------------------------------------
                # 3. MOMENTUM CALCULATOR
                # ---------------------------------------------
                with ui.tab_panel(p_tab):
                    ui.label("Formula: Momentum = Mass × Velocity").classes("text-sm text-muted mb-4")

                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-4"):
                        p_mass = ui.number(label="Mass (kg)", value=15, format="%.2f").props("outlined")
                        p_vel = ui.number(label="Velocity (m/s)", value=4, format="%.2f").props("outlined")

                    p_res = ui.label("Momentum: 60.00 kg·m/s").classes("text-xl font-bold text-purple-500 mt-6")

                    def calc_p():
                        m = p_mass.value or 0
                        v = p_vel.value or 0
                        p = m * v
                        p_res.text = f"Momentum: {p:.2f} kg·m/s"

                    ui.button("Calculate Momentum", icon="trending_up", on_click=calc_p).props("color=primary").classes("mt-2")


# =========================================================
# STANDARD CALCULATOR
# =========================================================

def show_calculator():
    with content:
        page_title("Standard Calculator", "Quick mathematical calculations.")

        with ui.card().classes("glass-card w-full max-w-sm p-5 mt-6"):
            display = ui.input(value="").props("outlined readonly").classes("w-full text-right text-2xl font-bold")

            def add_val(v):
                display.value = str(display.value) + str(v)

            def clear_calc():
                display.value = ""

            def compute():
                try:
                    expr = str(display.value).strip()
                    if not expr:
                        return
                    allowed = set("0123456789+-*/().% ")
                    if not all(c in allowed for c in expr):
                        raise ValueError
                    display.value = str(eval(expr, {"__builtins__": {}}, {}))
                except Exception:
                    display.value = "Error"

            btns = [
                ["7", "8", "9", "/"],
                ["4", "5", "6", "*"],
                ["1", "2", "3", "-"],
                ["0", ".", "%", "+"]
            ]

            with ui.column().classes("w-full gap-2 mt-4"):
                for row in btns:
                    with ui.row().classes("w-full gap-2"):
                        for b in row:
                            ui.button(b, on_click=lambda val=b: add_val(val)).props("outline").classes("flex-1 text-lg")

                with ui.row().classes("w-full gap-2 mt-2"):
                    ui.button("C", on_click=clear_calc).props("color=negative").classes("flex-1")
                    ui.button("=", on_click=compute).props("color=primary").classes("flex-1")


# =========================================================
# SAVED LABS
# =========================================================

def show_saved_labs():
    with content:
        page_title("Saved Labs", "Access your saved experiments and simulation logs.")

        with ui.card().classes("glass-card w-full p-8 mt-6 items-center justify-center text-center"):
            ui.icon("folder_open").classes("text-6xl text-orange-400")
            ui.label("No Saved Labs Found").classes("text-xl font-semibold mt-4")
            ui.label("Run experiments or simulations to save reports to your library.").classes("text-muted mt-1 text-sm")


# =========================================================
# AI SEARCH
# =========================================================

def show_ai_search():
    with content:
        page_title("AI Physics Assistant", "Ask questions and clarify core concepts.")

        with ui.card().classes("glass-card w-full p-6 mt-6"):
            ui.textarea(
                placeholder="Example: Explain the difference between elastic and inelastic collisions..."
            ).props("outlined").classes("w-full")

            ui.button("Ask Assistant", icon="auto_awesome").props("color=primary").classes("mt-4").on(
                "click",
                lambda: ui.notify("AI reasoning engine is under development stage.", type="info")
            )


# =========================================================
# SETTINGS
# =========================================================

def show_settings():
    with content:
        page_title("Settings", "Customise interface preferences.")

        with ui.card().classes("glass-card w-full p-6 mt-6"):
            ui.label("Appearance").classes("text-xl font-semibold")
            ui.separator().classes("my-4 opacity-20")

            ui.switch(
                "Dark Theme Mode",
                value=dark_mode.value,
                on_change=lambda e: dark_mode.set_value(e.value)
            ).classes("text-base font-medium")

            ui.label("Toggle between light and dark modes.").classes("text-muted text-sm mt-1")


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

drawer = ui.left_drawer(value=True).props("swipeable").classes("physics-sidebar w-64")

with drawer:
    # Sidebar Header
    with ui.column().classes("w-full px-4 pt-5 pb-4"):
        with ui.row().classes("w-full items-center gap-3"):
            ui.icon("science").classes("text-3xl text-blue-500")
            with ui.column().classes("gap-0"):
                ui.label(APP_NAME).classes("text-lg font-bold")
                ui.label("Simulation Platform").classes("text-xs text-muted")

    ui.separator().classes("opacity-20")

    # Sidebar Navigation Links
    with ui.column().classes("w-full px-3 py-4"):
        ui.label("WORKSPACE").classes("text-xs text-muted px-2 mb-2 font-bold tracking-wider")

        ui.button("Home", icon="home", on_click=lambda: navigate_to(show_home)).props("flat").classes("nav-button")
        ui.button("New Experiment", icon="science", on_click=lambda: navigate_to(show_experiment)).props("flat").classes("nav-button")
        ui.button("Simulations", icon="model_training", on_click=lambda: navigate_to(show_simulations)).props("flat").classes("nav-button")

        ui.separator().classes("opacity-10 my-3")

        ui.label("TOOLS").classes("text-xs text-muted px-2 mb-2 font-bold tracking-wider")

        ui.button("Physics Calculator", icon="functions", on_click=lambda: navigate_to(show_physics_calculator)).props("flat").classes("nav-button")
        ui.button("Calculator", icon="calculate", on_click=lambda: navigate_to(show_calculator)).props("flat").classes("nav-button")
        ui.button("Saved Labs", icon="folder", on_click=lambda: navigate_to(show_saved_labs)).props("flat").classes("nav-button")
        ui.button("AI Search", icon="search", on_click=lambda: navigate_to(show_ai_search)).props("flat").classes("nav-button")

        ui.separator().classes("opacity-10 my-3")

        ui.button("Settings", icon="settings", on_click=lambda: navigate_to(show_settings)).props("flat").classes("nav-button")

    # Sidebar Footer
    with ui.column().classes("absolute bottom-0 left-0 w-full px-4 pb-5"):
        ui.separator().classes("opacity-20 mb-3")
        ui.label("Physics Lab AI").classes("text-sm font-semibold")
        ui.label("Version 2.0").classes("text-xs text-muted")


# =========================================================
# TOP HEADER BAR
# =========================================================

with ui.header().classes("topbar items-center px-3 md:px-5"):
    ui.button(icon="menu", on_click=drawer.toggle).props("flat round").classes("text-current")

    # Left Corner Logo & Title Block
    with ui.row().classes("items-center gap-2 ml-2"):
        ui.icon("science").classes("text-2xl text-blue-500")
        ui.label(APP_NAME).classes("text-lg md:text-xl font-semibold")

    # Top Back Button
    ui.button("BACK", icon="arrow_back", on_click=go_back).props("flat dense").classes("text-current ml-4 text-xs font-bold")

    ui.space()

    # Top-Right System Ready & Author Tag
    with ui.column().classes("items-end gap-0 py-1"):
        ui.badge("● SYSTEM READY").classes("system-ready text-xs px-2 py-0.5 rounded-full font-medium")
        ui.label("MADE BY ISHAN SHARMA").classes("text-[10px] text-muted font-bold tracking-wider mt-1 uppercase")


# =========================================================
# INITIALISE APPLICATION
# =========================================================

navigate_to(show_home, addToHistory=False)


# =========================================================
# SERVER RUNNER
# =========================================================

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8080"))
    ui.run(
        host="0.0.0.0",
        port=port,
        reload=False,
        title=APP_NAME
    )