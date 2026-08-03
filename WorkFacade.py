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

        self.cards = []
        for i, sim in enumerate(SIMULATIONS):
            row, col = divmod(i, 3)
            card = self._create_card(grid_frame, sim)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.cards.append(card)

        for c in range(3):
            grid_frame.columnconfigure(c, weight=1)
        num_rows = (len(SIMULATIONS) + 2) // 3
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

    def _create_card(self, parent, sim):
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
            anchor="w", justify="left", wraplength=240
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
