"""
WorkFacade - The Ultimate "I'm Working" Simulator
==================================================
A single unified app with a glassmorphic launcher menu.
Choose a simulation mode and it runs fullscreen, keeping
you "active" on all platforms while looking completely legit.

Educational / demonstration project showing how activity
simulation, fullscreen overlays, and idle-prevention work
across platforms (Windows, macOS, Linux).

Requirements: pip install pyautogui
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random
import string
import math
import re
from datetime import datetime, timedelta

try:
    import pyautogui
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None


# ═══════════════════════════════════════════════════════════════
# CONSTANTS & THEME
# ═══════════════════════════════════════════════════════════════

APP_TITLE = "WorkFacade"
APP_VERSION = "3.0"

# Glassmorphic color palette
BG_DARK = "#0b0f19"
BG_CARD = "#131a2b"
BG_CARD_HOVER = "#1a2440"
BG_INPUT = "#0d1321"
ACCENT = "#00e5a0"
ACCENT_DIM = "#00b87a"
ACCENT_GLOW = "#00ffb3"
TEXT_PRIMARY = "#e8edf5"
TEXT_SECONDARY = "#7a8ba8"
TEXT_MUTED = "#4a5568"
TEXT_DESC = "#8593ac"  # card body copy — readable but recedes behind titles
BORDER = "#1e2d4a"
BORDER_HOVER = "#2a4070"
RED_ACCENT = "#ff4757"
YELLOW_ACCENT = "#ffd32a"
BLUE_ACCENT = "#3498db"
CYAN_ACCENT = "#00d2d3"
ORANGE_ACCENT = "#ff9f43"
PURPLE_ACCENT = "#9b59b6"
MAGENTA_ACCENT = "#e056fd"
MATRIX_GREEN = "#00ff41"

# Simulation card definitions
SIMULATIONS = [
    {
        "id": "bsod",
        "icon": "\u2620",
        "title": "Blue Screen of Death",
        "subtitle": "Windows BSOD Simulation",
        "desc": "Pixel-perfect Windows 11 BSOD with random stop codes, looping progress, and hidden cursor. Auto-exits when duration expires. Press ESC to exit early.",
        "color": "#3498db",
    },
    {
        "id": "security_scan",
        "icon": "\U0001f6e1",
        "title": "Cyber Threat Scanner",
        "subtitle": "Enterprise Security Audit",
        "desc": "Enterprise security dashboard with live console, dual progress bars, 18 scan items, AI threat scoring, and pause/resume. Elapsed-time tracking stays accurate across pauses.",
        "color": "#00e5a0",
    },
    {
        "id": "windows_update",
        "icon": "\u2b6f",
        "title": "Windows Update",
        "subtitle": "System Update Simulation",
        "desc": "Classic Windows Update with animated spinner dots and slow, erratic progress. Fullscreen, hidden cursor, always-on-top. Auto-exits when done. ESC to exit early.",
        "color": "#0078d4",
    },
    {
        "id": "disk_defrag",
        "icon": "\u2b13",
        "title": "Disk Optimization",
        "subtitle": "Drive Defrag & Analysis",
        "desc": "Drive defragmentation with per-drive status tracking, live block map visualization, rotating action labels, and completion finalization. Stop button to exit.",
        "color": "#ff9f43",
    },
    {
        "id": "stay_active",
        "icon": "\u2615",
        "title": "Stay Active",
        "subtitle": "Invisible Keep-Alive",
        "desc": "Silent keep-alive with micro mouse movements and shift key presses. Countdown timer, progress bar, and minimize button. Set duration in hours or minutes and walk away.",
        "color": "#ffd32a",
    },
    {
        "id": "code_build",
        "icon": "\u2328",
        "title": "Code Compiler",
        "subtitle": "Build & Test Pipeline",
        "desc": "Developer build console: resolves dependencies, compiles modules, bundles assets, and runs a passing test suite with live scrolling output. Looks like you're deep in a build. ESC or Stop to exit.",
        "color": "#9b59b6",
    },
    {
        "id": "ai_training",
        "icon": "\U0001f9e0",
        "title": "AI Model Training",
        "subtitle": "Neural Net Trainer",
        "desc": "Deep-learning training dashboard with live loss/accuracy curves, epoch counter, animated layer activations, and GPU telemetry. Nobody interrupts a model mid-training. ESC or Stop to exit.",
        "color": "#e056fd",
    },
    {
        "id": "matrix_rain",
        "icon": "\U0001f4a7",
        "title": "Matrix Rain",
        "subtitle": "Digital Rain Screensaver",
        "desc": "Fullscreen cascading green digital rain with glowing lead characters and fading trails. Pure hacker aesthetic. Hidden cursor, always-on-top, auto-exits when done. Press ESC to exit early.",
        "color": "#00ff41",
    },
    {
        "id": "bi_trainer",
        "icon": "\U0001f4ca",
        "title": "THE BI TRAINER",
        "subtitle": "BI Chart & Insight Clinic",
        "desc": "Scrolling BI masterclass: 12 chart types drawn live, the SQL/DAX/pandas behind each one, and the rules for reading them honestly. Arrows steer, SPACE pauses.",
        "color": "#3498db",
    },
    {
        "id": "docs",
        "icon": "\u2139",
        "title": "Documentation",
        "subtitle": "How It Works & Why",
        "desc": "Full breakdown of every simulation mode, keep-alive mechanics, technical details, launcher features, and usage notes.",
        "color": "#7a8ba8",
    },
]


# ═══════════════════════════════════════════════════════════════
# KEEP-ALIVE ENGINE (shared across all simulation modes)
# ═══════════════════════════════════════════════════════════════

# Intensity profiles control how often (and how) activity is injected.
# Each profile defines base mouse/key intervals in seconds.
KEEP_ALIVE_PROFILES = {
    "Stealth": {
        "mouse": 110, "key": 150,
        "desc": "Longest gaps — minimal footprint, just enough to stay green.",
    },
    "Normal": {
        "mouse": 55, "key": 80,
        "desc": "Balanced default — reliable across Teams, Slack, and the OS.",
    },
    "Aggressive": {
        "mouse": 25, "key": 35,
        "desc": "Frequent nudges — never lets the idle timer get close.",
    },
}
DEFAULT_PROFILE = "Normal"

# Harmless keys that have no visible effect in virtually any application.
HARMLESS_KEYS = ["shift", "ctrl", "f13", "f14", "f15"]


class KeepAliveEngine:
    """Background thread that prevents idle/away status.

    Supports selectable intensity profiles, randomized timing jitter so the
    activity never looks robotic, a rotating set of harmless keys, occasional
    micro mouse-scrolls, and live activity statistics.
    """

    def __init__(self, profile=DEFAULT_PROFILE):
        self._running = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
        self.jitter = 0.25  # +/- 25% randomization on every interval
        self.mouse_moves = 0
        self.key_presses = 0
        self.last_action = "idle"
        self.set_profile(profile)

    def set_profile(self, name):
        """Select an intensity profile (Stealth / Normal / Aggressive)."""
        prof = KEEP_ALIVE_PROFILES.get(name, KEEP_ALIVE_PROFILES[DEFAULT_PROFILE])
        self.profile = name if name in KEEP_ALIVE_PROFILES else DEFAULT_PROFILE
        self.mouse_interval = prof["mouse"]
        self.key_interval = prof["key"]

    def _jittered(self, base):
        """Return base interval +/- the jitter fraction so timing varies."""
        return base * (1 + random.uniform(-self.jitter, self.jitter))

    @property
    def running(self):
        return self._running.is_set()

    def start(self):
        with self._lock:
            if self._running.is_set():
                return
            # Reset per-session counters so each simulation starts from zero.
            self.mouse_moves = 0
            self.key_presses = 0
            self.last_action = "idle"
            self._running.set()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._running.clear()
            thread = self._thread
            self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=2)
        self.last_action = "stopped"

    @property
    def available(self):
        """Check if pyautogui is available for input injection."""
        return pyautogui is not None

    def stats(self):
        """Return a snapshot of activity counters for UI display."""
        return {
            "profile": self.profile,
            "mouse_moves": self.mouse_moves,
            "key_presses": self.key_presses,
            "last_action": self.last_action,
        }

    def _do_mouse(self):
        """Inject an invisible mouse nudge; occasionally a tiny scroll."""
        if not pyautogui:
            return
        try:
            if random.random() < 0.2:
                pyautogui.scroll(random.choice([-1, 1]))
                self.last_action = "scroll"
            else:
                dx = random.choice([-1, 1])
                pyautogui.moveRel(dx, 0, duration=0.05)
                pyautogui.moveRel(-dx, 0, duration=0.05)
                self.last_action = "mouse"
            self.mouse_moves += 1
        except Exception:
            pass

    def _do_key(self):
        """Press a randomly chosen harmless key."""
        if not pyautogui:
            return
        try:
            pyautogui.press(random.choice(HARMLESS_KEYS))
            self.key_presses += 1
            self.last_action = "key"
        except Exception:
            pass

    def _loop(self):
        last_mouse = time.time()
        last_key = time.time()
        mouse_wait = self._jittered(self.mouse_interval)
        key_wait = self._jittered(self.key_interval)
        while self._running.is_set():
            now = time.time()
            if now - last_mouse > mouse_wait:
                self._do_mouse()
                last_mouse = now
                mouse_wait = self._jittered(self.mouse_interval)
            if now - last_key > key_wait:
                self._do_key()
                last_key = now
                key_wait = self._jittered(self.key_interval)
            time.sleep(0.5)


# Global keep-alive instance
keep_alive = KeepAliveEngine()


def _post(win, func, delay=0):
    """Schedule ``func`` on the Tk main loop, tolerating a torn-down window.

    Background worker threads dispatch UI updates via ``win.after``. If the
    window is destroyed mid-flight (ESC, Stop, or auto-exit), ``after`` raises
    TclError (window gone) or RuntimeError (no main loop). Both are benign
    during shutdown, so we swallow them instead of crashing the worker thread.
    """
    try:
        return win.after(delay, func)
    except (tk.TclError, RuntimeError):
        return None


def _init_styles():
    """Configure all ttk styles once. Call after root Tk is created."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Green.Horizontal.TProgressbar",
                     background=ACCENT, troughcolor="#1a2235")
    style.configure("Cyan.Horizontal.TProgressbar",
                     background=CYAN_ACCENT, troughcolor="#1a2235")
    style.configure("Defrag.Horizontal.TProgressbar",
                     background=ACCENT, troughcolor="#333333")
    style.configure("Active.Horizontal.TProgressbar",
                     background=YELLOW_ACCENT, troughcolor="#1a2235")
    style.configure("Purple.Horizontal.TProgressbar",
                     background=PURPLE_ACCENT, troughcolor="#1a2235")
    style.configure("Magenta.Horizontal.TProgressbar",
                     background=MAGENTA_ACCENT, troughcolor="#1a2235")
    style.configure("BI.Horizontal.TProgressbar",
                     background=BLUE_ACCENT, troughcolor="#132038")


# ═══════════════════════════════════════════════════════════════
# SIMULATION: BSOD
# ═══════════════════════════════════════════════════════════════

class BSODSimulation:
    """Fullscreen Windows 11 Blue Screen of Death."""

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()

        self.win = tk.Toplevel(parent_root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#0078d4")
        self.win.focus_force()

        # Hide cursor
        self.win.config(cursor="none")

        # Bind escape and close
        self.win.bind("<Escape>", self._exit)
        self.win.protocol("WM_DELETE_WINDOW", self._exit)

        self._build_ui()
        keep_alive.start()

        # Start the fake progress
        self.progress = 0
        self._tick()

    def _build_ui(self):
        container = tk.Frame(self.win, bg="#0078d4")
        container.place(relx=0.5, rely=0.42, anchor="center")

        # Sad face
        tk.Label(
            container, text=":(", font=("Segoe UI Light", 120),
            fg="white", bg="#0078d4"
        ).pack(anchor="w")

        # Main text
        tk.Label(
            container,
            text="Your PC ran into a problem and needs to restart.",
            font=("Segoe UI", 22), fg="white", bg="#0078d4"
        ).pack(anchor="w", pady=(20, 5))

        tk.Label(
            container,
            text="We're just collecting some error info, and then we'll restart for you.",
            font=("Segoe UI", 16), fg="white", bg="#0078d4"
        ).pack(anchor="w", pady=(0, 30))

        # Progress
        self.progress_label = tk.Label(
            container, text="0% complete",
            font=("Segoe UI", 18), fg="white", bg="#0078d4"
        )
        self.progress_label.pack(anchor="w", pady=(0, 40))

        # QR code placeholder (square block)
        bottom = tk.Frame(container, bg="#0078d4")
        bottom.pack(anchor="w", pady=(10, 0))

        qr_frame = tk.Frame(bottom, bg="white", width=90, height=90)
        qr_frame.pack(side="left", padx=(0, 20))
        qr_frame.pack_propagate(False)
        tk.Label(
            qr_frame, text="QR", font=("Consolas", 14, "bold"),
            fg="#0078d4", bg="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        info_frame = tk.Frame(bottom, bg="#0078d4")
        info_frame.pack(side="left")

        tk.Label(
            info_frame,
            text="For more information about this issue and possible fixes,",
            font=("Segoe UI", 11), fg="white", bg="#0078d4"
        ).pack(anchor="w")
        tk.Label(
            info_frame,
            text="visit https://www.windows.com/stopcode",
            font=("Segoe UI", 11), fg="white", bg="#0078d4"
        ).pack(anchor="w")
        tk.Label(
            info_frame,
            text="",
            font=("Segoe UI", 8), fg="#0078d4", bg="#0078d4"
        ).pack(anchor="w")

        stop_code = random.choice([
            "CRITICAL_PROCESS_DIED", "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED",
            "IRQL_NOT_LESS_OR_EQUAL", "KERNEL_DATA_INPAGE_ERROR",
            "PAGE_FAULT_IN_NONPAGED_AREA", "SYSTEM_SERVICE_EXCEPTION",
            "UNEXPECTED_KERNEL_MODE_TRAP", "KMODE_EXCEPTION_NOT_HANDLED",
        ])
        tk.Label(
            info_frame,
            text=f"Stop code: {stop_code}",
            font=("Segoe UI", 11), fg="white", bg="#0078d4"
        ).pack(anchor="w", pady=(8, 0))

    def _tick(self):
        if not self.win.winfo_exists():
            return

        # Check if duration has elapsed
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self._exit()
            return

        if self.progress < 100:
            increment = random.choice([0, 0, 0, 0, 1, 1, 0, 0, 0, 1])
            self.progress = min(100, self.progress + increment)
            self.progress_label.config(text=f"{self.progress}% complete")
            delay = random.randint(800, 4000)
            self.win.after(delay, self._tick)
        else:
            # Reset and loop
            self.progress = 0
            self.win.after(8000, self._tick)

    def _exit(self, event=None):
        if not self.win.winfo_exists():
            return
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: CYBER THREAT SCANNER
# ═══════════════════════════════════════════════════════════════

class SecurityScanSimulation:
    """Full cybersecurity behavioral analytics engine UI."""

    SCAN_ITEMS = [
        "Kernel integrity verification",
        "User behavior entropy analysis",
        "Credential reuse vector scan",
        "DNS tunneling indicator check",
        "Memory injection trace sweep",
        "Lateral movement path detection",
        "Encrypted payload heuristics",
        "Privilege escalation audit",
        "Registry anomaly detection",
        "Process hollowing indicators",
        "Network covert channel scan",
        "API hooking pattern analysis",
        "Fileless malware trace detection",
        "Ransomware behavior pattern match",
        "Zero-day exploit heuristic scan",
        "TLS certificate chain validation",
        "Rootkit persistence mechanism scan",
        "Sandbox evasion technique detection",
    ]

    SCAN_PHASES = [
        "Network Behavioral Analysis",
        "Forensic Memory Sweep",
        "Credential Exposure Audit",
        "AI Correlation Engine",
        "Anomaly Clustering Pass",
        "Threat Intelligence Feed Sync",
        "Sandbox Execution Analysis",
        "Endpoint Detection Response",
        "Deep Packet Inspection",
        "Behavioral Baseline Calibration",
    ]

    FLAGS = [
        ("OK", "#00e5a0"), ("WARN", "#ffd32a"),
        ("FLAGGED", "#ff9f43"), ("CRITICAL", "#ff4757"),
    ]

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.scanning = False
        self.paused = False
        self.start_time = None
        self.total_paused = 0
        self._pause_start = None

        self.win = tk.Toplevel(parent_root)
        self.win.title("Cyber Threat Behavioral Analytics Engine v9.4")
        self.win.geometry("1100x750")
        self.win.configure(bg="#0a0e17")
        self.win.protocol("WM_DELETE_WINDOW", self._exit)
        self.win.bind("<Escape>", lambda e: self._exit())

        self._build_ui()
        self._start_scan()

    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self.win, bg="#0d1220", height=50)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="\U0001f6e1  CYBER THREAT BEHAVIORAL ANALYTICS ENGINE v9.4",
            font=("Consolas", 14, "bold"), fg=ACCENT, bg="#0d1220"
        ).pack(side="left", padx=15, pady=10)

        self.elapsed_label = tk.Label(
            title_frame, text="00:00:00",
            font=("Consolas", 13), fg=TEXT_SECONDARY, bg="#0d1220"
        )
        self.elapsed_label.pack(side="right", padx=15)

        tk.Label(
            title_frame, text="ELAPSED",
            font=("Consolas", 9), fg=TEXT_MUTED, bg="#0d1220"
        ).pack(side="right")

        # Status bar
        status_frame = tk.Frame(self.win, bg="#111827", height=36)
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame, text="INITIALIZING...",
            font=("Consolas", 10), fg=ACCENT, bg="#111827"
        )
        self.status_label.pack(side="left", padx=15, pady=6)

        self.percent_label = tk.Label(
            status_frame, text="0%",
            font=("Consolas", 10, "bold"), fg=ACCENT, bg="#111827"
        )
        self.percent_label.pack(side="right", padx=15)

        # Progress bars
        prog_frame = tk.Frame(self.win, bg="#0a0e17", pady=8)
        prog_frame.pack(fill="x", padx=15)

        tk.Label(
            prog_frame, text="OVERALL", font=("Consolas", 8),
            fg=TEXT_MUTED, bg="#0a0e17"
        ).pack(anchor="w")

        self.overall_bar = ttk.Progressbar(
            prog_frame, length=1060, mode="determinate",
            style="Green.Horizontal.TProgressbar"
        )
        self.overall_bar.pack(fill="x", pady=(2, 6))

        tk.Label(
            prog_frame, text="CURRENT MODULE", font=("Consolas", 8),
            fg=TEXT_MUTED, bg="#0a0e17"
        ).pack(anchor="w")

        self.module_bar = ttk.Progressbar(
            prog_frame, length=1060, mode="determinate",
            style="Cyan.Horizontal.TProgressbar"
        )
        self.module_bar.pack(fill="x", pady=(2, 0))

        # Console
        console_frame = tk.Frame(self.win, bg="#0a0e17")
        console_frame.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        tk.Label(
            console_frame, text="SCAN OUTPUT",
            font=("Consolas", 9, "bold"), fg=TEXT_MUTED, bg="#0a0e17"
        ).pack(anchor="w", pady=(0, 3))

        self.console = scrolledtext.ScrolledText(
            console_frame, bg="#060a12", fg=ACCENT,
            font=("Consolas", 9), insertbackground=ACCENT,
            relief="flat", bd=0, highlightthickness=1,
            highlightcolor=BORDER, highlightbackground=BORDER,
        )
        self.console.pack(fill="both", expand=True)

        # Configure text tags for colors
        self.console.tag_configure("green", foreground=ACCENT)
        self.console.tag_configure("yellow", foreground=YELLOW_ACCENT)
        self.console.tag_configure("orange", foreground=ORANGE_ACCENT)
        self.console.tag_configure("red", foreground=RED_ACCENT)
        self.console.tag_configure("cyan", foreground=CYAN_ACCENT)
        self.console.tag_configure("blue", foreground=BLUE_ACCENT)
        self.console.tag_configure("muted", foreground=TEXT_MUTED)
        self.console.tag_configure("white", foreground=TEXT_PRIMARY)

        # Bottom controls
        bottom = tk.Frame(self.win, bg="#0d1220", height=45)
        bottom.pack(fill="x")
        bottom.pack_propagate(False)

        btn_style = {"font": ("Segoe UI", 9, "bold"), "relief": "flat",
                      "bd": 0, "padx": 16, "pady": 4, "cursor": "hand2"}

        self.pause_btn = tk.Button(
            bottom, text="PAUSE", bg="#1a2744", fg=YELLOW_ACCENT,
            command=self._toggle_pause, **btn_style
        )
        self.pause_btn.pack(side="left", padx=(15, 5), pady=8)

        tk.Button(
            bottom, text="STOP & EXIT", bg="#2a1525", fg=RED_ACCENT,
            command=self._exit, **btn_style
        ).pack(side="left", padx=5, pady=8)

    def _log(self, msg, tag="green"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.console.insert("end", f"[{ts}] ", "muted")
        self.console.insert("end", f"{msg}\n", tag)
        self.console.see("end")

    def _start_scan(self):
        self.scanning = True
        self.start_time = time.time()
        keep_alive.start()
        self._log("=== SCAN INITIATED ===", "green")
        self._log(f"Runtime: {self.duration // 3600}h | Engine: v9.4 | Mode: Full Behavioral", "muted")
        threading.Thread(target=self._scan_loop, daemon=True).start()
        self._update_elapsed()

    def _update_elapsed(self):
        if not self.scanning or not self.win.winfo_exists():
            return
        # Subtract paused time so elapsed matches progress percentage
        paused = self.total_paused
        if self._pause_start is not None:
            paused += time.time() - self._pause_start
        elapsed = time.time() - self.start_time - paused
        h, m, s = int(elapsed // 3600), int((elapsed % 3600) // 60), int(elapsed % 60)
        self.elapsed_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.win.after(1000, self._update_elapsed)

    def _scan_loop(self):
        while self.scanning:
            while self.paused:
                time.sleep(0.1)
                if not self.scanning:
                    return

            # Subtract paused time from elapsed for accurate progress
            elapsed = time.time() - self.start_time - self.total_paused
            if elapsed >= self.duration:
                break
            overall = min(99, (elapsed / self.duration) * 100)

            try:
                _post(self.win, lambda v=overall: self._update_bars(v, 0))
                _post(self.win, lambda v=overall: self.status_label.config(
                    text=f"SCANNING \u2014 Phase {random.randint(1, 8)}"
                ))
                _post(self.win, lambda v=overall: self.percent_label.config(
                    text=f"{int(v)}%"
                ))
            except Exception:
                return

            # Phase header
            phase = random.choice(self.SCAN_PHASES)
            _post(self.win, lambda p=phase: self._log(f"\n--- {p} ---", "cyan"))

            # Module progress simulation
            for mp in range(0, 101, random.randint(5, 15)):
                if not self.scanning:
                    return
                while self.paused and self.scanning:
                    time.sleep(0.1)
                if not self.scanning:
                    return
                _post(self.win, lambda v=overall, m=mp: self._update_bars(v, m))
                time.sleep(random.uniform(0.04, 0.08))

            # Scan items with flags
            items = random.sample(self.SCAN_ITEMS, random.randint(3, 7))
            for item in items:
                if not self.scanning:
                    return
                status, color = random.choices(
                    self.FLAGS, weights=[55, 25, 15, 5], k=1
                )[0]
                tag = {ACCENT: "green", YELLOW_ACCENT: "yellow",
                       ORANGE_ACCENT: "orange", RED_ACCENT: "red"}[color]
                _post(self.win, lambda i=item, s=status, t=tag:
                    self._log(f"  {i:<42} [{s}]", t))
                time.sleep(random.uniform(0.08, 0.25))

            # Random events
            if random.random() < 0.15:
                _post(self.win, lambda: self._log(
                    "  Subsystem latency spike \u2014 auto-correcting", "yellow"))
            if random.random() < 0.08:
                _post(self.win, lambda: self._log(
                    "  Packet capture: anomalous traffic pattern logged", "orange"))
            if random.random() < 0.05:
                conf = round(random.uniform(0.4, 0.99), 2)
                score = int(conf * random.randint(80, 200))
                _post(self.win, lambda c=conf, s=score: self._log(
                    f"  [AI] ThreatScoreNet inference \u2014 conf: {c} \u2014 score: {s}", "blue"))

            time.sleep(random.uniform(0.3, 1.5))

        if self.scanning:
            _post(self.win, lambda: self._log(
                "\n=== SYSTEM SCAN COMPLETE \u2014 REPORT GENERATED ===", "green"))
            _post(self.win, lambda: self._update_bars(100, 100))
            _post(self.win, lambda: self.status_label.config(text="COMPLETE"))
            _post(self.win, lambda: self.percent_label.config(text="100%"))
            # Auto-exit after brief delay to show completion
            _post(self.win, self._exit, 3000)

    def _update_bars(self, overall, module):
        try:
            self.overall_bar["value"] = overall
            self.module_bar["value"] = module
        except Exception:
            pass

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self._pause_start = time.time()
            self.pause_btn.config(text="RESUME", fg=ACCENT)
            self._log("=== SCAN PAUSED ===", "yellow")
        else:
            if self._pause_start is not None:
                self.total_paused += time.time() - self._pause_start
                self._pause_start = None
            self.pause_btn.config(text="PAUSE", fg=YELLOW_ACCENT)
            self._log("=== SCAN RESUMED ===", "green")

    def _exit(self):
        if not self.scanning:
            return
        self.scanning = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: WINDOWS UPDATE
# ═══════════════════════════════════════════════════════════════

class WindowsUpdateSimulation:
    """Fullscreen Windows Update screen."""

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()

        self.win = tk.Toplevel(parent_root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#000000")
        self.win.config(cursor="none")
        self.win.focus_force()

        self.win.bind("<Escape>", self._exit)
        self.win.protocol("WM_DELETE_WINDOW", self._exit)

        self.progress = 0
        self._build_ui()
        keep_alive.start()
        self._tick()

    def _build_ui(self):
        container = tk.Frame(self.win, bg="#000000")
        container.place(relx=0.5, rely=0.45, anchor="center")

        # Spinning dots (simulated with a label that updates)
        self.spinner_label = tk.Label(
            container, text="\u25CF  \u25CB  \u25CB  \u25CB  \u25CB",
            font=("Segoe UI", 28), fg="#0078d4", bg="#000000"
        )
        self.spinner_label.pack(pady=(0, 40))

        tk.Label(
            container, text="Working on updates",
            font=("Segoe UI Light", 32), fg="white", bg="#000000"
        ).pack()

        self.progress_label = tk.Label(
            container, text="0% complete",
            font=("Segoe UI Light", 22), fg="white", bg="#000000"
        )
        self.progress_label.pack(pady=(10, 30))

        tk.Label(
            container, text="Don't turn off your computer.",
            font=("Segoe UI", 14), fg="#999999", bg="#000000"
        ).pack()

        # ESC hint (subtle, bottom of screen)
        tk.Label(
            self.win, text="Press ESC to exit",
            font=("Segoe UI", 8), fg="#333333", bg="#000000"
        ).place(relx=0.5, rely=0.97, anchor="center")

        self.spinner_step = 0
        self._animate_spinner()

    def _animate_spinner(self):
        if not self.win.winfo_exists():
            return
        dots = ["\u25CB"] * 5
        dots[self.spinner_step % 5] = "\u25CF"
        self.spinner_label.config(text="  ".join(dots))
        self.spinner_step += 1
        self.win.after(300, self._animate_spinner)

    def _tick(self):
        if not self.win.winfo_exists():
            return

        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self._exit()
            return

        # Slow, realistic progress
        target = min(99, int((elapsed / self.duration) * 100))
        if self.progress < target:
            self.progress += random.choice([0, 0, 1, 0, 0, 0, 1])
            self.progress = min(self.progress, target)

        self.progress_label.config(text=f"{self.progress}% complete")

        delay = random.randint(1500, 5000)
        self.win.after(delay, self._tick)

    def _exit(self, event=None):
        if not self.win.winfo_exists():
            return
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: DISK DEFRAGMENTATION
# ═══════════════════════════════════════════════════════════════

class DiskDefragSimulation:
    """Simulates a Windows-style disk optimization tool."""

    DRIVE_NAMES = ["Windows (C:)", "Data (D:)", "Recovery (E:)"]

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()
        self.running = True

        self.win = tk.Toplevel(parent_root)
        self.win.title("Optimize Drives")
        self.win.geometry("850x620")
        self.win.configure(bg="#1e1e1e")
        self.win.protocol("WM_DELETE_WINDOW", self._exit)
        self.win.bind("<Escape>", lambda e: self._exit())

        self._build_ui()
        keep_alive.start()
        threading.Thread(target=self._defrag_loop, daemon=True).start()

    def _build_ui(self):
        # Title
        tk.Label(
            self.win, text="Optimize Drives",
            font=("Segoe UI", 16, "bold"), fg="white", bg="#1e1e1e"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tk.Label(
            self.win,
            text="Optimizing your drives can help your computer run more efficiently.",
            font=("Segoe UI", 10), fg="#aaaaaa", bg="#1e1e1e"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Drive list
        list_frame = tk.Frame(self.win, bg="#2d2d2d", highlightbackground="#444",
                               highlightthickness=1)
        list_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Header
        header = tk.Frame(list_frame, bg="#333333")
        header.pack(fill="x")
        for text, w in [("Drive", 25), ("Media type", 15), ("Last optimized", 20), ("Current status", 25)]:
            tk.Label(
                header, text=text, font=("Segoe UI", 9, "bold"),
                fg="#cccccc", bg="#333333", width=w, anchor="w"
            ).pack(side="left", padx=5, pady=6)

        self.drive_labels = []
        for i, name in enumerate(self.DRIVE_NAMES):
            row = tk.Frame(list_frame, bg="#2d2d2d" if i % 2 == 0 else "#282828")
            row.pack(fill="x")
            tk.Label(row, text=name, font=("Segoe UI", 9), fg="white",
                     bg=row["bg"], width=25, anchor="w").pack(side="left", padx=5, pady=4)
            tk.Label(row, text="Solid state drive" if i == 0 else "Hard disk drive",
                     font=("Segoe UI", 9), fg="#aaa", bg=row["bg"],
                     width=15, anchor="w").pack(side="left", padx=5)
            tk.Label(row, text=datetime.now().strftime("%m/%d/%Y %I:%M %p"),
                     font=("Segoe UI", 9), fg="#aaa", bg=row["bg"],
                     width=20, anchor="w").pack(side="left", padx=5)
            status_lbl = tk.Label(row, text="Queued", font=("Segoe UI", 9),
                                   fg="#ffd32a", bg=row["bg"], width=25, anchor="w")
            status_lbl.pack(side="left", padx=5)
            self.drive_labels.append(status_lbl)

        # Block visualization
        tk.Label(
            self.win, text="Block Map Visualization",
            font=("Segoe UI", 10, "bold"), fg="#aaaaaa", bg="#1e1e1e"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.canvas = tk.Canvas(
            self.win, width=800, height=160, bg="#111111",
            highlightthickness=1, highlightbackground="#444"
        )
        self.canvas.pack(padx=20, pady=(0, 10))
        self._draw_blocks()

        # Progress
        prog_frame = tk.Frame(self.win, bg="#1e1e1e")
        prog_frame.pack(fill="x", padx=20, pady=(5, 5))

        tk.Label(
            prog_frame, text="Progress:", font=("Segoe UI", 10),
            fg="#aaaaaa", bg="#1e1e1e"
        ).pack(side="left")

        self.progress_label = tk.Label(
            prog_frame, text="0%", font=("Segoe UI", 10, "bold"),
            fg=ACCENT, bg="#1e1e1e"
        )
        self.progress_label.pack(side="left", padx=10)

        self.progress_bar = ttk.Progressbar(
            self.win, length=800, mode="determinate",
            style="Defrag.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(padx=20, pady=(0, 10))

        # Current action
        self.action_label = tk.Label(
            self.win, text="Analyzing...",
            font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg="#1e1e1e"
        )
        self.action_label.pack(anchor="w", padx=20)

        # Exit button
        tk.Button(
            self.win, text="Stop & Exit", font=("Segoe UI", 9, "bold"),
            bg="#442222", fg=RED_ACCENT, relief="flat", padx=15, pady=4,
            command=self._exit, cursor="hand2"
        ).pack(anchor="e", padx=20, pady=(10, 15))

    def _draw_blocks(self):
        self.canvas.delete("all")
        colors = ["#00e5a0", "#0078d4", "#ff9f43", "#ff4757",
                  "#ffd32a", "#9b59b6", "#333333", "#1a1a1a"]
        weights = [35, 18, 8, 3, 6, 4, 18, 8]
        bw, bh = 10, 10
        for row in range(16):
            for col in range(80):
                x, y = col * bw, row * bh
                c = random.choices(colors, weights=weights, k=1)[0]
                self.canvas.create_rectangle(x, y, x + bw - 1, y + bh - 1, fill=c, outline="")

    def _defrag_loop(self):
        actions = [
            "Analyzing drive fragmentation...",
            "Moving file clusters to contiguous blocks...",
            "Consolidating free space...",
            "Optimizing MFT zone...",
            "Relocating system files...",
            "Verifying block integrity...",
            "Compacting volume metadata...",
            "Reindexing file allocation table...",
        ]

        num_drives = len(self.DRIVE_NAMES)
        drive_idx = 0
        while self.running and time.time() - self.start_time < self.duration:
            elapsed = time.time() - self.start_time
            pct = min(99, int((elapsed / self.duration) * 100))

            # Calculate per-drive progress
            drive_share = 100 // num_drives
            drive_pct = min(99, max(0, int((pct - drive_idx * drive_share) / drive_share * 100))) if drive_idx < num_drives else 100

            try:
                _post(self.win, lambda p=pct: self.progress_bar.configure(value=p))
                _post(self.win, lambda p=pct: self.progress_label.config(text=f"{p}%"))
                _post(self.win, lambda a=random.choice(actions): self.action_label.config(text=a))

                for i, lbl in enumerate(self.drive_labels):
                    if i < drive_idx:
                        _post(self.win, lambda w=lbl: w.config(text="OK (0% fragmented)", fg=ACCENT))
                    elif i == drive_idx:
                        _post(self.win, lambda w=lbl, dp=drive_pct: w.config(
                            text=f"Optimizing ({dp}%)", fg=ORANGE_ACCENT))
                    else:
                        _post(self.win, lambda w=lbl: w.config(text="Queued", fg=YELLOW_ACCENT))
            except Exception:
                return

            # Periodically redraw blocks
            if random.random() < 0.15:
                _post(self.win, self._draw_blocks)

            # Advance to next drive at evenly-spaced thresholds
            if drive_idx < num_drives - 1 and pct >= drive_share * (drive_idx + 1):
                drive_idx += 1

            time.sleep(random.uniform(1.0, 3.0))

        # Show completion state
        if self.running:
            try:
                _post(self.win, lambda: self.progress_bar.configure(value=100))
                _post(self.win, lambda: self.progress_label.config(text="100%"))
                _post(self.win, lambda: self.action_label.config(
                    text="All drives have been optimized.", fg=ACCENT))
                for lbl in self.drive_labels:
                    _post(self.win, lambda w=lbl: w.config(
                        text="OK (0% fragmented)", fg=ACCENT))
                # Auto-exit after brief delay to show completion
                _post(self.win, self._exit, 3000)
            except Exception:
                pass

    def _exit(self):
        if not self.running:
            return
        self.running = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: STAY ACTIVE (invisible keep-alive)
# ═══════════════════════════════════════════════════════════════

class StayActiveSimulation:
    """Minimal window that just keeps the PC active."""

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()
        self.running = True

        self.win = tk.Toplevel(parent_root)
        self.win.title("Stay Active")
        self.win.geometry("440x340")
        self.win.configure(bg=BG_DARK)
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._exit)
        self.win.bind("<Escape>", lambda e: self._exit())

        self._build_ui()
        keep_alive.start()
        self._tick()

    def _build_ui(self):
        tk.Label(
            self.win, text="\u2615", font=("Segoe UI", 36),
            fg=YELLOW_ACCENT, bg=BG_DARK
        ).pack(pady=(20, 0))

        tk.Label(
            self.win, text="Staying Active",
            font=("Segoe UI", 18, "bold"), fg=TEXT_PRIMARY, bg=BG_DARK
        ).pack(pady=(5, 2))

        if keep_alive.available:
            tk.Label(
                self.win, text="Mouse & keyboard activity running silently",
                font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK
            ).pack()
        else:
            tk.Label(
                self.win, text="\u26a0 pyautogui not installed \u2014 keep-alive disabled",
                font=("Segoe UI", 9), fg=YELLOW_ACCENT, bg=BG_DARK
            ).pack()

        self.time_label = tk.Label(
            self.win, text="Remaining: --:--:--",
            font=("Consolas", 16), fg=ACCENT, bg=BG_DARK
        )
        self.time_label.pack(pady=20)

        self.progress = ttk.Progressbar(
            self.win, length=380, mode="determinate",
            style="Active.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=(0, 8))

        # Live keep-alive activity readout
        self.stats_label = tk.Label(
            self.win, text="",
            font=("Consolas", 8), fg=TEXT_MUTED, bg=BG_DARK
        )
        self.stats_label.pack(pady=(0, 8))

        btn_frame = tk.Frame(self.win, bg=BG_DARK)
        btn_frame.pack(pady=(0, 5))

        tk.Button(
            btn_frame, text="MINIMIZE", font=("Segoe UI", 9, "bold"),
            bg="#1a2744", fg=ACCENT, relief="flat", padx=16, pady=4,
            command=lambda: self.win.iconify(), cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="STOP", font=("Segoe UI", 10, "bold"),
            bg="#2a1525", fg=RED_ACCENT, relief="flat", padx=20, pady=4,
            command=self._exit, cursor="hand2"
        ).pack(side="left")

    def _tick(self):
        if not self.running or not self.win.winfo_exists():
            return

        remaining = max(0, self.duration - (time.time() - self.start_time))
        total = self.duration
        pct = ((total - remaining) / total) * 100

        self.progress["value"] = pct
        td = str(timedelta(seconds=int(remaining)))
        self.time_label.config(text=f"Remaining: {td}")

        # Reflect the live keep-alive counters so the user can see it working
        if keep_alive.available:
            s = keep_alive.stats()
            self.stats_label.config(
                text=f"profile: {s['profile']}   mouse: {s['mouse_moves']}   "
                     f"keys: {s['key_presses']}   last: {s['last_action']}")
        else:
            self.stats_label.config(text="keep-alive disabled (pyautogui missing)")

        if remaining <= 0:
            self.time_label.config(text="Done!", fg=ACCENT)
            self.progress["value"] = 100
            keep_alive.stop()
            self.running = False
            # Auto-return to launcher after brief pause
            self.win.after(2000, self._exit)
            return

        self.win.after(1000, self._tick)

    def _exit(self):
        if not self.running and self.win.winfo_exists():
            # Natural completion path — just destroy and return
            self.win.destroy()
            self.on_exit()
            return
        self.running = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: CODE COMPILER / BUILD PIPELINE
# ═══════════════════════════════════════════════════════════════

class CodeBuildSimulation:
    """Fake developer build & test pipeline with a live scrolling console."""

    PACKAGES = [
        "react", "react-dom", "webpack", "babel-core", "typescript",
        "eslint", "jest", "lodash", "axios", "redux", "express",
        "tailwindcss", "vite", "rollup", "postcss", "prettier",
        "@types/node", "ts-loader", "sass", "chalk", "commander",
    ]

    MODULES = [
        "src/index.ts", "src/app.tsx", "src/store/reducer.ts",
        "src/components/Header.tsx", "src/components/Sidebar.tsx",
        "src/utils/format.ts", "src/api/client.ts", "src/hooks/useAuth.ts",
        "src/services/cache.ts", "src/models/user.ts", "src/router.tsx",
        "src/styles/theme.ts", "src/middleware/logger.ts", "src/db/pool.ts",
    ]

    TESTS = [
        "auth.service.spec", "user.model.spec", "format.util.spec",
        "cache.service.spec", "router.spec", "reducer.spec",
        "client.api.spec", "header.component.spec", "hooks.spec",
    ]

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()
        self.running = True

        self.win = tk.Toplevel(parent_root)
        self.win.title("Terminal — npm run build")
        self.win.geometry("1000x680")
        self.win.configure(bg="#0a0e17")
        self.win.protocol("WM_DELETE_WINDOW", self._exit)
        self.win.bind("<Escape>", lambda e: self._exit())

        self._build_ui()
        keep_alive.start()
        threading.Thread(target=self._build_loop, daemon=True).start()

    def _build_ui(self):
        title_frame = tk.Frame(self.win, bg="#0d1220", height=46)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame, text="⌨  build-pipeline — zsh",
            font=("Consolas", 13, "bold"), fg=PURPLE_ACCENT, bg="#0d1220"
        ).pack(side="left", padx=15, pady=10)

        self.stage_label = tk.Label(
            title_frame, text="initializing…",
            font=("Consolas", 11), fg=TEXT_SECONDARY, bg="#0d1220"
        )
        self.stage_label.pack(side="right", padx=15)

        prog_frame = tk.Frame(self.win, bg="#0a0e17", pady=6)
        prog_frame.pack(fill="x", padx=15)
        self.progress_bar = ttk.Progressbar(
            prog_frame, length=970, mode="determinate",
            style="Purple.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x")

        self.console = scrolledtext.ScrolledText(
            self.win, bg="#05080f", fg="#c8d3e6",
            font=("Consolas", 10), insertbackground=PURPLE_ACCENT,
            relief="flat", bd=0, highlightthickness=1,
            highlightcolor=BORDER, highlightbackground=BORDER,
        )
        self.console.pack(fill="both", expand=True, padx=15, pady=(4, 8))
        self.console.tag_configure("green", foreground=ACCENT)
        self.console.tag_configure("yellow", foreground=YELLOW_ACCENT)
        self.console.tag_configure("purple", foreground=PURPLE_ACCENT)
        self.console.tag_configure("cyan", foreground=CYAN_ACCENT)
        self.console.tag_configure("muted", foreground=TEXT_MUTED)
        self.console.tag_configure("white", foreground=TEXT_PRIMARY)
        self.console.tag_configure("red", foreground=RED_ACCENT)

        bottom = tk.Frame(self.win, bg="#0d1220", height=44)
        bottom.pack(fill="x")
        bottom.pack_propagate(False)
        tk.Button(
            bottom, text="STOP & EXIT", bg="#2a1525", fg=RED_ACCENT,
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
            padx=16, pady=4, cursor="hand2", command=self._exit
        ).pack(side="left", padx=15, pady=8)

    def _log(self, msg, tag="white"):
        self.console.insert("end", f"{msg}\n", tag)
        self.console.see("end")

    def _set_stage(self, text):
        try:
            self.stage_label.config(text=text)
        except Exception:
            pass

    def _emit(self, msg, tag="white"):
        """Thread-safe console write."""
        if not self.running:
            return
        try:
            _post(self.win, lambda: self._log(msg, tag))
        except Exception:
            pass

    def _set_progress(self, pct):
        try:
            _post(self.win, lambda: self.progress_bar.configure(value=pct))
        except Exception:
            pass

    def _build_loop(self):
        cycle = 0
        while self.running and time.time() - self.start_time < self.duration:
            cycle += 1
            self._emit(f"\n$ npm run build  — cycle #{cycle}", "purple")
            self._emit("", "muted")

            # Stage 1: install dependencies
            _post(self.win, lambda: self._set_stage("installing dependencies"))
            self._emit("> resolving dependency tree…", "muted")
            for pkg in random.sample(self.PACKAGES, random.randint(6, 11)):
                if not self.running:
                    return
                ver = f"{random.randint(1,18)}.{random.randint(0,20)}.{random.randint(0,30)}"
                self._emit(f"  + {pkg}@{ver}", "green")
                self._sleep(random.uniform(0.05, 0.18))
            self._emit("  added 312 packages in 4.7s", "muted")

            # Stage 2: compile modules
            _post(self.win, lambda: self._set_stage("compiling"))
            self._emit("\n> tsc --build", "cyan")
            for mod in random.sample(self.MODULES, random.randint(7, 12)):
                if not self.running:
                    return
                self._emit(f"  ✓ compiled {mod}", "white")
                self._sleep(random.uniform(0.08, 0.22))
            if random.random() < 0.4:
                self._emit("  ⚠ deprecation: 'componentWillMount' is deprecated", "yellow")

            # Stage 3: bundle
            _post(self.win, lambda: self._set_stage("bundling"))
            self._emit("\n> vite build", "cyan")
            for chunk in ["vendor", "main", "runtime", "polyfills", "styles"]:
                if not self.running:
                    return
                kb = random.randint(40, 980)
                self._emit(f"  dist/{chunk}.[hash].js   {kb:>4} KiB", "white")
                self._sleep(random.uniform(0.1, 0.3))
            self._emit("  built in 8.42s", "muted")

            # Stage 4: tests
            _post(self.win, lambda: self._set_stage("running tests"))
            self._emit("\n> jest --coverage", "cyan")
            passed = 0
            for spec in random.sample(self.TESTS, random.randint(5, 9)):
                if not self.running:
                    return
                n = random.randint(3, 12)
                passed += n
                self._emit(f"  PASS  {spec}  ({n} tests)", "green")
                self._sleep(random.uniform(0.12, 0.28))
            self._emit(f"\nTest Suites: all passed  —  Tests: {passed} passed", "green")
            cov = random.randint(82, 99)
            self._emit(f"Coverage: {cov}% statements  |  build OK ✨", "green")

            # Progress tracks elapsed/duration so it mirrors real runtime
            elapsed = time.time() - self.start_time
            self._set_progress(min(99, (elapsed / self.duration) * 100))
            self._emit("\n— watching for changes —", "muted")
            self._sleep(random.uniform(1.5, 3.5))

        if self.running:
            self._set_progress(100)
            _post(self.win, lambda: self._set_stage("done"))
            self._emit("\n✅ Pipeline finished cleanly.", "green")
            _post(self.win, self._exit, 3000)

    def _sleep(self, secs):
        """Interruptible sleep that bails out when stopped."""
        end = time.time() + secs
        while self.running and time.time() < end:
            time.sleep(0.03)

    def _exit(self):
        if not self.running:
            return
        self.running = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: AI MODEL TRAINING
# ═══════════════════════════════════════════════════════════════

class AITrainingSimulation:
    """Deep-learning training dashboard with live loss/accuracy curves."""

    MODELS = [
        "transformer-xl-1.3B", "resnet152-finetune", "bert-large-uncased",
        "gpt-neo-2.7B", "vit-h14", "stable-diffusion-unet", "yolo-v8x",
    ]
    DATASETS = ["ImageNet-21k", "C4-en", "LAION-400M", "COCO-2017",
                "OpenWebText", "WikiText-103", "Common Crawl"]

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()
        self.running = True
        self.model = random.choice(self.MODELS)
        self.dataset = random.choice(self.DATASETS)
        self.total_epochs = random.randint(40, 120)
        self.loss = random.uniform(4.0, 6.5)
        self.acc = random.uniform(0.05, 0.15)
        self.loss_history = []

        self.win = tk.Toplevel(parent_root)
        self.win.title(f"TrainerHub — {self.model}")
        self.win.geometry("1040x700")
        self.win.configure(bg="#0a0e17")
        self.win.protocol("WM_DELETE_WINDOW", self._exit)
        self.win.bind("<Escape>", lambda e: self._exit())

        self._build_ui()
        keep_alive.start()
        threading.Thread(target=self._train_loop, daemon=True).start()
        self._animate_layers()

    def _build_ui(self):
        header = tk.Frame(self.win, bg="#0d1220", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text=f"\U0001f9e0  TrainerHub  —  {self.model}",
            font=("Consolas", 14, "bold"), fg=MAGENTA_ACCENT, bg="#0d1220"
        ).pack(side="left", padx=15, pady=10)
        tk.Label(
            header, text=f"dataset: {self.dataset}",
            font=("Consolas", 10), fg=TEXT_SECONDARY, bg="#0d1220"
        ).pack(side="right", padx=15)

        # Metric cards
        metrics = tk.Frame(self.win, bg="#0a0e17")
        metrics.pack(fill="x", padx=15, pady=(10, 4))
        self.metric_labels = {}
        for key, title, color in [
            ("epoch", "EPOCH", CYAN_ACCENT), ("loss", "LOSS", RED_ACCENT),
            ("acc", "ACCURACY", ACCENT), ("lr", "LEARN RATE", YELLOW_ACCENT),
            ("gpu", "GPU UTIL", MAGENTA_ACCENT),
        ]:
            card = tk.Frame(metrics, bg="#131a2b", highlightbackground=BORDER,
                            highlightthickness=1)
            card.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(card, text=title, font=("Consolas", 8),
                     fg=TEXT_MUTED, bg="#131a2b").pack(anchor="w", padx=10, pady=(8, 0))
            val = tk.Label(card, text="—", font=("Consolas", 18, "bold"),
                           fg=color, bg="#131a2b")
            val.pack(anchor="w", padx=10, pady=(0, 8))
            self.metric_labels[key] = val

        # Loss curve canvas
        tk.Label(self.win, text="TRAINING LOSS", font=("Consolas", 8),
                 fg=TEXT_MUTED, bg="#0a0e17").pack(anchor="w", padx=18, pady=(8, 0))
        self.curve = tk.Canvas(self.win, height=180, bg="#05080f",
                               highlightthickness=1, highlightbackground=BORDER)
        self.curve.pack(fill="x", padx=15, pady=(2, 8))

        # Layer activation bars
        tk.Label(self.win, text="LAYER ACTIVATIONS", font=("Consolas", 8),
                 fg=TEXT_MUTED, bg="#0a0e17").pack(anchor="w", padx=18)
        self.layers = tk.Canvas(self.win, height=120, bg="#05080f",
                                highlightthickness=1, highlightbackground=BORDER)
        self.layers.pack(fill="x", padx=15, pady=(2, 8))

        # Overall progress + log
        self.progress_bar = ttk.Progressbar(
            self.win, length=1010, mode="determinate",
            style="Magenta.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 6))

        self.log = scrolledtext.ScrolledText(
            self.win, bg="#05080f", fg=TEXT_SECONDARY, height=6,
            font=("Consolas", 9), relief="flat", bd=0,
            highlightthickness=1, highlightcolor=BORDER,
            highlightbackground=BORDER,
        )
        self.log.pack(fill="both", expand=True, padx=15, pady=(0, 6))
        self.log.tag_configure("magenta", foreground=MAGENTA_ACCENT)
        self.log.tag_configure("green", foreground=ACCENT)
        self.log.tag_configure("muted", foreground=TEXT_MUTED)

        bottom = tk.Frame(self.win, bg="#0d1220", height=42)
        bottom.pack(fill="x")
        bottom.pack_propagate(False)
        tk.Button(
            bottom, text="STOP & EXIT", bg="#2a1525", fg=RED_ACCENT,
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
            padx=16, pady=4, cursor="hand2", command=self._exit
        ).pack(side="left", padx=15, pady=7)

    def _animate_layers(self):
        """Continuously redraw the layer-activation bar chart on the UI thread."""
        if not self.running or not self.win.winfo_exists():
            return
        try:
            c = self.layers
            c.delete("all")
            w = c.winfo_width() or 1000
            h = c.winfo_height() or 120
            n = 32
            bw = w / n
            for i in range(n):
                val = abs(math.sin(time.time() * 1.5 + i * 0.4)) * random.uniform(0.3, 1.0)
                bh = val * (h - 8)
                x = i * bw
                shade = "#%02x%02x%02x" % (
                    int(80 + val * 120), int(40 + val * 60), int(140 + val * 100))
                c.create_rectangle(x + 1, h - bh, x + bw - 1, h, fill=shade, outline="")
        except Exception:
            pass
        self.win.after(120, self._animate_layers)

    def _draw_curve(self):
        try:
            c = self.curve
            c.delete("all")
            w = c.winfo_width() or 1000
            h = c.winfo_height() or 180
            if len(self.loss_history) < 2:
                return
            hi = max(self.loss_history)
            lo = min(self.loss_history)
            rng = (hi - lo) or 1
            pts = []
            n = len(self.loss_history)
            for i, v in enumerate(self.loss_history):
                x = (i / (n - 1)) * (w - 10) + 5
                y = h - 10 - ((v - lo) / rng) * (h - 20)
                pts.extend([x, y])
            if len(pts) >= 4:
                c.create_line(*pts, fill=RED_ACCENT, width=2, smooth=True)
        except Exception:
            pass

    def _log(self, msg, tag="muted"):
        try:
            self.log.insert("end", f"{msg}\n", tag)
            self.log.see("end")
        except Exception:
            pass

    def _train_loop(self):
        _post(self.win, lambda: self._log(
            f"Initializing {self.model} on 8× A100  —  {self.total_epochs} epochs", "magenta"))
        epoch = 0
        while self.running and time.time() - self.start_time < self.duration:
            elapsed = time.time() - self.start_time
            frac = min(0.999, elapsed / self.duration)
            epoch = int(frac * self.total_epochs) + 1

            # Loss decays toward a small floor; accuracy climbs toward ~0.99
            target_loss = 0.08 + (1 - frac) ** 1.6 * 5.5
            self.loss += (target_loss - self.loss) * 0.3 + random.uniform(-0.04, 0.04)
            self.loss = max(0.03, self.loss)
            target_acc = 0.99 - (1 - frac) ** 1.4 * 0.9
            self.acc += (target_acc - self.acc) * 0.3 + random.uniform(-0.005, 0.005)
            self.acc = min(0.999, max(0.0, self.acc))
            lr = 3e-4 * (0.5 ** (epoch / 20))
            gpu = random.randint(91, 100)

            self.loss_history.append(self.loss)
            if len(self.loss_history) > 120:
                self.loss_history.pop(0)

            # Snapshot values as default args so the UI-thread callback shows the
            # state from this iteration, not whatever the worker has moved on to.
            def update(epoch=epoch, loss=self.loss, acc=self.acc,
                       lr=lr, gpu=gpu, frac=frac):
                if not self.running:
                    return
                self.metric_labels["epoch"].config(text=f"{epoch}/{self.total_epochs}")
                self.metric_labels["loss"].config(text=f"{loss:.4f}")
                self.metric_labels["acc"].config(text=f"{acc*100:.2f}%")
                self.metric_labels["lr"].config(text=f"{lr:.1e}")
                self.metric_labels["gpu"].config(text=f"{gpu}%")
                self.progress_bar.configure(value=frac * 100)
                self._draw_curve()
            try:
                _post(self.win, update)
            except Exception:
                return

            if random.random() < 0.5:
                step = random.randint(100, 9000)
                _post(self.win, lambda e=epoch, ls=self.loss, ac=self.acc, s=step:
                    self._log(f"epoch {e:>3}  step {s:>5}  loss {ls:.4f}  acc {ac*100:.2f}%"))
            if random.random() < 0.08:
                _post(self.win, lambda: self._log(
                    "  checkpoint saved → ckpt/epoch_latest.pt", "green"))

            time.sleep(random.uniform(0.4, 1.1))

        if self.running:
            _post(self.win, lambda: self._log(
                "✅ Training complete — best model exported.", "green"))
            _post(self.win, lambda: self.progress_bar.configure(value=100))
            _post(self.win, self._exit, 3000)

    def _exit(self):
        if not self.running:
            return
        self.running = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: MATRIX DIGITAL RAIN
# ═══════════════════════════════════════════════════════════════

class MatrixRainSimulation:
    """Fullscreen cascading green digital rain (Matrix screensaver style)."""

    GLYPHS = (string.ascii_letters + string.digits +
              "アイウエオカキクケコ"
              "サシスセソ¥#@%&*+<>=")
    # Trail brightness shades, dimmest -> brightest (head is MATRIX_GREEN)
    SHADES = ["#063b16", "#0a5a22", "#10883a", "#1fc24d", "#5dff8f"]

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()
        self.running = True
        self.font_size = 16
        self.cell = self.font_size + 2
        self.trail = 16

        self.win = tk.Toplevel(parent_root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="black")
        self.win.config(cursor="none")
        self.win.focus_force()
        self.win.bind("<Escape>", self._exit)
        self.win.protocol("WM_DELETE_WINDOW", self._exit)

        self.canvas = tk.Canvas(self.win, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # ESC hint, fades into the rain
        tk.Label(self.win, text="Press ESC to exit",
                 font=("Consolas", 9), fg="#0a5a22", bg="black").place(
            relx=0.5, rely=0.98, anchor="center")

        self.win.after(60, self._setup_columns)
        keep_alive.start()
        self.win.after(120, self._tick)

    def _setup_columns(self):
        self.win.update_idletasks()
        w = self.win.winfo_width() or 1280
        h = self.win.winfo_height() or 720
        self.rows = max(8, h // self.cell)
        self.cols = max(8, w // self.cell)
        # Each column: head row (float) + falling speed
        self.heads = [random.uniform(-self.rows, 0) for _ in range(self.cols)]
        self.speeds = [random.uniform(0.4, 1.4) for _ in range(self.cols)]

    def _rand_glyph(self):
        return random.choice(self.GLYPHS)

    def _tick(self):
        if not self.running or not self.win.winfo_exists():
            return

        # Auto-exit when duration expires
        if time.time() - self.start_time >= self.duration:
            self._exit()
            return

        if not hasattr(self, "heads"):
            self.win.after(60, self._tick)
            return

        c = self.canvas
        c.delete("all")
        font = ("Consolas", self.font_size, "bold")
        for col in range(self.cols):
            head = self.heads[col]
            x = col * self.cell + self.cell // 2
            for t in range(self.trail):
                row = int(head) - t
                if row < 0 or row >= self.rows:
                    continue
                y = row * self.cell + self.cell // 2
                if t == 0:
                    color = "#ffffff"  # bright leading char
                elif t == 1:
                    color = MATRIX_GREEN
                else:
                    idx = max(0, len(self.SHADES) - 1 - (t // 3))
                    color = self.SHADES[idx]
                c.create_text(x, y, text=self._rand_glyph(),
                              fill=color, font=font)
            # Advance head; reset to top once fully off-screen
            self.heads[col] += self.speeds[col]
            if self.heads[col] - self.trail > self.rows:
                self.heads[col] = random.uniform(-6, 0)
                self.speeds[col] = random.uniform(0.4, 1.4)

        self.win.after(55, self._tick)

    def _exit(self, event=None):
        if not self.running or not self.win.winfo_exists():
            return
        self.running = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: THE BI TRAINER
# ═══════════════════════════════════════════════════════════════

# Series palette used by every chart renderer in the BI Trainer.
BI_PALETTE = [BLUE_ACCENT, ACCENT, YELLOW_ACCENT, MAGENTA_ACCENT,
              ORANGE_ACCENT, CYAN_ACCENT, PURPLE_ACCENT, RED_ACCENT]

BI_PLOT_BG = "#05080f"
BI_PANEL_BG = "#0b111d"
BI_GRID = "#132038"
BI_AXIS = "#20304e"

# Chatter appended to the insight feed between lesson takeaways so the
# console keeps scrolling even in the quiet gaps of a lesson.
BI_FEED_CHATTER = [
    "grain check: fact_sales is one row per order line — never per order",
    "semantic model refreshed  •  12 tables  •  4.2M rows  •  38s",
    "SELECT is fine; the joins are what change your denominator",
    "measure [Revenue YoY %] = DIVIDE([Revenue] - [Revenue LY], [Revenue LY])",
    "filter context beats row context — always check what the visual is slicing",
    "null ≠ 0: a missing month is a gap in the line, not a drop to zero",
    "averages hide the distribution; always look at the spread before you act",
    "correlation checked against a lagged series — no causal claim made",
    "seasonality flagged: December spike repeats in 3 of 3 prior years",
    "sample size on this slice is n=14 — treat the % as directional only",
    "row-level security applied: viewer sees their region only",
    "cardinality warning: 1.2M distinct values on a slicer field",
    "outlier retained (not dropped) and annotated on the visual",
    "comparing like-for-like: both periods normalised to 30 days",
    "definition locked: 'active user' = ≥1 session in trailing 28 days",
]

BI_LESSONS = [
    {
        "chart": "bar",
        "title": "Column / Bar Chart",
        "family": "COMPARISON",
        "question": "Which categories are biggest — and by how much?",
        "read": [
            "Rank before you read. Sort descending unless the axis has a natural"
            " order (time, size bands, survey scale).",
            "Judge by bar LENGTH, so the value axis must start at zero. A truncated"
            " baseline turns a 4% gap into a visual landslide.",
            "Compare the top bar to the MEDIAN bar, not to the total — that gap is"
            " the one you can actually act on.",
            "Keep it under ~12 bars. Roll the tail into 'Other' or switch to a"
            " table with in-cell bars.",
            "Horizontal bars when labels are long; vertical columns when the"
            " category is time-like.",
        ],
        "pitfall": "Non-zero baselines and 3-D bars are the two fastest ways to lie with a column chart.",
        "lang": "SQL  ·  warehouse aggregate",
        "code": """-- Revenue by region, ranked. Aggregate BEFORE you visualise:
-- let the warehouse do the grouping, not the BI tool.
SELECT
    r.region_name                        AS region,
    SUM(f.net_revenue)                   AS revenue,
    COUNT(DISTINCT f.order_id)           AS orders,
    SUM(f.net_revenue)
      / NULLIF(COUNT(DISTINCT f.order_id), 0) AS avg_order_value
FROM   fact_sales      f
JOIN   dim_region      r ON r.region_id = f.region_id
WHERE  f.order_date >= DATE_TRUNC('quarter', CURRENT_DATE)
  AND  f.is_returned = FALSE          -- exclude returns, or AOV lies
GROUP  BY r.region_name
ORDER  BY revenue DESC;""",
        "insights": [
            "top region leads the median by 1.7x — that is the actionable gap",
            "bars sorted descending; axis pinned to zero for honest length ratios",
            "returns excluded at source, so AOV is not inflated",
        ],
    },
    {
        "chart": "line",
        "title": "Line Chart",
        "family": "TREND OVER TIME",
        "question": "Which way is this moving, and is the move real?",
        "read": [
            "Read the SLOPE, not the last point. One high dot is noise; a sustained"
            " change of slope is a trend.",
            "Always plot enough history to see the previous cycle — 13 months beats"
            " 3 months for anything seasonal.",
            "A zero baseline is optional here (you are reading change, not size) —"
            " but say so on the axis.",
            "Overlay last year, or a rolling 7/28-day average, to separate the"
            " signal from the weekly saw-tooth.",
            "Gaps mean missing data. Never connect across a gap — that invents a"
            " trend nobody measured.",
        ],
        "pitfall": "More than ~5 lines is spaghetti. Small multiples beat a crowded single axis every time.",
        "lang": "Python  ·  pandas rolling window",
        "code": """import pandas as pd

df = pd.read_parquet("daily_revenue.parquet")
df["date"] = pd.to_datetime(df["date"])

# Reindex to a complete calendar so missing days stay VISIBLE as gaps
full = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
s = df.set_index("date")["revenue"].reindex(full)

trend = pd.DataFrame({
    "actual":   s,
    "ma_7":     s.rolling(7,  min_periods=7).mean(),   # weekly noise out
    "ma_28":    s.rolling(28, min_periods=28).mean(),  # true direction
    "yoy_pct":  s.pct_change(365) * 100,
})
print(trend.tail(10))""",
        "insights": [
            "28-day average is still climbing while dailies wobble — trend holds",
            "calendar reindexed: two missing days render as gaps, not as zeros",
            "YoY comparison aligned on day-of-week to kill the saw-tooth",
        ],
    },
    {
        "chart": "stacked_area",
        "title": "Stacked Area",
        "family": "COMPOSITION OVER TIME",
        "question": "Is the mix changing while the total grows?",
        "read": [
            "Only the BOTTOM band sits on a flat baseline. Every band above it"
            " rides on the ones below, so read totals, not individual shapes.",
            "The top edge is the total. If you need each segment's own trend, use"
            " small multiples or unstack to lines.",
            "Switch to 100%-stacked when the question is share-of-mix; keep it"
            " absolute when the question is growth.",
            "Order the bands: biggest and most stable at the bottom, volatile at"
            " the top, so the noise does not shake everything.",
            "3–5 bands maximum. Anything more and the middle becomes unreadable.",
        ],
        "pitfall": "Readers routinely misjudge a middle band as shrinking when the band below it merely grew.",
        "lang": "Power Query  ·  M — unpivot to tidy shape",
        "code": """let
    Source   = Sql.Database("dw-prod", "analytics"),
    Revenue  = Source{[Schema="mart", Item="revenue_by_segment"]}[Data],

    // BI tools want TIDY data: one row per (period, segment, value)
    Unpivot  = Table.UnpivotOtherColumns(
                   Revenue, {"month"}, "segment", "revenue"),

    Typed    = Table.TransformColumnTypes(Unpivot, {
                   {"month",   type date},
                   {"segment", type text},
                   {"revenue", Currency.Type}}),

    // Stable band order — biggest / steadiest at the bottom
    Ranked   = Table.AddColumn(Typed, "sort_order", each
                   if [segment] = "Enterprise"  then 1
                   else if [segment] = "Mid-Market" then 2
                   else 3, Int64.Type)
in
    Ranked""",
        "insights": [
            "total is up 22% but SMB share fell 9pts — growth is mix-driven",
            "bands ordered by stability so the volatile segment sits on top",
            "unpivoted to tidy rows: one record per month per segment",
        ],
    },
    {
        "chart": "donut",
        "title": "Donut / Pie",
        "family": "PART-TO-WHOLE",
        "question": "How is one total split, right now?",
        "read": [
            "Use it only when the slices sum to a meaningful 100% of ONE total at"
            " ONE point in time.",
            "Humans compare angles badly. Print the % on every slice or don't"
            " bother with the chart.",
            "Keep to ≤5 slices, ordered largest-first from 12 o'clock clockwise.",
            "Never use two pies to compare periods — a bar chart of the same"
            " splits answers that far faster.",
            "The hole in a donut is free real estate: put the total in it.",
        ],
        "pitfall": "If any slice is 'Other' at 30%, the chart is hiding the actual answer.",
        "lang": "DAX  ·  share-of-total measure",
        "code": """-- Share of total that RESPECTS the visual's filter context
Revenue = SUM ( fact_sales[net_revenue] )

Revenue % of Total =
VAR CurrentRevenue = [Revenue]
VAR TotalRevenue =
    CALCULATE (
        [Revenue],
        REMOVEFILTERS ( dim_product[category] )   -- denominator = the whole
    )
RETURN
    DIVIDE ( CurrentRevenue, TotalRevenue )       -- DIVIDE, never "/"

-- Guard the long tail so the donut never grows a 6th slice
Category Label =
IF ( [Revenue % of Total] < 0.03, "Other", SELECTEDVALUE ( dim_product[category] ) )""",
        "insights": [
            "5 slices, labelled, largest-first — angles never read alone",
            "REMOVEFILTERS fixes the denominator to the true whole",
            "tail below 3% folded into 'Other' to keep the split legible",
        ],
    },
    {
        "chart": "scatter",
        "title": "Scatter Plot",
        "family": "RELATIONSHIP",
        "question": "Do these two measures move together?",
        "read": [
            "Shape first: tight band = strong relationship, cloud = none, curve ="
            " a real relationship your linear fit will miss.",
            "Direction is the sign, tightness is the strength. Report r AND the"
            " sample size — r = 0.9 on n = 5 is nothing.",
            "Look for clusters and outliers before you trust the trend line; two"
            " groups can fake a slope that neither has.",
            "Correlation is not causation, and a lagged variable often explains"
            " both. Say which way you think it runs and why.",
            "Size or colour a third measure only if it is genuinely ordinal.",
        ],
        "pitfall": "Simpson's paradox: the overall slope can point the opposite way to every subgroup's slope.",
        "lang": "Python  ·  correlation with the caveats attached",
        "code": """import numpy as np, pandas as pd
from scipy import stats

d = df.dropna(subset=["ad_spend", "revenue"])
r, p = stats.pearsonr(d["ad_spend"], d["revenue"])
slope, intercept = np.polyfit(d["ad_spend"], d["revenue"], 1)

print(f"n = {len(d):,}   r = {r:.2f}   p = {p:.4f}")
print(f"fit: revenue = {slope:.2f} * spend + {intercept:,.0f}")

# Check every subgroup before believing the pooled slope (Simpson's paradox)
for seg, g in d.groupby("segment"):
    if len(g) > 30:
        rs, _ = stats.pearsonr(g["ad_spend"], g["revenue"])
        print(f"  {seg:<12} n={len(g):>5}  r={rs:+.2f}")""",
        "insights": [
            "r = +0.71 on n = 240 — strong, and every subgroup agrees in sign",
            "two outliers annotated, not deleted; both are real campaign spikes",
            "fit is linear and the cloud is linear — no curve being flattened",
        ],
    },
    {
        "chart": "histogram",
        "title": "Histogram",
        "family": "DISTRIBUTION",
        "question": "What does the spread look like behind the average?",
        "read": [
            "Find the SHAPE: one peak, two peaks, or a long tail. Two peaks means"
            " you are averaging two different populations.",
            "Skew moves the mean away from the median. When they disagree, quote"
            " the median and say so.",
            "Bin width is a decision, not a default. Too wide hides the shape, too"
            " narrow turns it into noise — try a few.",
            "The x-axis is a measure here, not a category, so the bars touch. Gaps"
            " between bars mean gaps in the data.",
            "Read the tail deliberately: p95 and p99 are where SLAs and complaints"
            " live.",
        ],
        "pitfall": "'Average order value' on a bimodal distribution describes a customer who does not exist.",
        "lang": "SQL  ·  bins and percentiles together",
        "code": """-- Distribution + the percentiles you will be asked about anyway
WITH binned AS (
    SELECT
        WIDTH_BUCKET(order_value, 0, 500, 20) AS bin,
        order_value
    FROM fact_sales
    WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT
    bin * 25                          AS bin_floor,
    COUNT(*)                          AS orders,
    ROUND(AVG(order_value), 2)        AS mean_in_bin
FROM binned
GROUP BY bin
ORDER BY bin;

SELECT
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY order_value) AS p50,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY order_value) AS p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY order_value) AS p99,
    AVG(order_value)                                          AS mean
FROM fact_sales;""",
        "insights": [
            "mean sits 18% above the median — right-skewed, quote the median",
            "single clean peak: one population, so the average is meaningful",
            "p95 is 3.1x the median — that tail is where the escalations come from",
        ],
    },
    {
        "chart": "heatmap",
        "title": "Heatmap Matrix",
        "family": "PATTERN / DENSITY",
        "question": "Where do two dimensions intersect most intensely?",
        "read": [
            "Scan for BLOCKS and STRIPES, not single cells. A bright row is a"
            " pattern; a bright cell is an anecdote.",
            "The colour scale is the whole chart. Sequential for magnitude,"
            " diverging (with a fixed midpoint) for above/below target.",
            "Keep the scale stable across refreshes or last week's 'hot' is this"
            " week's 'cold' with no data change.",
            "Sort rows and columns by total, or by a clustering, so the structure"
            " lines up instead of scattering.",
            "Always print a legend with real units — colour alone has no scale.",
        ],
        "pitfall": "Rainbow palettes invent boundaries that are not in the data. Use one hue, varying in lightness.",
        "lang": "Python  ·  pivot to a matrix",
        "code": """# Sessions by day-of-week x hour — the classic operations heatmap
matrix = (
    events
      .assign(dow  = events["ts"].dt.day_name(),
              hour = events["ts"].dt.hour)
      .pivot_table(index="dow", columns="hour",
                   values="session_id", aggfunc="nunique", fill_value=0)
      .reindex(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])   # keep real order
)

# Fix the scale ACROSS refreshes so colour stays comparable week to week
vmin, vmax = 0, matrix.to_numpy().max()
ax = sns.heatmap(matrix, cmap="mako", vmin=vmin, vmax=vmax,
                 cbar_kws={"label": "unique sessions"})
ax.set_title("Sessions by day and hour")""",
        "insights": [
            "the hot block is Tue–Thu 09:00–11:00 — that is a staffing decision",
            "single hue, fixed vmin/vmax: colour means the same thing every week",
            "weekend rows are uniformly cold — not missing data, genuinely quiet",
        ],
    },
    {
        "chart": "box",
        "title": "Box & Whisker",
        "family": "SPREAD & OUTLIERS",
        "question": "How consistent is each group, not just how high?",
        "read": [
            "The box is the middle 50% (Q1→Q3). The line inside it is the MEDIAN,"
            " never the mean.",
            "Box height is consistency. A short box with a high median beats a tall"
            " box with the same median — it's predictable.",
            "Whiskers reach the furthest point within 1.5x IQR; dots beyond them"
            " are candidate outliers, not errors.",
            "Compare medians across groups first, then compare spreads. A shifted"
            " median with identical spread is a clean, real difference.",
            "Overlay the raw points when n is small — a box on n = 6 hides more"
            " than it shows.",
        ],
        "pitfall": "Two groups can share a median and behave nothing alike. Never quote the median alone.",
        "lang": "SQL  ·  quartiles per group",
        "code": """-- The five numbers behind every box, per group
SELECT
    region,
    COUNT(*)                                                     AS n,
    MIN(delivery_days)                                           AS min_days,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY delivery_days)  AS q1,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY delivery_days)  AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY delivery_days)  AS q3,
    MAX(delivery_days)                                           AS max_days,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY delivery_days)
      - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY delivery_days) AS iqr
FROM fact_delivery
WHERE ship_date >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY region
HAVING COUNT(*) >= 30          -- do not draw a box on a handful of rows
ORDER BY median;""",
        "insights": [
            "same median, double the IQR: that region is unpredictable, not slower",
            "outlier dots kept and labelled — they are the SLA breaches",
            "groups with n < 30 suppressed rather than drawn misleadingly",
        ],
    },
    {
        "chart": "waterfall",
        "title": "Waterfall (Bridge)",
        "family": "CONTRIBUTION TO CHANGE",
        "question": "What actually moved the number between the two periods?",
        "read": [
            "Read it as a sentence: start, plus these, minus those, equals end.",
            "Bar SIZE is contribution magnitude; colour is only the sign. Keep"
            " sign colours consistent everywhere.",
            "Order the middle bars largest-to-smallest so the top two or three"
            " drivers explain most of the move.",
            "The bars must reconcile exactly to the ending total. If they don't,"
            " you have a missing driver, not a rounding issue.",
            "Fold trivia into 'Other', but only after the top drivers are clear.",
        ],
        "pitfall": "A bridge that doesn't reconcile is worse than no bridge — it looks authoritative and isn't.",
        "lang": "DAX  ·  variance decomposition",
        "code": """Revenue LY = CALCULATE ( [Revenue], SAMEPERIODLASTYEAR ( dim_date[date] ) )

-- Split the move into price vs volume vs mix — one driver per bar
Volume Effect =
    ( [Units] - [Units LY] ) * [Avg Price LY]

Price Effect =
    ( [Avg Price] - [Avg Price LY] ) * [Units LY]

Mix Effect =
    ( [Units] - [Units LY] ) * ( [Avg Price] - [Avg Price LY] )

-- Reconciliation guard: this MUST be zero or the bridge is lying
Bridge Check =
    [Revenue] - ( [Revenue LY] + [Volume Effect] + [Price Effect] + [Mix Effect] )""",
        "insights": [
            "volume explains 62% of the move; price is a distant second",
            "bridge check returns 0.00 — the bars reconcile to the ending total",
            "one negative driver, isolated and named, instead of buried in a net",
        ],
    },
    {
        "chart": "funnel",
        "title": "Conversion Funnel",
        "family": "PROCESS DROP-OFF",
        "question": "Where are we losing people between the steps?",
        "read": [
            "Read the GAPS between stages, not the widths. The biggest percentage"
            " drop is the story, wherever it sits.",
            "Quote two rates per stage: step conversion (from the previous stage)"
            " and overall (from the top).",
            "Stages must be strictly sequential and mutually exclusive, or the"
            " funnel double-counts.",
            "Fix the cohort. Everyone in the funnel must have had time to reach the"
            " last stage, or the bottom looks falsely narrow.",
            "A wide top is not success. Cheap traffic that never converts just"
            " flatters stage one.",
        ],
        "pitfall": "Mixing a 30-day cohort with a 3-day one makes the final stage collapse for purely mechanical reasons.",
        "lang": "SQL  ·  cohort-safe funnel",
        "code": """-- One row per user, first timestamp per stage, ONE fixed cohort
WITH cohort AS (
    SELECT user_id, MIN(ts) AS entered_at
    FROM   events
    WHERE  event_name = 'visit'
      AND  ts >= CURRENT_DATE - INTERVAL '60 days'
      AND  ts <  CURRENT_DATE - INTERVAL '30 days'   -- 30d to complete
    GROUP  BY user_id
),
stages AS (
    SELECT
        c.user_id,
        MIN(CASE WHEN e.event_name = 'signup' THEN e.ts END) AS signed_up,
        MIN(CASE WHEN e.event_name = 'trial'  THEN e.ts END) AS trialled,
        MIN(CASE WHEN e.event_name = 'paid'   THEN e.ts END) AS paid
    FROM cohort c
    LEFT JOIN events e
           ON e.user_id = c.user_id
          AND e.ts BETWEEN c.entered_at AND c.entered_at + INTERVAL '30 days'
    GROUP BY c.user_id
)
SELECT COUNT(*)                                    AS visited,
       COUNT(signed_up)                            AS signed_up,
       COUNT(trialled)                             AS trialled,
       COUNT(paid)                                 AS paid,
       ROUND(100.0 * COUNT(paid) / COUNT(*), 2)    AS overall_pct
FROM stages;""",
        "insights": [
            "biggest drop is signup → trial at -58% — that is the fix, not the top",
            "cohort closed 30 days ago so every user had time to convert",
            "stages exclusive: a user counts once, at their first occurrence",
        ],
    },
    {
        "chart": "pareto",
        "title": "Pareto Chart",
        "family": "PRIORITISATION",
        "question": "Which few causes account for most of the effect?",
        "read": [
            "Bars descending, cumulative % line on the secondary axis, 80% marked"
            " with a reference line.",
            "Read across to where the line crosses 80%: everything left of that is"
            " your working list.",
            "The 80/20 split is an observation, not a law. Sometimes it is 60/20 —"
            " report what you actually see.",
            "Weight by IMPACT (cost, hours, revenue at risk), not by ticket count,"
            " or you optimise for the cheap and frequent.",
            "Re-run it after you fix the top cause. The tail reshuffles and the"
            " next Pareto is a different chart.",
        ],
        "pitfall": "Counting incidents instead of costing them makes the noisiest category look like the most expensive.",
        "lang": "Python  ·  cumulative share",
        "code": """cause = (
    tickets.groupby("root_cause")
           .agg(incidents=("id", "count"),
                cost=("cost_usd", "sum"))       # weight by IMPACT, not count
           .sort_values("cost", ascending=False)
)
cause["cum_pct"] = 100 * cause["cost"].cumsum() / cause["cost"].sum()

vital_few = cause[cause["cum_pct"] <= 80]
print(f"{len(vital_few)} of {len(cause)} causes carry "
      f"{cause['cum_pct'].iloc[len(vital_few) - 1]:.0f}% of total cost")
print(vital_few.round(0))""",
        "insights": [
            "3 of 8 causes carry 79% of the cost — that is the sprint backlog",
            "weighted by cost: the most frequent cause ranks fourth by impact",
            "cumulative line crosses 80% at cause #3, marked on the axis",
        ],
    },
    {
        "chart": "kpi",
        "title": "KPI Tiles + Sparklines",
        "family": "EXECUTIVE SUMMARY",
        "question": "Is this number good, and compared to what?",
        "read": [
            "A number alone is meaningless. Every tile needs a comparison: target,"
            " last period, or same period last year.",
            "The sparkline supplies the context the big number destroys — it shows"
            " whether you are at a peak or a plateau.",
            "Colour by DIRECTION OF GOODNESS, not by sign. Falling churn is green.",
            "State the grain and the as-of time on the tile. 'Revenue' with no"
            " period is a support ticket waiting to happen.",
            "Four to six tiles. A dashboard of twenty tiles is a table with worse"
            " typography.",
        ],
        "pitfall": "A green delta on a 2% sample is noise wearing a badge. Show n, or suppress the tile.",
        "lang": "DAX  ·  KPI with target and trend",
        "code": """Revenue MTD =
    CALCULATE ( [Revenue], DATESMTD ( dim_date[date] ) )

Revenue MTD LY =
    CALCULATE ( [Revenue MTD], SAMEPERIODLASTYEAR ( dim_date[date] ) )

Revenue MTD YoY % =
    DIVIDE ( [Revenue MTD] - [Revenue MTD LY], [Revenue MTD LY] )

-- Direction of goodness, not sign: churn falling is GOOD
KPI Status =
VAR Delta   = [Revenue MTD YoY %]
VAR Target  = 0.05
RETURN
    SWITCH ( TRUE (),
        Delta >= Target,     "on-track",
        Delta >= 0,          "watch",
                             "off-track" )""",
        "insights": [
            "every tile carries a comparison — target, prior period, or LY",
            "sparkline shows this peak is the third of the quarter, not a first",
            "delta suppressed where n < 30 instead of shown in confident green",
        ],
    },
]


def _bi_mix(c1, c2, t):
    """Blend two ``#rrggbb`` colours; ``t`` runs 0.0 (c1) → 1.0 (c2)."""
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class BITrainerSimulation:
    """THE BI TRAINER — a scrolling business-intelligence chart clinic.

    Cycles through a deck of chart types. Each lesson draws a live, animated
    example of the chart, reveals a "how to read it" panel one rule at a time,
    types out the query/measure code that produces it, and streams analyst
    commentary into an insight feed. Auto-advances, or drive it manually with
    the PREV / NEXT / PAUSE controls.
    """

    LESSON_SECONDS = 18       # auto-advance interval
    ENTRANCE_SECONDS = 0.9    # chart draw-on animation
    FRAME_MS = 60             # redraw cadence
    RULE_MS = 900             # gap between revealed interpretation rules
    CODE_MS = 85              # per-line typing speed for the code panel

    def __init__(self, parent_root, on_exit, duration_hours=2):
        self.on_exit = on_exit
        self.duration = duration_hours * 3600
        self.start_time = time.time()
        self.running = True
        self.paused = False
        self.pause_started = 0.0
        self.paused_total = 0.0

        self.index = 0
        self.generation = 0
        self.lesson_t0 = time.time()
        self.data = {}

        self.win = tk.Toplevel(parent_root)
        self.win.title("THE BI TRAINER — Business Intelligence Chart Clinic")
        self.win.geometry("1240x820")
        self.win.configure(bg="#070b14")
        self.win.protocol("WM_DELETE_WINDOW", self._exit)
        self.win.bind("<Escape>", lambda e: self._exit())
        self.win.bind("<Right>", lambda e: self._next())
        self.win.bind("<Left>", lambda e: self._prev())
        self.win.bind("<space>", lambda e: self._toggle_pause())

        self._build_ui()
        keep_alive.start()
        self._load_lesson(0)
        self._tick()
        self._feed_loop()

    # ── UI construction ────────────────────────────────────────

    def _build_ui(self):
        header = tk.Frame(self.win, bg="#0c1322", height=54)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="\U0001f4ca  THE BI TRAINER",
            font=("Segoe UI", 15, "bold"), fg=BLUE_ACCENT, bg="#0c1322"
        ).pack(side="left", padx=(16, 8), pady=12)
        tk.Label(
            header, text="Chart types, code, and how to read the data",
            font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg="#0c1322"
        ).pack(side="left", pady=14)

        self.clock_label = tk.Label(
            header, text="--:--:--", font=("Consolas", 11),
            fg=TEXT_SECONDARY, bg="#0c1322"
        )
        self.clock_label.pack(side="right", padx=16)
        self.lesson_label = tk.Label(
            header, text="", font=("Consolas", 10, "bold"),
            fg=CYAN_ACCENT, bg="#0c1322"
        )
        self.lesson_label.pack(side="right", padx=8)

        body = tk.Frame(self.win, bg="#070b14")
        body.pack(fill="both", expand=True, padx=14, pady=(10, 4))

        # ── Right column: interpretation + code ──
        right = tk.Frame(body, bg="#070b14", width=520)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        tk.Label(right, text="HOW TO READ IT", font=("Consolas", 8, "bold"),
                 fg=TEXT_MUTED, bg="#070b14").pack(anchor="w")
        self.read_text = tk.Text(
            right, bg=BI_PANEL_BG, fg=TEXT_PRIMARY, height=15, width=52,
            font=("Segoe UI", 9), relief="flat", bd=0, wrap="word",
            padx=12, pady=10, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=BORDER,
            spacing1=2, spacing3=6, cursor="arrow",
        )
        self.read_text.pack(fill="both", expand=True, pady=(3, 8))
        self.read_text.tag_configure("bullet", foreground=CYAN_ACCENT,
                                     font=("Segoe UI", 9, "bold"))
        self.read_text.tag_configure("rule", foreground=TEXT_PRIMARY)
        self.read_text.tag_configure("warn", foreground=ORANGE_ACCENT,
                                     font=("Segoe UI", 9, "italic"))
        self.read_text.config(state="disabled")

        self.code_lang_label = tk.Label(
            right, text="CODE", font=("Consolas", 8, "bold"),
            fg=TEXT_MUTED, bg="#070b14", anchor="w"
        )
        self.code_lang_label.pack(anchor="w")
        code_wrap = tk.Frame(right, bg="#070b14")
        code_wrap.pack(fill="both", expand=True, pady=(3, 0))
        code_scroll = tk.Scrollbar(code_wrap, orient="horizontal")
        code_scroll.pack(side="bottom", fill="x")
        self.code_text = tk.Text(
            code_wrap, bg=BI_PLOT_BG, fg="#c8d4e8", height=18, width=52,
            font=("Consolas", 8), relief="flat", bd=0, wrap="none",
            padx=12, pady=10, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=BORDER,
            cursor="arrow", xscrollcommand=code_scroll.set,
        )
        self.code_text.pack(side="top", fill="both", expand=True)
        code_scroll.config(command=self.code_text.xview)
        self.code_text.tag_configure("comment", foreground=TEXT_MUTED)
        self.code_text.tag_configure("kw", foreground=MAGENTA_ACCENT)
        self.code_text.tag_configure("str", foreground=ACCENT)
        self.code_text.tag_configure("num", foreground=ORANGE_ACCENT)
        self.code_text.config(state="disabled")

        # ── Left column: chart stage ──
        left = tk.Frame(body, bg="#070b14")
        left.pack(side="left", fill="both", expand=True)

        title_row = tk.Frame(left, bg="#070b14")
        title_row.pack(fill="x")
        self.chart_title = tk.Label(
            title_row, text="", font=("Segoe UI", 17, "bold"),
            fg=TEXT_PRIMARY, bg="#070b14", anchor="w"
        )
        self.chart_title.pack(side="left")
        self.family_badge = tk.Label(
            title_row, text="", font=("Consolas", 8, "bold"),
            fg=BG_DARK, bg=BLUE_ACCENT, padx=8, pady=2
        )
        self.family_badge.pack(side="left", padx=12, pady=6)

        self.question_label = tk.Label(
            left, text="", font=("Segoe UI", 10, "italic"),
            fg=TEXT_SECONDARY, bg="#070b14", anchor="w"
        )
        self.question_label.pack(fill="x", pady=(0, 6))

        self.canvas = tk.Canvas(
            left, bg=BI_PLOT_BG, highlightthickness=1,
            highlightbackground=BORDER, height=430
        )
        self.canvas.pack(fill="both", expand=True)

        self.pitfall_label = tk.Label(
            left, text="", font=("Segoe UI", 9), fg=ORANGE_ACCENT,
            bg="#0f1524", anchor="w", justify="left", wraplength=700,
            padx=10, pady=7
        )
        self.pitfall_label.pack(fill="x", pady=(8, 0))

        tk.Label(left, text="INSIGHT FEED", font=("Consolas", 8, "bold"),
                 fg=TEXT_MUTED, bg="#070b14").pack(anchor="w", pady=(8, 2))
        self.feed = scrolledtext.ScrolledText(
            left, bg=BI_PLOT_BG, fg=TEXT_SECONDARY, height=7, wrap="word",
            font=("Consolas", 9), relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=BORDER,
        )
        self.feed.pack(fill="x")
        self.feed.tag_configure("takeaway", foreground=ACCENT)
        self.feed.tag_configure("chatter", foreground=TEXT_MUTED)
        self.feed.tag_configure("head", foreground=BLUE_ACCENT)

        # ── Footer: lesson progress + transport controls ──
        self.progress = ttk.Progressbar(
            self.win, mode="determinate", style="BI.Horizontal.TProgressbar"
        )
        self.progress.pack(fill="x", padx=14, pady=(8, 0))

        bar = tk.Frame(self.win, bg="#0c1322", height=44)
        bar.pack(fill="x", pady=(8, 0))
        bar.pack_propagate(False)
        for text, cmd in (("◀  PREV", self._prev), ("NEXT  ▶", self._next)):
            tk.Button(
                bar, text=text, bg="#132038", fg=TEXT_PRIMARY,
                font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                padx=14, pady=4, cursor="hand2", command=cmd,
                activebackground="#1b2c4c", activeforeground=TEXT_PRIMARY
            ).pack(side="left", padx=(16, 6) if "PREV" in text else 6, pady=8)
        self.pause_btn = tk.Button(
            bar, text="| |  PAUSE", bg="#132038", fg=YELLOW_ACCENT,
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
            padx=14, pady=4, cursor="hand2", command=self._toggle_pause,
            activebackground="#1b2c4c", activeforeground=YELLOW_ACCENT
        )
        self.pause_btn.pack(side="left", padx=6, pady=8)
        tk.Label(
            bar, text="← / → change lesson  •  SPACE pauses  •  ESC exits",
            font=("Segoe UI", 8), fg=TEXT_MUTED, bg="#0c1322"
        ).pack(side="left", padx=14)
        tk.Button(
            bar, text="STOP & EXIT", bg="#2a1525", fg=RED_ACCENT,
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
            padx=16, pady=4, cursor="hand2", command=self._exit,
            activebackground="#3a1c30", activeforeground=RED_ACCENT
        ).pack(side="right", padx=16, pady=8)

    # ── Lesson lifecycle ───────────────────────────────────────

    def _load_lesson(self, index):
        """Swap in a lesson: new data, fresh panels, restart the reveal."""
        self.index = index % len(BI_LESSONS)
        self.generation += 1
        self.lesson_t0 = time.time()
        lesson = BI_LESSONS[self.index]
        self.data = self._make_data(lesson["chart"])

        self.chart_title.config(text=lesson["title"])
        self.family_badge.config(text=lesson["family"], bg=self._accent())
        self.question_label.config(text=lesson["question"])
        self.pitfall_label.config(text="⚠  " + lesson["pitfall"])
        self.code_lang_label.config(text="CODE  —  " + lesson["lang"].upper())

        for widget in (self.read_text, self.code_text):
            widget.config(state="normal")
            widget.delete("1.0", "end")
            widget.config(state="disabled")

        self._feed(f"▶ LESSON {self.index + 1}/{len(BI_LESSONS)}  —  "
                   f"{lesson['title']}  ({lesson['family'].lower()})", "head")
        self._reveal_rule(0, self.generation)
        self._type_code(0, self.generation)

    def _accent(self):
        return BI_PALETTE[self.index % len(BI_PALETTE)]

    def _reveal_rule(self, i, gen):
        """Reveal the interpretation rules one at a time, then the pitfall."""
        if not self.running or gen != self.generation:
            return
        lesson = BI_LESSONS[self.index]
        rules = lesson["read"]
        try:
            self.read_text.config(state="normal")
            if i < len(rules):
                self.read_text.insert("end", f"{i + 1}.  ", "bullet")
                self.read_text.insert("end", rules[i] + "\n", "rule")
            else:
                self.read_text.insert("end", "\n⚠  " + lesson["pitfall"] + "\n", "warn")
            self.read_text.see("end")
            self.read_text.config(state="disabled")
        except tk.TclError:
            return
        if i < len(rules):
            self.win.after(self.RULE_MS, lambda: self._reveal_rule(i + 1, gen))

    def _type_code(self, i, gen):
        """Type the lesson's code out line by line, lightly highlighted."""
        if not self.running or gen != self.generation:
            return
        lines = BI_LESSONS[self.index]["code"].split("\n")
        if i >= len(lines):
            return
        try:
            self.code_text.config(state="normal")
            self._insert_code_line(lines[i])
            self.code_text.see("end")
            self.code_text.config(state="disabled")
        except tk.TclError:
            return
        self.win.after(self.CODE_MS, lambda: self._type_code(i + 1, gen))

    CODE_KEYWORDS = {
        "SELECT", "FROM", "WHERE", "GROUP", "ORDER", "BY", "JOIN", "LEFT", "ON",
        "WITH", "AS", "AND", "CASE", "WHEN", "THEN", "ELSE", "END", "HAVING",
        "COUNT", "SUM", "AVG", "MIN", "MAX", "DISTINCT", "INTERVAL", "NULLIF",
        "BETWEEN", "VAR", "RETURN", "CALCULATE", "DIVIDE", "SWITCH", "TRUE",
        "IF", "let", "in", "each", "import", "for", "print", "def", "return",
        "not", "None",
    }

    def _insert_code_line(self, line):
        """Insert one code line, tagging comments, keywords, strings, numbers."""
        stripped = line.lstrip()
        if stripped.startswith("--") or stripped.startswith("#") or stripped.startswith("//"):
            self.code_text.insert("end", line + "\n", "comment")
            return
        pos = 0
        for match in re.finditer(r'"[^"]*"|\'[^\']*\'|\b\w+\b', line):
            if match.start() > pos:
                self.code_text.insert("end", line[pos:match.start()])
            token = match.group(0)
            if token[:1] in ('"', "'"):
                tag = "str"
            elif token in self.CODE_KEYWORDS:
                tag = "kw"
            elif token[:1].isdigit():
                tag = "num"
            else:
                tag = None
            self.code_text.insert("end", token, tag or ())
            pos = match.end()
        self.code_text.insert("end", line[pos:] + "\n")

    def _feed(self, msg, tag="chatter"):
        try:
            stamp = datetime.now().strftime("%H:%M:%S")
            self.feed.insert("end", f"[{stamp}] {msg}\n", tag)
            # Keep the buffer bounded — this runs for hours.
            if int(self.feed.index("end-1c").split(".")[0]) > 400:
                self.feed.delete("1.0", "120.0")
            self.feed.see("end")
        except tk.TclError:
            pass

    def _feed_loop(self):
        """Stream analyst commentary: lesson takeaways mixed with chatter."""
        if not self.running:
            return
        if not self.paused:
            lesson = BI_LESSONS[self.index]
            if random.random() < 0.55:
                self._feed("   " + random.choice(lesson["insights"]), "takeaway")
            else:
                self._feed("   " + random.choice(BI_FEED_CHATTER), "chatter")
        try:
            self.win.after(int(random.uniform(1800, 3400)), self._feed_loop)
        except tk.TclError:
            pass

    def _next(self):
        self._load_lesson(self.index + 1)

    def _prev(self):
        self._load_lesson(self.index - 1)

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_started = time.time()
            self.pause_btn.config(text="▶  RESUME", fg=ACCENT,
                                  activeforeground=ACCENT)
            self._feed("   paused — lesson timer held", "chatter")
        else:
            delta = time.time() - self.pause_started
            self.paused_total += delta
            self.lesson_t0 += delta
            self.pause_btn.config(text="| |  PAUSE", fg=YELLOW_ACCENT,
                                  activeforeground=YELLOW_ACCENT)
            self._feed("   resumed", "chatter")

    # ── Main loop ──────────────────────────────────────────────

    def _tick(self):
        if not self.running or not self.win.winfo_exists():
            return

        now = time.time()
        if self.paused:
            elapsed = self.pause_started - self.start_time - self.paused_total
        else:
            elapsed = now - self.start_time - self.paused_total
        remaining = max(0, self.duration - elapsed)

        if remaining <= 0:
            self._feed("✅ Session complete — deck exhausted, trainer closing.", "takeaway")
            _post(self.win, self._exit, 2500)
            return

        try:
            self.clock_label.config(
                text="remaining  " + str(timedelta(seconds=int(remaining))))
            self.lesson_label.config(
                text=f"LESSON {self.index + 1:02d}/{len(BI_LESSONS):02d}")
            ref = self.pause_started if self.paused else now
            lesson_elapsed = ref - self.lesson_t0
            self.progress.configure(
                value=min(100.0, lesson_elapsed / self.LESSON_SECONDS * 100))
            self._render(min(1.0, lesson_elapsed / self.ENTRANCE_SECONDS))
            if lesson_elapsed >= self.LESSON_SECONDS:
                self._next()
        except tk.TclError:
            return

        self.win.after(self.FRAME_MS, self._tick)

    # ── Data generation ────────────────────────────────────────

    def _make_data(self, chart):
        """Generate plausible-looking data for the current chart type."""
        if chart == "bar":
            labels = ["EMEA", "AMER", "APAC", "LATAM", "MEA", "ANZ"]
            vals = sorted((random.uniform(28, 100) for _ in labels), reverse=True)
            return {"labels": labels, "values": vals}
        if chart == "line":
            base, series = random.uniform(40, 60), []
            for i in range(24):
                base += random.uniform(-3.2, 4.4) + math.sin(i / 3.0) * 1.4
                series.append(max(8, base))
            return {"series": series}
        if chart == "stacked_area":
            names = ["Enterprise", "Mid-Market", "SMB"]
            stacks = []
            level = [random.uniform(20, 30) for _ in names]
            for i in range(16):
                level = [max(4, v + random.uniform(-2.5, 3.0)) for v in level]
                stacks.append(list(level))
            return {"names": names, "stacks": stacks}
        if chart == "donut":
            names = ["Subscriptions", "Services", "Hardware", "Support", "Training"]
            raw = sorted((random.uniform(6, 45) for _ in names), reverse=True)
            total = sum(raw)
            return {"names": names, "pcts": [v / total * 100 for v in raw]}
        if chart == "scatter":
            pts = []
            for _ in range(90):
                x = random.uniform(5, 95)
                y = x * random.uniform(0.7, 0.95) + random.uniform(-18, 18) + 12
                pts.append((x, max(2, y)))
            return {"points": pts, "r": random.uniform(0.62, 0.84)}
        if chart == "histogram":
            bins = []
            for i in range(18):
                centre = math.exp(-((i - 5.5) ** 2) / 13.0)
                bins.append(centre * 100 + random.uniform(0, 7) + max(0, 18 - i) * 0.4)
            return {"bins": bins, "median_bin": 5}
        if chart == "heatmap":
            rows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            cells = []
            for r_i in range(len(rows)):
                weekday = 1.0 if r_i < 5 else 0.14
                cells.append([
                    weekday * (math.exp(-((c - 2.5) ** 2) / 2.6) * 1.0
                               + math.exp(-((c - 8.0) ** 2) / 4.5) * 0.55)
                    + random.uniform(0, 0.07)
                    for c in range(12)
                ])
            return {"rows": rows, "cells": cells, "cols": list(range(8, 20))}
        if chart == "box":
            groups = []
            for name in ["EMEA", "AMER", "APAC", "LATAM"]:
                med = random.uniform(30, 62)
                spread = random.uniform(5, 20)
                groups.append({
                    "name": name,
                    "q1": med - spread, "med": med, "q3": med + spread * 0.9,
                    "lo": med - spread * 2.1, "hi": med + spread * 2.0,
                    "outliers": [med + spread * random.uniform(2.4, 3.2)
                                 for _ in range(random.randint(0, 2))],
                })
            return {"groups": groups}
        if chart == "waterfall":
            start = random.uniform(60, 80)
            steps = [("Volume", random.uniform(8, 20)),
                     ("Price", random.uniform(3, 9)),
                     ("Mix", random.uniform(-7, -2)),
                     ("Churn", random.uniform(-11, -4)),
                     ("FX", random.uniform(-3, 3))]
            return {"start": start, "steps": steps,
                    "end": start + sum(v for _, v in steps)}
        if chart == "funnel":
            names = ["Visited", "Signed up", "Started trial", "Qualified", "Closed won"]
            counts, n = [], random.uniform(48000, 90000)
            for _ in names:
                counts.append(n)
                n *= random.uniform(0.32, 0.66)
            return {"names": names, "counts": counts}
        if chart == "pareto":
            names = ["Latency", "Auth", "Data sync", "Billing", "UI bug",
                     "Timeout", "Import", "Other"]
            vals = sorted((random.uniform(4, 100) for _ in names), reverse=True)
            total = sum(vals)
            cum, acc = [], 0.0
            for v in vals:
                acc += v
                cum.append(acc / total * 100)
            return {"names": names, "values": vals, "cum": cum}
        if chart == "kpi":
            specs = [
                # name, formatter, is-up-good, sample size
                ("Revenue MTD", lambda: f"${random.uniform(1.2, 4.8):.2f}M", True, 4820),
                ("Active users", lambda: f"{random.randint(18000, 64000):,}", True, 41902),
                ("Churn rate", lambda: f"{random.uniform(1.8, 6.4):.1f}%", False, 1180),
                ("Avg handle time", lambda: f"{random.uniform(3.4, 9.2):.1f}m", False, 26),
            ]
            tiles = []
            for name, fmt, good_up, n in specs:
                spark, level = [], random.uniform(40, 70)
                for _ in range(22):
                    level = max(6, level + random.uniform(-5, 5.6))
                    spark.append(level)
                tiles.append({
                    "name": name, "display": fmt(), "good_up": good_up, "n": n,
                    "delta": random.uniform(-14, 18), "spark": spark,
                })
            return {"tiles": tiles}
        return {}

    # ── Rendering ──────────────────────────────────────────────

    def _render(self, anim):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 720
        h = c.winfo_height() or 430
        if w < 60 or h < 60:
            return
        draw = getattr(self, "_draw_" + BI_LESSONS[self.index]["chart"], None)
        if draw is None:
            return
        try:
            draw(c, w, h, max(0.02, anim))
        except Exception:
            # A renderer must never take the trainer down mid-session.
            pass

    def _frame(self, c, w, h, pad=(64, 26, 30, 46), ticks=5, fmt=None):
        """Draw the plot frame + horizontal gridlines. Returns the plot box."""
        x0, y0 = pad[0], pad[1]
        x1, y1 = w - pad[2], h - pad[3]
        for i in range(ticks + 1):
            y = y1 - (y1 - y0) * i / ticks
            c.create_line(x0, y, x1, y, fill=BI_GRID)
            if fmt:
                c.create_text(x0 - 8, y, text=fmt(i / ticks), anchor="e",
                              fill=TEXT_MUTED, font=("Consolas", 8))
        c.create_line(x0, y0, x0, y1, fill=BI_AXIS)
        c.create_line(x0, y1, x1, y1, fill=BI_AXIS)
        return x0, y0, x1, y1

    def _callout(self, c, x, y, text, color, anchor="w"):
        """Pulsing annotation marker — the 'the analyst points here' bit."""
        pulse = 3.5 + math.sin(time.time() * 3.2) * 1.8
        c.create_oval(x - pulse, y - pulse, x + pulse, y + pulse,
                      outline=color, width=1)
        c.create_text(x + (12 if anchor == "w" else -12), y, text=text,
                      anchor=anchor, fill=color, font=("Consolas", 8, "bold"))

    def _draw_bar(self, c, w, h, anim):
        d = self.data
        vals, labels = d["values"], d["labels"]
        top = max(vals) * 1.15
        x0, y0, x1, y1 = self._frame(c, w, h, fmt=lambda t: f"{top * t:,.0f}k")
        n = len(vals)
        slot = (x1 - x0) / n
        for i, v in enumerate(vals):
            bh = (v / top) * (y1 - y0) * anim
            bx = x0 + slot * i + slot * 0.18
            bw = slot * 0.64
            color = self._accent() if i == 0 else _bi_mix(self._accent(), BI_PLOT_BG, 0.45)
            c.create_rectangle(bx, y1 - bh, bx + bw, y1, fill=color, outline="")
            c.create_text(bx + bw / 2, y1 + 14, text=labels[i], anchor="n",
                          fill=TEXT_SECONDARY, font=("Consolas", 8))
            if anim > 0.85:
                c.create_text(bx + bw / 2, y1 - bh - 9, text=f"{v:,.0f}k",
                              fill=TEXT_PRIMARY, font=("Consolas", 8))
        if anim > 0.9:
            median = sorted(vals)[n // 2]
            my = y1 - (median / top) * (y1 - y0)
            c.create_line(x0, my, x1, my, fill=YELLOW_ACCENT, dash=(4, 3))
            c.create_text(x1 - 4, my - 9, text=f"median {median:,.0f}k", anchor="e",
                          fill=YELLOW_ACCENT, font=("Consolas", 8))
            self._callout(c, x0 + slot * 0.82,
                          y1 - (vals[0] / top) * (y1 - y0) - 24,
                          "top performer", self._accent())

    def _draw_line(self, c, w, h, anim):
        s = self.data["series"]
        top, low = max(s) * 1.12, min(s) * 0.85
        rng = top - low or 1
        x0, y0, x1, y1 = self._frame(c, w, h, fmt=lambda t: f"{low + rng * t:,.0f}")
        shown = max(2, int(len(s) * anim))
        pts = []
        for i in range(shown):
            x = x0 + (x1 - x0) * i / (len(s) - 1)
            y = y1 - ((s[i] - low) / rng) * (y1 - y0)
            pts.extend([x, y])
        if len(pts) >= 4:
            c.create_line(*pts, fill=self._accent(), width=2, smooth=True)
        # 7-point moving average — the "what is the actual direction" line
        ma = []
        for i in range(shown):
            window = s[max(0, i - 6):i + 1]
            avg = sum(window) / len(window)
            ma.extend([x0 + (x1 - x0) * i / (len(s) - 1),
                       y1 - ((avg - low) / rng) * (y1 - y0)])
        if len(ma) >= 4:
            c.create_line(*ma, fill=CYAN_ACCENT, width=2, dash=(5, 3), smooth=True)
        c.create_text(x0 + 8, y0 + 10, text="— actual    - - 7-pt moving average",
                      anchor="w", fill=TEXT_MUTED, font=("Consolas", 8))
        for lbl, frac in (("Q1", 0.0), ("Q2", 0.25), ("Q3", 0.5), ("Q4", 0.75)):
            c.create_text(x0 + (x1 - x0) * frac + 6, y1 + 12, text=lbl, anchor="w",
                          fill=TEXT_MUTED, font=("Consolas", 8))
        if anim >= 1.0 and len(pts) >= 4:
            self._callout(c, pts[-2], pts[-1], "read the slope, not the last dot",
                          self._accent(), anchor="e")

    def _draw_stacked_area(self, c, w, h, anim):
        d = self.data
        stacks, names = d["stacks"], d["names"]
        totals = [sum(row) for row in stacks]
        top = max(totals) * 1.12
        x0, y0, x1, y1 = self._frame(c, w, h, fmt=lambda t: f"{top * t:,.0f}k")
        n = len(stacks)
        shown = max(2, int(n * anim))
        bases = [0.0] * shown
        for si in range(len(names)):
            poly, back = [], []
            for i in range(shown):
                x = x0 + (x1 - x0) * i / (n - 1)
                lo = bases[i]
                hi = lo + stacks[i][si]
                poly.extend([x, y1 - (hi / top) * (y1 - y0)])
                back.append((x, y1 - (lo / top) * (y1 - y0)))
                bases[i] = hi
            for x, y in reversed(back):
                poly.extend([x, y])
            if len(poly) >= 6:
                c.create_polygon(*poly, fill=_bi_mix(BI_PALETTE[si], BI_PLOT_BG, 0.35),
                                 outline=BI_PALETTE[si], width=1)
        for si, name in enumerate(names):
            c.create_rectangle(x0 + 10 + si * 118, y0 + 6, x0 + 20 + si * 118, y0 + 16,
                               fill=BI_PALETTE[si], outline="")
            c.create_text(x0 + 25 + si * 118, y0 + 11, text=name, anchor="w",
                          fill=TEXT_SECONDARY, font=("Consolas", 8))
        c.create_text(x1 - 6, y1 + 14, text="top edge = total  •  only the bottom band has a flat baseline",
                      anchor="e", fill=TEXT_MUTED, font=("Consolas", 8))

    def _draw_donut(self, c, w, h, anim):
        d = self.data
        cx, cy = w * 0.36, h * 0.52
        rad = min(w * 0.24, h * 0.36)
        inner = rad * 0.56
        start = 90.0
        for i, (name, pct) in enumerate(zip(d["names"], d["pcts"])):
            extent = -pct * 3.6 * anim
            color = BI_PALETTE[i % len(BI_PALETTE)]
            c.create_arc(cx - rad, cy - rad, cx + rad, cy + rad,
                         start=start, extent=extent, style="pieslice",
                         fill=color, outline=BI_PLOT_BG, width=2)
            mid = math.radians(start + extent / 2)
            lx = cx + math.cos(mid) * (rad * 0.78)
            ly = cy - math.sin(mid) * (rad * 0.78)
            if anim > 0.8 and pct > 4:
                c.create_text(lx, ly, text=f"{pct:.0f}%", fill="#06101c",
                              font=("Consolas", 9, "bold"))
            start += extent
        c.create_oval(cx - inner, cy - inner, cx + inner, cy + inner,
                      fill=BI_PLOT_BG, outline="")
        c.create_text(cx, cy - 10, text="TOTAL", fill=TEXT_MUTED, font=("Consolas", 8))
        c.create_text(cx, cy + 10, text="$4.82M", fill=TEXT_PRIMARY,
                      font=("Consolas", 15, "bold"))
        lx = w * 0.68
        c.create_text(lx, h * 0.22, text="ONE total  •  ONE moment",
                      anchor="w", fill=TEXT_MUTED, font=("Consolas", 8))
        for i, (name, pct) in enumerate(zip(d["names"], d["pcts"])):
            y = h * 0.30 + i * 26
            c.create_rectangle(lx, y, lx + 12, y + 12,
                               fill=BI_PALETTE[i % len(BI_PALETTE)], outline="")
            c.create_text(lx + 20, y + 6, text=f"{name}", anchor="w",
                          fill=TEXT_SECONDARY, font=("Consolas", 9))
            c.create_text(lx + 200, y + 6, text=f"{pct:5.1f}%", anchor="e",
                          fill=TEXT_PRIMARY, font=("Consolas", 9, "bold"))

    def _draw_scatter(self, c, w, h, anim):
        d = self.data
        pts = d["points"]
        x0, y0, x1, y1 = self._frame(c, w, h, fmt=lambda t: f"{t * 120:,.0f}k")
        shown = int(len(pts) * anim)
        for px, py in pts[:shown]:
            x = x0 + (x1 - x0) * px / 100.0
            y = y1 - (y1 - y0) * py / 120.0
            c.create_oval(x - 3, y - 3, x + 3, y + 3,
                          fill=_bi_mix(self._accent(), BI_PLOT_BG, 0.25),
                          outline=self._accent())
        if anim > 0.6:
            # Least-squares fit over what is on screen
            xs = [p[0] for p in pts[:shown]]
            ys = [p[1] for p in pts[:shown]]
            n = len(xs) or 1
            mx, my = sum(xs) / n, sum(ys) / n
            denom = sum((x - mx) ** 2 for x in xs) or 1
            slope = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / denom
            fy = lambda vx: my + slope * (vx - mx)
            c.create_line(x0 + (x1 - x0) * 0.02, y1 - (y1 - y0) * fy(2) / 120.0,
                          x0 + (x1 - x0) * 0.98, y1 - (y1 - y0) * fy(98) / 120.0,
                          fill=YELLOW_ACCENT, width=2, dash=(6, 4))
            c.create_text(x1 - 8, y0 + 12,
                          text=f"r = +{d['r']:.2f}   n = {len(pts)}   p < 0.001",
                          anchor="e", fill=YELLOW_ACCENT, font=("Consolas", 9, "bold"))
            c.create_text(x1 - 8, y0 + 28, text="correlation ≠ causation",
                          anchor="e", fill=TEXT_MUTED, font=("Consolas", 8))
        c.create_text((x0 + x1) / 2, y1 + 26, text="ad spend  →",
                      fill=TEXT_MUTED, font=("Consolas", 8))

    def _draw_histogram(self, c, w, h, anim):
        bins = self.data["bins"]
        top = max(bins) * 1.15
        x0, y0, x1, y1 = self._frame(c, w, h, fmt=lambda t: f"{top * t:,.0f}")
        slot = (x1 - x0) / len(bins)
        for i, v in enumerate(bins):
            bh = (v / top) * (y1 - y0) * anim
            bx = x0 + slot * i
            c.create_rectangle(bx, y1 - bh, bx + slot - 1, y1,
                               fill=_bi_mix(self._accent(), BI_PLOT_BG, 0.3),
                               outline=self._accent())
        if anim > 0.85:
            med_x = x0 + slot * (self.data["median_bin"] + 0.5)
            mean_x = med_x + slot * 2.4
            for x, label, color in ((med_x, "median", ACCENT),
                                    (mean_x, "mean", ORANGE_ACCENT)):
                c.create_line(x, y0, x, y1, fill=color, dash=(4, 3))
                c.create_text(x + 4, y0 + 10, text=label, anchor="w", fill=color,
                              font=("Consolas", 8, "bold"))
            c.create_text(x1 - 8, y0 + 12,
                          text="right-skewed → mean pulled above median",
                          anchor="e", fill=TEXT_MUTED, font=("Consolas", 8))
        c.create_text((x0 + x1) / 2, y1 + 26, text="order value (bins of $25)  →",
                      fill=TEXT_MUTED, font=("Consolas", 8))

    def _draw_heatmap(self, c, w, h, anim):
        d = self.data
        rows, cells, cols = d["rows"], d["cells"], d["cols"]
        x0, y0 = 62, 34
        x1, y1 = w - 150, h - 46
        cw = (x1 - x0) / len(cols)
        ch = (y1 - y0) / len(rows)
        peak = max(max(r) for r in cells) or 1
        for ri, row in enumerate(cells):
            for ci, v in enumerate(row):
                if (ri * len(cols) + ci) > len(cols) * len(rows) * anim:
                    continue
                t = (v / peak) ** 0.9           # near-linear: quiet stays dark
                color = _bi_mix("#07101f", self._accent(), t)
                c.create_rectangle(x0 + ci * cw, y0 + ri * ch,
                                   x0 + (ci + 1) * cw - 1, y0 + (ri + 1) * ch - 1,
                                   fill=color, outline="")
            c.create_text(x0 - 8, y0 + ri * ch + ch / 2, text=rows[ri], anchor="e",
                          fill=TEXT_SECONDARY, font=("Consolas", 8))
        for ci, hour in enumerate(cols):
            c.create_text(x0 + ci * cw + cw / 2, y1 + 12, text=f"{hour:02d}",
                          fill=TEXT_MUTED, font=("Consolas", 8))
        # Legend: one hue, varying lightness — never a rainbow
        lx = w - 128
        for i in range(60):
            t = i / 59.0
            c.create_rectangle(lx, y1 - t * (y1 - y0), lx + 16,
                               y1 - (t + 0.02) * (y1 - y0),
                               fill=_bi_mix("#07101f", self._accent(), t ** 0.9),
                               outline="")
        c.create_text(lx + 22, y0, text=f"{peak * 1000:,.0f}", anchor="w",
                      fill=TEXT_MUTED, font=("Consolas", 8))
        c.create_text(lx + 22, y1, text="0", anchor="w",
                      fill=TEXT_MUTED, font=("Consolas", 8))
        c.create_text(lx, y0 - 18, text="unique sessions", anchor="w",
                      fill=TEXT_MUTED, font=("Consolas", 8))
        c.create_text(x0, y0 - 18, text="scan for blocks and stripes, not single cells",
                      anchor="w", fill=TEXT_MUTED, font=("Consolas", 8))

    def _draw_box(self, c, w, h, anim):
        groups = self.data["groups"]
        top = max(g["hi"] + 12 for g in groups)
        x0, y0, x1, y1 = self._frame(c, w, h, fmt=lambda t: f"{top * t:,.0f}d")
        slot = (x1 - x0) / len(groups)
        yof = lambda v: y1 - (v / top) * (y1 - y0) * anim
        for i, g in enumerate(groups):
            cx = x0 + slot * (i + 0.5)
            half = slot * 0.22
            color = BI_PALETTE[i % len(BI_PALETTE)]
            c.create_line(cx, yof(g["lo"]), cx, yof(g["hi"]), fill=color)
            for v in (g["lo"], g["hi"]):
                c.create_line(cx - half * 0.5, yof(v), cx + half * 0.5, yof(v), fill=color)
            c.create_rectangle(cx - half, yof(g["q3"]), cx + half, yof(g["q1"]),
                               fill=_bi_mix(color, BI_PLOT_BG, 0.65), outline=color)
            c.create_line(cx - half, yof(g["med"]), cx + half, yof(g["med"]),
                          fill=color, width=3)
            for o in g["outliers"]:
                oy = yof(o)
                c.create_oval(cx - 3, oy - 3, cx + 3, oy + 3, outline=RED_ACCENT)
            c.create_text(cx, y1 + 14, text=g["name"], anchor="n",
                          fill=TEXT_SECONDARY, font=("Consolas", 8))
            if anim > 0.9:
                c.create_text(cx + half + 6, yof(g["med"]), text=f"{g['med']:.0f}",
                              anchor="w", fill=TEXT_PRIMARY, font=("Consolas", 8))
        c.create_text(x0 + 8, y0 + 10,
                      text="box = middle 50% (Q1→Q3)  •  line = median  •  dots = outliers",
                      anchor="w", fill=TEXT_MUTED, font=("Consolas", 8))

    def _draw_waterfall(self, c, w, h, anim):
        d = self.data
        bars = [("Start", d["start"], "total")]
        for name, delta in d["steps"]:
            bars.append((name, delta, "delta"))
        bars.append(("End", d["end"], "total"))
        top = max(d["start"], d["end"]) * 1.35
        x0, y0, x1, y1 = self._frame(c, w, h, fmt=lambda t: f"{top * t:,.0f}k")
        slot = (x1 - x0) / len(bars)
        yof = lambda v: y1 - (v / top) * (y1 - y0)
        running = 0.0
        prev_x = prev_y = None
        for i, (name, val, kind) in enumerate(bars):
            if i > len(bars) * anim:
                break
            bx = x0 + slot * i + slot * 0.2
            bw = slot * 0.6
            if kind == "total":
                lo, hi = 0.0, val
                color = BLUE_ACCENT
                running = val
            else:
                lo, hi = running, running + val
                color = ACCENT if val >= 0 else RED_ACCENT
                running = hi
            c.create_rectangle(bx, yof(max(lo, hi)), bx + bw, yof(min(lo, hi)),
                               fill=_bi_mix(color, BI_PLOT_BG, 0.35), outline=color)
            label = f"{val:+,.1f}k" if kind == "delta" else f"{val:,.1f}k"
            c.create_text(bx + bw / 2, yof(max(lo, hi)) - 9, text=label,
                          fill=color, font=("Consolas", 8, "bold"))
            c.create_text(bx + bw / 2, y1 + 14, text=name, anchor="n",
                          fill=TEXT_SECONDARY, font=("Consolas", 8))
            if prev_x is not None:
                c.create_line(prev_x, prev_y, bx, prev_y, fill=BI_AXIS, dash=(2, 2))
            prev_x, prev_y = bx + bw, yof(running)
        if anim > 0.95:
            c.create_text(x1 - 6, y0 + 12,
                          text="bridge check = 0.00  •  bars reconcile to the end total",
                          anchor="e", fill=ACCENT, font=("Consolas", 8, "bold"))

    def _draw_funnel(self, c, w, h, anim):
        d = self.data
        names, counts = d["names"], d["counts"]
        x0, y0 = 128, 44
        x1, y1 = w - 210, h - 40
        top = counts[0]
        rowh = (y1 - y0) / len(names)
        cx = (x0 + x1) / 2
        worst = 0
        for i in range(1, len(counts)):
            if counts[i] / counts[i - 1] < counts[worst + 1] / counts[worst]:
                worst = i - 1
        for i, (name, cnt) in enumerate(zip(names, counts)):
            if i > len(names) * anim:
                break
            half = (x1 - x0) / 2 * (cnt / top)
            ty = y0 + rowh * i
            by = ty + rowh * 0.72
            color = BI_PALETTE[i % len(BI_PALETTE)]
            c.create_rectangle(cx - half, ty, cx + half, by,
                               fill=_bi_mix(color, BI_PLOT_BG, 0.4), outline=color)
            mid = (ty + by) / 2
            c.create_text(x0 - 14, mid, text=name, anchor="e",
                          fill=TEXT_PRIMARY, font=("Consolas", 9, "bold"))
            c.create_text(x1 + 16, mid, text=f"{cnt:>9,.0f}", anchor="w",
                          fill=TEXT_SECONDARY, font=("Consolas", 9))
            c.create_text(x1 + 16, mid + 14, text=f"{cnt / top * 100:.1f}% of top",
                          anchor="w", fill=TEXT_MUTED, font=("Consolas", 8))
            if i:
                step = cnt / counts[i - 1] * 100
                worst_gap = (i - 1 == worst)
                gap_color = RED_ACCENT if worst_gap else TEXT_SECONDARY
                c.create_text(cx, ty - rowh * 0.14,
                              text=f"▼ {100 - step:.0f}% lost"
                                   + ("   ← biggest drop" if worst_gap else ""),
                              fill=gap_color, font=("Consolas", 8, "bold"))
        c.create_text(x0 - 14, y0 - 22, text="read the GAPS, not the widths",
                      anchor="w", fill=TEXT_MUTED, font=("Consolas", 8))

    def _draw_pareto(self, c, w, h, anim):
        d = self.data
        vals, names, cum = d["values"], d["names"], d["cum"]
        top = max(vals) * 1.2
        x0, y0, x1, y1 = self._frame(c, w, h, pad=(64, 26, 58, 46),
                                     fmt=lambda t: f"{top * t:,.0f}k")
        slot = (x1 - x0) / len(vals)
        for i, v in enumerate(vals):
            bh = (v / top) * (y1 - y0) * anim
            bx = x0 + slot * i + slot * 0.15
            bw = slot * 0.7
            vital = cum[i] <= 80
            color = self._accent() if vital else _bi_mix(self._accent(), BI_PLOT_BG, 0.6)
            c.create_rectangle(bx, y1 - bh, bx + bw, y1, fill=color, outline="")
            c.create_text(bx + bw / 2, y1 + 14, text=names[i], anchor="n",
                          fill=TEXT_SECONDARY, font=("Consolas", 7))
        pts = []
        for i, cv in enumerate(cum):
            if i > len(cum) * anim:
                break
            pts.extend([x0 + slot * (i + 0.5), y1 - (cv / 100.0) * (y1 - y0)])
        line_color = CYAN_ACCENT if self._accent() == YELLOW_ACCENT else YELLOW_ACCENT
        if len(pts) >= 4:
            c.create_line(*pts, fill=line_color, width=2)
            for i in range(0, len(pts), 2):
                c.create_oval(pts[i] - 3, pts[i + 1] - 3, pts[i] + 3, pts[i + 1] + 3,
                              fill=line_color, outline="")
            c.create_text(x0 + 10, y0 + 26, text="— cumulative % of cost (right axis)",
                          anchor="w", fill=line_color, font=("Consolas", 8))
        y80 = y1 - 0.8 * (y1 - y0)
        c.create_line(x0, y80, x1, y80, fill=RED_ACCENT, dash=(5, 3))
        c.create_text(x1 + 6, y80, text="80%", anchor="w", fill=RED_ACCENT,
                      font=("Consolas", 8, "bold"))
        for i in range(6):
            yy = y1 - (y1 - y0) * i / 5
            c.create_text(x1 + 6, yy, text=f"{i * 20}%", anchor="w",
                          fill=TEXT_MUTED, font=("Consolas", 7))
        vital_n = sum(1 for cv in cum if cv <= 80)
        if anim > 0.9:
            c.create_text(x0 + 10, y0 + 10,
                          text=f"{vital_n} of {len(vals)} causes carry ~80% of the cost",
                          anchor="w", fill=ACCENT, font=("Consolas", 9, "bold"))

    def _draw_kpi(self, c, w, h, anim):
        tiles = self.data["tiles"]
        pad = 16
        tw = (w - pad * (len(tiles) + 1)) / len(tiles)
        th = h * 0.54
        ty = h * 0.10
        for i, t in enumerate(tiles):
            if i > len(tiles) * anim * 1.2:
                break
            tx = pad + i * (tw + pad)
            good = (t["delta"] >= 0) == t["good_up"]
            color = ACCENT if good else RED_ACCENT
            c.create_rectangle(tx, ty, tx + tw, ty + th, fill=BI_PANEL_BG,
                               outline=BORDER)
            c.create_text(tx + 14, ty + 16, text=t["name"].upper(), anchor="w",
                          fill=TEXT_MUTED, font=("Consolas", 8))
            c.create_text(tx + 14, ty + 46, text=t["display"], anchor="w",
                          fill=TEXT_PRIMARY, font=("Consolas", 19, "bold"))
            arrow = "▲" if t["delta"] >= 0 else "▼"
            c.create_text(tx + 14, ty + 72,
                          text=f"{arrow} {abs(t['delta']):.1f}%  vs LY",
                          anchor="w", fill=color, font=("Consolas", 9, "bold"))
            # n on the tile: a delta with no sample size is not evidence.
            n_color = TEXT_MUTED if t["n"] >= 30 else ORANGE_ACCENT
            c.create_text(tx + 14, ty + 90,
                          text=f"n = {t['n']:,}" + ("" if t["n"] >= 30 else "  (n too low)"),
                          anchor="w", fill=n_color, font=("Consolas", 8))
            c.create_text(tx + 14, ty + 108, text="target  ≥ +5.0% YoY", anchor="w",
                          fill=TEXT_MUTED, font=("Consolas", 8))
            # Sparkline: the context the big number destroys
            sx0, sy0 = tx + 14, ty + th - 52
            sx1, sy1 = tx + tw - 14, ty + th - 12
            spark = t["spark"]
            hi, lo = max(spark), min(spark)
            rng = (hi - lo) or 1
            pts = []
            for j, v in enumerate(spark):
                pts.extend([sx0 + (sx1 - sx0) * j / (len(spark) - 1),
                            sy1 - ((v - lo) / rng) * (sy1 - sy0)])
            if len(pts) >= 4:
                c.create_line(*pts, fill=color, width=1, smooth=True)
                c.create_oval(pts[-2] - 3, pts[-1] - 3, pts[-2] + 3, pts[-1] + 3,
                              fill=color, outline="")
            c.create_text(sx0, ty + th - 62, text="trailing 22 periods", anchor="w",
                          fill=TEXT_MUTED, font=("Consolas", 7))
        c.create_text(w / 2, ty + th + 34,
                      text="a number with no comparison is not a KPI — it is trivia",
                      fill=TEXT_SECONDARY, font=("Segoe UI", 10, "italic"))
        c.create_text(w / 2, ty + th + 58,
                      text="colour follows DIRECTION OF GOODNESS: falling churn is green",
                      fill=TEXT_MUTED, font=("Consolas", 8))

    # ── Teardown ───────────────────────────────────────────────

    def _exit(self):
        if not self.running:
            return
        self.running = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# DOCUMENTATION VIEWER
# ═══════════════════════════════════════════════════════════════

DOCS_TEXT = """
\u2550\u2550\u2550  WorkFacade \u2014 Documentation  \u2550\u2550\u2550

\u2501\u2501\u2501  WHAT IS THIS?  \u2501\u2501\u2501

WorkFacade is an educational demonstration project that shows how
desktop activity simulation works across platforms (Windows, macOS,
Linux). It combines multiple "excuse screens" into a single launcher
with a clean glassmorphic UI.

Every mode has two jobs:
  1. Display a convincing fullscreen simulation
  2. Keep your PC marked as "Active" on all platforms

All timed modes auto-exit when the configured duration expires and
return you to the launcher automatically.


\u2501\u2501\u2501  HOW DOES KEEP-ALIVE WORK?  \u2501\u2501\u2501

Operating systems (and apps like Teams, Slack, etc.) detect idle
status by monitoring input events. If no mouse movement or keystrokes
happen for a threshold period (usually 3-5 minutes), you go "Away".

WorkFacade prevents this with a background KeepAliveEngine that:
  \u2022 Moves the mouse by 1 pixel and back (and the occasional 1-notch scroll)
  \u2022 Sends a harmless key press (Shift / Ctrl / F13-F15, rotated)
  \u2022 Adds \u00b125% random jitter to every interval so it never looks robotic
  \u2022 Runs on a daemon thread so it doesn't block the UI
  \u2022 Uses thread-safe signaling (threading.Event) for start/stop
  \u2022 Uses pyautogui for cross-application input injection
  \u2022 Tracks live activity stats (mouse moves / key presses)
  \u2022 Gracefully degrades if pyautogui is not installed

The movements are invisible (1px) and the chosen keys have no effect
in any application, so nothing gets disrupted.

KEEP-ALIVE INTENSITY PROFILES (selectable from the launcher):
  \u2022 Stealth     \u2014 mouse ~110s / key ~150s   (minimal footprint)
  \u2022 Normal      \u2014 mouse ~55s  / key ~80s     (balanced default)
  \u2022 Aggressive  \u2014 mouse ~25s  / key ~35s     (never lets idle near)


\u2501\u2501\u2501  SIMULATION MODES  \u2501\u2501\u2501

\u2590 BLUE SCREEN OF DEATH (BSOD)
  Renders a pixel-perfect Windows 11 blue screen with:
  \u2022 The iconic ":(" sad face
  \u2022 Slowly creeping percentage counter (0-100%, then loops)
  \u2022 Random real Windows stop codes (8 variants)
  \u2022 QR code placeholder and support URL
  \u2022 Hidden cursor, fullscreen, always-on-top
  \u2022 Configurable duration (hours or minutes, auto-exits when done)
  \u2022 Press ESC to exit early

  Why it works: Nobody approaches someone whose PC is BSOD'd. You
  get left completely alone. The keep-alive runs underneath so your
  status stays green on all platforms.


\u2590 CYBER THREAT SCANNER
  A full enterprise-grade security dashboard simulation with:
  \u2022 Real-time console output with timestamped log entries
  \u2022 18 different scan items with weighted status flags
  \u2022 10 scan phases that cycle randomly
  \u2022 Dual progress bars (overall + current module)
  \u2022 AI threat scoring messages
  \u2022 Anomaly and latency spike events
  \u2022 Pause/Resume with accurate elapsed-time tracking
  \u2022 Configurable duration (hours or minutes)
  \u2022 Double-exit protection prevents crashes

  Why it works: If anyone glances at your screen, they see a serious
  corporate security tool running. The scrolling green text and
  "CRITICAL" flags make it look important and untouchable.


\u2590 WINDOWS UPDATE
  The universally-accepted excuse screen:
  \u2022 Fullscreen black background
  \u2022 Animated spinning dots (Windows 10/11 style)
  \u2022 Slow, realistic progress percentage
  \u2022 "Don't turn off your computer" message
  \u2022 Hidden cursor, always-on-top
  \u2022 Configurable duration (hours or minutes, auto-exits when done)
  \u2022 Press ESC to exit early

  Why it works: Everyone has been trapped by a Windows Update.
  Nobody questions it. Nobody tries to use your machine. The
  progress is intentionally slow and erratic (just like real
  Windows Updates).


\u2590 DISK OPTIMIZATION
  A Windows-style drive defragmentation tool:
  \u2022 Drive list with SSD/HDD types and per-drive status
  \u2022 Colorful block map visualization that updates live
  \u2022 Rotating action descriptions (8 action types)
  \u2022 Per-drive status progression (Queued \u2192 Optimizing \u2192 OK)
  \u2022 Completion state finalization when all drives are done
  \u2022 Realistic progress bar

  Why it works: Disk optimization is a known "IT maintenance" task.
  It looks technical, has visual elements that suggest real work,
  and nobody wants to interrupt a defrag.


\u2590 STAY ACTIVE (Invisible Mode)
  No flashy screen \u2014 pure stealth:
  \u2022 Tiny control window with countdown timer
  \u2022 Micro mouse movements (1px, invisible) + occasional scroll
  \u2022 Periodic harmless key presses (Shift/Ctrl/F13-F15, rotated)
  \u2022 Set duration in hours or minutes (validated input)
  \u2022 Live keep-alive readout: profile, mouse/key counts, last action
  \u2022 Minimize button to hide the control window
  \u2022 Progress bar showing elapsed time

  Why it works: If you just need to step away without any cover
  story, this keeps every platform showing you as "Active" with
  zero visual footprint. Hit Minimize and walk away.


\u2590 CODE COMPILER (Build & Test Pipeline)
  A developer build console that loops convincingly through:
  \u2022 Dependency resolution (real-looking package@version lines)
  \u2022 TypeScript compilation of source modules
  \u2022 Vite/Rollup-style asset bundling with chunk sizes
  \u2022 A green, all-passing Jest test suite + coverage report
  \u2022 "watching for changes" idle state between cycles
  \u2022 Live progress bar tied to elapsed runtime
  \u2022 ESC or Stop & Exit to leave

  Why it works: A scrolling build log screams "deep in dev work."
  No one interrupts a developer mid-compile.


\u2590 AI MODEL TRAINING (Neural Net Trainer)
  A deep-learning training dashboard featuring:
  \u2022 Live metric cards: epoch, loss, accuracy, learn rate, GPU util
  \u2022 A real-time training-loss curve drawn on a canvas
  \u2022 Animated layer-activation bar chart
  \u2022 Decaying loss / climbing accuracy that track the duration
  \u2022 Checkpoint-save log events
  \u2022 ESC or Stop & Exit to leave

  Why it works: Training runs take hours and must not be disturbed.
  It's the most untouchable "I'm busy" screen of all.


\u2590 MATRIX RAIN (Digital Rain Screensaver)
  Pure aesthetic cover \u2014 fullscreen cascading green code:
  \u2022 Columns of falling glyphs with bright leading characters
  \u2022 Fading green trails over a black background
  \u2022 Latin, digit, and katakana glyph set
  \u2022 Hidden cursor, fullscreen, always-on-top
  \u2022 Auto-exits when duration expires; ESC to exit early

  Why it works: It looks like a screensaver or "something technical
  running." Eye-catching enough that people leave it (and you) alone.


\u2590 THE BI TRAINER (BI Chart & Insight Clinic)
  A scrolling business-intelligence masterclass. Cycles through 12
  chart types, drawing a live example of each:
  \u2022 Column, line, stacked area, donut, scatter, histogram, heatmap,
    box & whisker, waterfall, funnel, Pareto, and KPI tiles
  \u2022 A "how to read it" panel that reveals the interpretation rules
    one at a time, ending on the classic misreading to avoid
  \u2022 The SQL / DAX / pandas / Power Query code behind each chart,
    typed out line by line with syntax highlighting
  \u2022 A scrolling insight feed of analyst commentary
  \u2022 Auto-advances every 18 seconds; \u2190 / \u2192 change lesson,
    SPACE pauses, ESC or Stop & Exit leaves

  Why it works: It reads as focused analysis work \u2014 and unlike the
  other modes, the content on screen is genuinely worth reading.


\u2501\u2501\u2501  LAUNCHER FEATURES  \u2501\u2501\u2501

  \u2022 Glassmorphic card-based UI with dark theme
  \u2022 Flicker-free hover effects on simulation cards
  \u2022 Duration input in HOURS or MINUTES (validated)
  \u2022 Keep-alive intensity selector (Stealth / Normal / Aggressive)
  \u2022 "\ud83c\udfb2 Surprise Me" button launches a random simulation
  \u2022 Universal ESC panic-exit on every simulation window
  \u2022 Simulation registry pattern for clean extensibility
  \u2022 Auto-center on screen, non-resizable


\u2501\u2501\u2501  TECHNICAL DETAILS  \u2501\u2501\u2501

  Framework:        Python + Tkinter (built-in, no web server)
  Input Injection:  pyautogui (cross-platform mouse/keyboard)
  Intensity:        Stealth / Normal / Aggressive timing profiles
  Jitter:           +/-25% randomization on every interval
  Thread Safety:    threading.Event for KeepAliveEngine signaling
  Threading:        daemon threads for background activity
  UI Updates:       root.after() for thread-safe GUI updates
  Fullscreen:       tk attributes -fullscreen + -topmost
  Cursor Hide:      config(cursor="none") on fullscreen windows
  Dispatch:         Registry dict for simulation class lookup

  pyautogui.FAILSAFE is ON \u2014 move mouse to top-left corner
  to force-quit if anything goes wrong.


\u2501\u2501\u2501  USAGE NOTES  \u2501\u2501\u2501

  \u2022 Install dependency:  pip install pyautogui
  \u2022 Run:                 python WorkFacade.py
  \u2022 ESC exits ANY simulation (fullscreen or windowed)
  \u2022 Close window / Stop button also exits windowed modes
  \u2022 All timed modes auto-exit when duration expires
  \u2022 pyautogui failsafe: move mouse to (0,0) corner to abort
  \u2022 Duration: 1-8 hours OR 1-480 minutes (validated)
  \u2022 Keep-alive intensity + "Surprise Me" live on the launcher


\u2501\u2501\u2501  DISCLAIMER  \u2501\u2501\u2501

  This is an EDUCATIONAL project demonstrating UI simulation,
  input injection, and idle-prevention techniques. It is provided
  for learning purposes and should be used responsibly.
  See DISCLAIMER.md for full liability waiver.
"""


class DocumentationViewer:
    """In-app documentation viewer."""

    def __init__(self, parent_root, on_exit):
        self.on_exit = on_exit

        self.win = tk.Toplevel(parent_root)
        self.win.title("WorkFacade \u2014 Documentation")
        self.win.geometry("800x650")
        self.win.configure(bg=BG_DARK)
        self.win.protocol("WM_DELETE_WINDOW", self._exit)
        self.win.bind("<Escape>", lambda e: self._exit())

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.win, bg="#0d1220", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="\u2139  Documentation",
            font=("Segoe UI", 14, "bold"), fg=TEXT_PRIMARY, bg="#0d1220"
        ).pack(side="left", padx=15, pady=10)

        tk.Button(
            header, text="Close", font=("Segoe UI", 9),
            bg="#2a1525", fg=RED_ACCENT, relief="flat", padx=12,
            command=self._exit, cursor="hand2"
        ).pack(side="right", padx=15, pady=10)

        # Text area
        self.text = scrolledtext.ScrolledText(
            self.win, bg="#060a12", fg=TEXT_PRIMARY,
            font=("Consolas", 10), relief="flat", bd=0,
            insertbackground=ACCENT, wrap="word",
            highlightthickness=1, highlightcolor=BORDER,
            highlightbackground=BORDER, padx=15, pady=15
        )
        self.text.pack(fill="both", expand=True, padx=15, pady=15)
        self.text.insert("1.0", DOCS_TEXT)
        self.text.config(state="disabled")

    def _exit(self):
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# MAIN LAUNCHER (Glassmorphic Menu)
# ═══════════════════════════════════════════════════════════════

class Launcher:
    """Main menu with glassmorphic card-based UI."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.W, self.H = 960, 880
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.active_sim = None
        self.duration_var = tk.IntVar(value=2)
        self.unit_var = tk.StringVar(value="hours")
        self.intensity_var = tk.StringVar(value=DEFAULT_PROFILE)

        _init_styles()
        self._build_ui()

        # Size the window to fit its content, then center. The card grid's
        # natural height varies with the longest description (and with whether
        # the pyautogui warning is shown), so measuring after build keeps card
        # text from being clipped instead of hard-coding a height that isn't
        # tall enough. Clamp to the screen so it always fits on smaller displays.
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.W = max(self.W, self.root.winfo_reqwidth())
        self.H = min(self.root.winfo_reqheight(), sh - 40)
        x = (sw - self.W) // 2
        y = max(0, (sh - self.H) // 2)
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

    def _max_duration(self):
        """Maximum duration value allowed for the currently selected unit."""
        return 480 if self.unit_var.get() == "minutes" else 8

    def _validate_duration(self, value):
        """Allow empty (mid-edit) or an integer within the current unit's range."""
        if value == "":
            return True
        try:
            return 1 <= int(value) <= self._max_duration()
        except ValueError:
            return False

    def _duration_hours(self):
        """Resolve the duration control to a number of hours (float)."""
        try:
            val = self.duration_var.get()
        except tk.TclError:
            val = 2
        if val < 1:
            val = 1
        if self.unit_var.get() == "minutes":
            return max(1, val) / 60.0
        return min(max(val, 1), 8)

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg=BG_DARK, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=BG_DARK)
        title_frame.pack(pady=20)

        tk.Label(
            title_frame, text=APP_TITLE,
            font=("Segoe UI", 26, "bold"), fg=TEXT_PRIMARY, bg=BG_DARK
        ).pack(side="left")

        tk.Label(
            title_frame, text=f"  v{APP_VERSION}",
            font=("Segoe UI", 12), fg=TEXT_MUTED, bg=BG_DARK
        ).pack(side="left", pady=(12, 0))

        # ── pyautogui warning ──
        if not keep_alive.available:
            warn_frame = tk.Frame(self.root, bg="#3a2200")
            warn_frame.pack(fill="x", padx=30, pady=(0, 5))
            tk.Label(
                warn_frame,
                text="\u26a0  pyautogui not installed \u2014 keep-alive (mouse/keyboard injection) is disabled. Install with: pip install pyautogui",
                font=("Segoe UI", 9), fg=YELLOW_ACCENT, bg="#3a2200",
                wraplength=860, justify="left"
            ).pack(padx=10, pady=6)

        # ── Subtitle ──
        tk.Label(
            self.root,
            text="Choose a simulation mode. All modes keep you \"Active\" on every platform.",
            font=("Segoe UI", 10), fg=TEXT_SECONDARY, bg=BG_DARK
        ).pack(pady=(0, 5))

        # ── Duration Control ──
        dur_frame = tk.Frame(self.root, bg=BG_DARK)
        dur_frame.pack(pady=(0, 15))

        tk.Label(
            dur_frame, text="Duration",
            font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK
        ).pack(side="left", padx=(0, 8))

        vcmd = (self.root.register(self._validate_duration), "%P")
        self.dur_spin = tk.Spinbox(
            dur_frame, from_=1, to=self._max_duration(), width=4,
            textvariable=self.duration_var,
            validate="key", validatecommand=vcmd,
            font=("Consolas", 11), justify="center",
            bg=BG_INPUT, fg=ACCENT, insertbackground=ACCENT,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, relief="flat", bd=2,
            buttonbackground=BG_CARD
        )
        self.dur_spin.pack(side="left")

        # Unit toggle: hours or minutes
        unit_menu = tk.OptionMenu(dur_frame, self.unit_var, "hours", "minutes",
                                  command=self._on_unit_change)
        unit_menu.config(font=("Segoe UI", 9), bg=BG_INPUT, fg=TEXT_PRIMARY,
                         activebackground=BG_CARD_HOVER, activeforeground=ACCENT,
                         relief="flat", bd=0, highlightthickness=1,
                         highlightbackground=BORDER, width=7, cursor="hand2")
        unit_menu["menu"].config(bg=BG_CARD, fg=TEXT_PRIMARY,
                                 activebackground=ACCENT, activeforeground=BG_DARK)
        unit_menu.pack(side="left", padx=(8, 0))

        # Keep-alive intensity selector
        tk.Label(
            dur_frame, text="   Keep-alive",
            font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK
        ).pack(side="left", padx=(12, 6))

        intensity_menu = tk.OptionMenu(
            dur_frame, self.intensity_var, *KEEP_ALIVE_PROFILES.keys(),
            command=self._on_intensity_change)
        intensity_menu.config(font=("Segoe UI", 9), bg=BG_INPUT, fg=ACCENT,
                              activebackground=BG_CARD_HOVER, activeforeground=ACCENT,
                              relief="flat", bd=0, highlightthickness=1,
                              highlightbackground=BORDER, width=10, cursor="hand2")
        intensity_menu["menu"].config(bg=BG_CARD, fg=TEXT_PRIMARY,
                                      activebackground=ACCENT, activeforeground=BG_DARK)
        intensity_menu.pack(side="left")

        # Surprise Me — launches a random simulation
        tk.Button(
            dur_frame, text="\U0001f3b2  Surprise Me",
            font=("Segoe UI", 9, "bold"), bg="#1a2744", fg=ACCENT,
            activebackground=BG_CARD_HOVER, activeforeground=ACCENT_GLOW,
            relief="flat", bd=0, padx=14, pady=3, cursor="hand2",
            command=self._launch_random
        ).pack(side="left", padx=(16, 0))

        # Live hint describing the selected keep-alive profile
        self.intensity_hint = tk.Label(
            self.root,
            text=self._intensity_hint_text(),
            font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_DARK
        )
        self.intensity_hint.pack(pady=(0, 12))

        # ── Card Grid ──
        grid_frame = tk.Frame(self.root, bg=BG_DARK)
        grid_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # Widen the grid rather than adding a fourth row: three rows of cards
        # plus the header is about as tall as a 1080p screen can show, and the
        # window height is clamped to the display, which would clip card text.
        cols = 3 if len(SIMULATIONS) <= 9 else 4
        wrap = 240 if cols == 3 else 195

        self.cards = []
        for i, sim in enumerate(SIMULATIONS):
            row, col = divmod(i, cols)
            card = self._create_card(grid_frame, sim, wraplength=wrap)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.cards.append(card)

        for c in range(cols):
            grid_frame.columnconfigure(c, weight=1)
        num_rows = (len(SIMULATIONS) + cols - 1) // cols
        for r in range(num_rows):
            grid_frame.rowconfigure(r, weight=1)

        # ── Footer ──
        footer = tk.Frame(self.root, bg=BG_DARK, height=30)
        footer.pack(fill="x")
        tk.Label(
            footer,
            text="ESC exits any simulation  \u2022  pyautogui failsafe: move mouse to (0,0)  \u2022  Educational project",
            font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_DARK
        ).pack(pady=5)

    def _create_card(self, parent, sim, wraplength=240):
        """Create a glassmorphic simulation card."""
        card = tk.Frame(
            parent, bg=BG_CARD, highlightbackground=BORDER,
            highlightthickness=1, cursor="hand2"
        )
        card.columnconfigure(0, weight=1)

        # Inner padding frame
        inner = tk.Frame(card, bg=BG_CARD, padx=16, pady=14)
        inner.pack(fill="both", expand=True)

        # Icon
        icon_label = tk.Label(
            inner, text=sim["icon"], font=("Segoe UI", 28),
            fg=sim["color"], bg=BG_CARD
        )
        icon_label.pack(anchor="w")

        # Title
        title_label = tk.Label(
            inner, text=sim["title"],
            font=("Segoe UI", 13, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD,
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(6, 0))

        # Subtitle
        sub_label = tk.Label(
            inner, text=sim["subtitle"],
            font=("Segoe UI", 9), fg=sim["color"], bg=BG_CARD,
            anchor="w"
        )
        sub_label.pack(anchor="w")

        # Description (shown on hover via tooltip-like area)
        desc_label = tk.Label(
            inner, text=sim["desc"],
            font=("Segoe UI", 8), fg=TEXT_DESC, bg=BG_CARD,
            anchor="w", justify="left", wraplength=wraplength
        )
        desc_label.pack(anchor="w", pady=(8, 0))

        # Hover effects - bind to all children
        all_widgets = [card, inner, icon_label, title_label, sub_label, desc_label]
        card._hover_widgets = all_widgets
        card._hover_active = False
        for widget in all_widgets:
            widget.bind("<Enter>", lambda e, c=card, s=sim:
                self._on_card_enter(c, s))
            widget.bind("<Leave>", lambda e, c=card, s=sim:
                self._on_card_leave(c, s))
            widget.bind("<Button-1>", lambda e, s=sim: self._launch(s["id"]))

        return card

    def _on_card_enter(self, card, sim):
        if card._hover_active:
            return
        card._hover_active = True
        self._apply_hover(card, sim, True)

    def _on_card_leave(self, card, sim):
        # Check if mouse is still within the card bounds
        try:
            mx = card.winfo_pointerx() - card.winfo_rootx()
            my = card.winfo_pointery() - card.winfo_rooty()
            if 0 <= mx <= card.winfo_width() and 0 <= my <= card.winfo_height():
                return
        except Exception:
            pass
        card._hover_active = False
        self._apply_hover(card, sim, False)

    def _apply_hover(self, card, sim, entering):
        bg = BG_CARD_HOVER if entering else BG_CARD
        border = sim["color"] if entering else BORDER
        card.config(bg=bg, highlightbackground=border)
        for w in card._hover_widgets:
            try:
                w.config(bg=bg)
            except Exception:
                pass

    # Simulation registry: id -> (class, takes_duration)
    SIM_REGISTRY = {
        "bsod":          (BSODSimulation,          True),
        "security_scan": (SecurityScanSimulation,  True),
        "windows_update": (WindowsUpdateSimulation, True),
        "disk_defrag":   (DiskDefragSimulation,    True),
        "stay_active":   (StayActiveSimulation,    True),
        "code_build":    (CodeBuildSimulation,     True),
        "ai_training":   (AITrainingSimulation,    True),
        "matrix_rain":   (MatrixRainSimulation,    True),
        "bi_trainer":    (BITrainerSimulation,     True),
        "docs":          (DocumentationViewer,     False),
    }

    def _intensity_hint_text(self):
        """Build the hint line for the currently selected profile."""
        name = self.intensity_var.get()
        prof = KEEP_ALIVE_PROFILES.get(name, KEEP_ALIVE_PROFILES[DEFAULT_PROFILE])
        return (f"{name}: {prof['desc']}  "
                f"(mouse ~{prof['mouse']}s / key ~{prof['key']}s)")

    def _on_unit_change(self, *_):
        """Re-range the duration spinbox to match the unit and clamp the value."""
        max_val = self._max_duration()
        try:
            self.dur_spin.config(to=max_val)
            if self.duration_var.get() > max_val:
                self.duration_var.set(max_val)
        except tk.TclError:
            self.duration_var.set(2)

    def _on_intensity_change(self, *_):
        """Apply the chosen keep-alive intensity profile immediately."""
        keep_alive.set_profile(self.intensity_var.get())
        if hasattr(self, "intensity_hint"):
            self.intensity_hint.config(text=self._intensity_hint_text())

    def _launch_random(self):
        """Pick and launch a random simulation (excluding docs)."""
        choices = [sid for sid in self.SIM_REGISTRY if sid != "docs"]
        self._launch(random.choice(choices))

    def _launch(self, sim_id):
        """Launch the selected simulation."""
        entry = self.SIM_REGISTRY.get(sim_id)
        if entry is None:
            return

        # Apply current keep-alive intensity before the engine starts
        keep_alive.set_profile(self.intensity_var.get())

        self.root.withdraw()

        sim_class, takes_duration = entry
        try:
            if takes_duration:
                self.active_sim = sim_class(
                    self.root, self._show_launcher, self._duration_hours()
                )
            else:
                self.active_sim = sim_class(self.root, self._show_launcher)
        except Exception:
            # If a simulation fails to start, restore the launcher instead of
            # leaving the app withdrawn and seemingly frozen.
            self.active_sim = None
            self._show_launcher()

    def _show_launcher(self):
        """Return to the launcher after a simulation exits."""
        self.active_sim = None
        self.root.deiconify()
        self.root.focus_force()

    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = Launcher()
    app.run()
