"""
MakeMeLookBusy - The Ultimate "I'm Working" Simulator
=====================================================
A single unified app with a glassmorphic launcher menu.
Choose a simulation mode and it runs fullscreen, keeping
you "active" on all platforms while looking completely legit.

Educational / demonstration project showing how activity
simulation, fullscreen overlays, and idle-prevention work
on Windows.

Requirements: pip install pyautogui
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random
import os
import sys
import ctypes
from datetime import datetime, timedelta

try:
    import pyautogui
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None


# ═══════════════════════════════════════════════════════════════
# CONSTANTS & THEME
# ═══════════════════════════════════════════════════════════════

APP_TITLE = "MakeMeLookBusy"
APP_VERSION = "2.0"

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
BORDER = "#1e2d4a"
BORDER_HOVER = "#2a4070"
RED_ACCENT = "#ff4757"
YELLOW_ACCENT = "#ffd32a"
BLUE_ACCENT = "#3498db"
CYAN_ACCENT = "#00d2d3"
ORANGE_ACCENT = "#ff9f43"

# Simulation card definitions
SIMULATIONS = [
    {
        "id": "bsod",
        "icon": "\u2620",
        "title": "Blue Screen of Death",
        "subtitle": "Windows BSOD Simulation",
        "desc": "Displays a pixel-perfect Windows 11 BSOD fullscreen. Nobody will bother you while your PC is 'crashed'. Press ESC to exit.",
        "color": "#3498db",
    },
    {
        "id": "security_scan",
        "icon": "\U0001f6e1",
        "title": "Cyber Threat Scanner",
        "subtitle": "Enterprise Security Audit",
        "desc": "Runs a convincing cybersecurity behavioral analytics scan with live console output, progress bars, threat flags, and AI analysis. Looks like a serious corporate security tool.",
        "color": "#00e5a0",
    },
    {
        "id": "windows_update",
        "icon": "\u2b6f",
        "title": "Windows Update",
        "subtitle": "System Update Simulation",
        "desc": "Shows the classic Windows Update screen with a slowly creeping progress bar. 'Don't turn off your computer.' Nobody questions a Windows Update.",
        "color": "#0078d4",
    },
    {
        "id": "disk_defrag",
        "icon": "\u2b13",
        "title": "Disk Optimization",
        "subtitle": "Drive Defrag & Analysis",
        "desc": "Simulates a Windows disk optimization/defragmentation process with drive analysis, block visualization, and detailed progress. A classic IT excuse.",
        "color": "#ff9f43",
    },
    {
        "id": "stay_active",
        "icon": "\u2615",
        "title": "Stay Active",
        "subtitle": "Invisible Keep-Alive",
        "desc": "No flashy screen \u2014 just silently keeps your PC awake with micro mouse movements and shift key presses. All platforms see you as 'Active'. Set duration and walk away.",
        "color": "#ffd32a",
    },
    {
        "id": "docs",
        "icon": "\u2139",
        "title": "Documentation",
        "subtitle": "How It Works & Why",
        "desc": "Full breakdown of every simulation mode, the techniques used, and the educational purpose behind this project.",
        "color": "#7a8ba8",
    },
]


# ═══════════════════════════════════════════════════════════════
# KEEP-ALIVE ENGINE (shared across all simulation modes)
# ═══════════════════════════════════════════════════════════════

class KeepAliveEngine:
    """Background thread that prevents idle/away status."""

    def __init__(self):
        self.running = False
        self._thread = None
        self.mouse_interval = 55
        self.key_interval = 80

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        last_mouse = time.time()
        last_key = time.time()
        while self.running:
            now = time.time()
            if pyautogui and now - last_mouse > self.mouse_interval:
                try:
                    pyautogui.moveRel(1, 0, duration=0.05)
                    pyautogui.moveRel(-1, 0, duration=0.05)
                except Exception:
                    pass
                last_mouse = now
            if pyautogui and now - last_key > self.key_interval:
                try:
                    pyautogui.press("shift")
                except Exception:
                    pass
                last_key = now
            time.sleep(0.5)


# Global keep-alive instance
keep_alive = KeepAliveEngine()


# ═══════════════════════════════════════════════════════════════
# SIMULATION: BSOD
# ═══════════════════════════════════════════════════════════════

class BSODSimulation:
    """Fullscreen Windows 11 Blue Screen of Death."""

    def __init__(self, parent_root, on_exit):
        self.on_exit = on_exit
        self.win = tk.Toplevel(parent_root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#0078d4")
        self.win.focus_force()

        # Hide cursor
        self.win.config(cursor="none")

        # Bind escape
        self.win.bind("<Escape>", self._exit)
        self.win.bind("<Key>", self._on_key)

        self._build_ui()
        keep_alive.start()

        # Start the fake progress
        self.progress = 0
        self._tick()

    def _build_ui(self):
        w = self.win.winfo_screenwidth()
        h = self.win.winfo_screenheight()

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

    def _on_key(self, event):
        if event.keysym == "Escape":
            self._exit()

    def _exit(self, event=None):
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

        self.win = tk.Toplevel(parent_root)
        self.win.title("Cyber Threat Behavioral Analytics Engine v9.4")
        self.win.geometry("1100x750")
        self.win.configure(bg="#0a0e17")
        self.win.protocol("WM_DELETE_WINDOW", self._exit)

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

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Green.Horizontal.TProgressbar",
                         background=ACCENT, troughcolor="#1a2235")
        style.configure("Cyan.Horizontal.TProgressbar",
                         background=CYAN_ACCENT, troughcolor="#1a2235")

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
        elapsed = time.time() - self.start_time
        h, m, s = int(elapsed // 3600), int((elapsed % 3600) // 60), int(elapsed % 60)
        self.elapsed_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.win.after(1000, self._update_elapsed)

    def _scan_loop(self):
        start = time.time()
        while self.scanning and (time.time() - start < self.duration):
            while self.paused:
                time.sleep(0.1)
                if not self.scanning:
                    return

            elapsed = time.time() - start
            overall = min(99, (elapsed / self.duration) * 100)

            try:
                self.win.after(0, lambda v=overall: self._update_bars(v, 0))
                self.win.after(0, lambda v=overall: self.status_label.config(
                    text=f"SCANNING \u2014 Phase {random.randint(1, 8)}"
                ))
                self.win.after(0, lambda v=overall: self.percent_label.config(
                    text=f"{int(v)}%"
                ))
            except Exception:
                return

            # Phase header
            phase = random.choice(self.SCAN_PHASES)
            self.win.after(0, lambda p=phase: self._log(f"\n--- {p} ---", "cyan"))

            # Module progress simulation
            for mp in range(0, 101, random.randint(5, 15)):
                if not self.scanning:
                    return
                while self.paused:
                    time.sleep(0.1)
                self.win.after(0, lambda v=overall, m=mp: self._update_bars(v, m))
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
                self.win.after(0, lambda i=item, s=status, t=tag:
                    self._log(f"  {i:<42} [{s}]", t))
                time.sleep(random.uniform(0.08, 0.25))

            # Random events
            if random.random() < 0.15:
                self.win.after(0, lambda: self._log(
                    "  Subsystem latency spike \u2014 auto-correcting", "yellow"))
            if random.random() < 0.08:
                self.win.after(0, lambda: self._log(
                    "  Packet capture: anomalous traffic pattern logged", "orange"))
            if random.random() < 0.05:
                conf = round(random.uniform(0.4, 0.99), 2)
                score = int(conf * random.randint(80, 200))
                self.win.after(0, lambda c=conf, s=score: self._log(
                    f"  [AI] ThreatScoreNet inference \u2014 conf: {c} \u2014 score: {s}", "blue"))

            time.sleep(random.uniform(0.3, 1.5))

        if self.scanning:
            self.win.after(0, lambda: self._log(
                "\n=== SYSTEM SCAN COMPLETE \u2014 REPORT GENERATED ===", "green"))
            self.win.after(0, lambda: self._update_bars(100, 100))
            self.win.after(0, lambda: self.status_label.config(text="COMPLETE"))
            self.win.after(0, lambda: self.percent_label.config(text="100%"))

    def _update_bars(self, overall, module):
        try:
            self.overall_bar["value"] = overall
            self.module_bar["value"] = module
        except Exception:
            pass

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="RESUME", fg=ACCENT)
            self._log("=== SCAN PAUSED ===", "yellow")
        else:
            self.pause_btn.config(text="PAUSE", fg=YELLOW_ACCENT)
            self._log("=== SCAN RESUMED ===", "green")

    def _exit(self):
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
            self.progress_label.config(text="100% complete")
            keep_alive.stop()
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

        style = ttk.Style()
        style.configure("Defrag.Horizontal.TProgressbar",
                         background=ACCENT, troughcolor="#333333")

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
        colors = ["#00e5a0", "#0078d4", "#ff9f43", "#ff4757", "#333333", "#1a1a1a"]
        weights = [40, 20, 8, 3, 20, 9]
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

        drive_idx = 0
        while self.running and time.time() - self.start_time < self.duration:
            elapsed = time.time() - self.start_time
            pct = min(99, int((elapsed / self.duration) * 100))

            # Update drive statuses
            current_drive = drive_idx % len(self.DRIVE_NAMES)
            try:
                self.win.after(0, lambda p=pct: self.progress_bar.configure(value=p))
                self.win.after(0, lambda p=pct: self.progress_label.config(text=f"{p}%"))
                self.win.after(0, lambda a=random.choice(actions): self.action_label.config(text=a))

                for i, lbl in enumerate(self.drive_labels):
                    if i < current_drive:
                        self.win.after(0, lambda l=lbl: l.config(text="OK (0% fragmented)", fg=ACCENT))
                    elif i == current_drive:
                        self.win.after(0, lambda l=lbl, p=pct: l.config(
                            text=f"Optimizing ({p}%)", fg=ORANGE_ACCENT))
                    else:
                        self.win.after(0, lambda l=lbl: l.config(text="Queued", fg=YELLOW_ACCENT))
            except Exception:
                return

            # Periodically redraw blocks
            if random.random() < 0.15:
                self.win.after(0, self._draw_blocks)

            if pct > 33 * (drive_idx + 1):
                drive_idx += 1

            time.sleep(random.uniform(1.0, 3.0))

    def _exit(self):
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
        self.win.geometry("440x280")
        self.win.configure(bg=BG_DARK)
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._exit)

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

        tk.Label(
            self.win, text="Mouse & keyboard activity running silently",
            font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK
        ).pack()

        self.time_label = tk.Label(
            self.win, text="Remaining: --:--:--",
            font=("Consolas", 16), fg=ACCENT, bg=BG_DARK
        )
        self.time_label.pack(pady=20)

        style = ttk.Style()
        style.configure("Active.Horizontal.TProgressbar",
                         background=YELLOW_ACCENT, troughcolor="#1a2235")

        self.progress = ttk.Progressbar(
            self.win, length=380, mode="determinate",
            style="Active.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=(0, 15))

        tk.Button(
            self.win, text="STOP", font=("Segoe UI", 10, "bold"),
            bg="#2a1525", fg=RED_ACCENT, relief="flat", padx=20, pady=4,
            command=self._exit, cursor="hand2"
        ).pack()

    def _tick(self):
        if not self.running or not self.win.winfo_exists():
            return

        remaining = max(0, self.duration - (time.time() - self.start_time))
        total = self.duration
        pct = ((total - remaining) / total) * 100

        self.progress["value"] = pct
        td = str(timedelta(seconds=int(remaining)))
        self.time_label.config(text=f"Remaining: {td}")

        if remaining <= 0:
            self.time_label.config(text="Done!", fg=ACCENT)
            keep_alive.stop()
            return

        self.win.after(1000, self._tick)

    def _exit(self):
        self.running = False
        keep_alive.stop()
        self.win.destroy()
        self.on_exit()


# ═══════════════════════════════════════════════════════════════
# DOCUMENTATION VIEWER
# ═══════════════════════════════════════════════════════════════

DOCS_TEXT = """
\u2550\u2550\u2550  MakeMeLookBusy \u2014 Documentation  \u2550\u2550\u2550

\u2501\u2501\u2501  WHAT IS THIS?  \u2501\u2501\u2501

MakeMeLookBusy is an educational demonstration project that shows how
desktop activity simulation works on Windows. It combines multiple
"excuse screens" into a single launcher with a clean glassmorphic UI.

Every mode has two jobs:
  1. Display a convincing fullscreen simulation
  2. Keep your PC marked as "Active" on all platforms


\u2501\u2501\u2501  HOW DOES KEEP-ALIVE WORK?  \u2501\u2501\u2501

Windows (and apps like Teams, Slack, etc.) detect idle status by
monitoring input events. If no mouse movement or keystrokes happen
for a threshold period (usually 3-5 minutes), you go "Away".

MakeMeLookBusy prevents this with a background KeepAliveEngine that:
  \u2022 Moves the mouse by 1 pixel and back every ~55 seconds
  \u2022 Sends a Shift key press every ~80 seconds
  \u2022 Runs on a daemon thread so it doesn't block the UI
  \u2022 Uses pyautogui for cross-application input injection

The movements are invisible (1px) and Shift alone has no effect in
any application, so nothing gets disrupted.


\u2501\u2501\u2501  SIMULATION MODES  \u2501\u2501\u2501

\u2590 BLUE SCREEN OF DEATH (BSOD)
  Renders a pixel-perfect Windows 11 blue screen with:
  \u2022 The iconic ":(" sad face
  \u2022 Slowly creeping percentage counter (0-100%, then loops)
  \u2022 Random real Windows stop codes
  \u2022 QR code placeholder and support URL
  \u2022 Hidden cursor, fullscreen, always-on-top
  \u2022 Press ESC to exit

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
  \u2022 Pause/Resume functionality
  \u2022 Configurable duration (set before launch)

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

  Why it works: Everyone has been trapped by a Windows Update.
  Nobody questions it. Nobody tries to use your machine. The
  progress is intentionally slow and erratic (just like real
  Windows Updates).


\u2590 DISK OPTIMIZATION
  A Windows-style drive defragmentation tool:
  \u2022 Drive list with SSD/HDD types and status
  \u2022 Colorful block map visualization that updates live
  \u2022 Rotating action descriptions
  \u2022 Per-drive status progression
  \u2022 Realistic progress bar

  Why it works: Disk optimization is a known "IT maintenance" task.
  It looks technical, has visual elements that suggest real work,
  and nobody wants to interrupt a defrag.


\u2590 STAY ACTIVE (Invisible Mode)
  No flashy screen \u2014 pure stealth:
  \u2022 Tiny control window with countdown timer
  \u2022 Micro mouse movements (1px, invisible)
  \u2022 Periodic Shift key presses (no visible effect)
  \u2022 Set duration from 1-8 hours

  Why it works: If you just need to step away without any cover
  story, this keeps every platform showing you as "Active" with
  zero visual footprint. Minimize the window and walk away.


\u2501\u2501\u2501  TECHNICAL DETAILS  \u2501\u2501\u2501

  Framework:        Python + Tkinter (built-in, no web server)
  Input Injection:  pyautogui (cross-platform mouse/keyboard)
  Threading:        daemon threads for background activity
  UI Updates:       root.after() for thread-safe GUI updates
  Fullscreen:       tk attributes -fullscreen + -topmost
  Cursor Hide:      config(cursor="none") on fullscreen windows

  pyautogui.FAILSAFE is ON \u2014 move mouse to top-left corner
  to force-quit if anything goes wrong.


\u2501\u2501\u2501  USAGE NOTES  \u2501\u2501\u2501

  \u2022 Install dependency:  pip install pyautogui
  \u2022 Run:                 python MakeMeLookBusy.py
  \u2022 ESC exits fullscreen modes (BSOD, Windows Update)
  \u2022 Close window / Stop button exits windowed modes
  \u2022 pyautogui failsafe: move mouse to (0,0) corner to abort


\u2501\u2501\u2501  DISCLAIMER  \u2501\u2501\u2501

  This is an EDUCATIONAL project demonstrating UI simulation,
  input injection, and idle-prevention techniques. It is provided
  for learning purposes and should be used responsibly.
"""


class DocumentationViewer:
    """In-app documentation viewer."""

    def __init__(self, parent_root, on_exit):
        self.on_exit = on_exit

        self.win = tk.Toplevel(parent_root)
        self.win.title("MakeMeLookBusy \u2014 Documentation")
        self.win.geometry("800x650")
        self.win.configure(bg=BG_DARK)
        self.win.protocol("WM_DELETE_WINDOW", self._exit)

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
        self.root.geometry("920x720")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        # Center on screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 920) // 2
        y = (sh - 720) // 2
        self.root.geometry(f"920x720+{x}+{y}")

        self.active_sim = None
        self.duration_var = tk.IntVar(value=2)

        self._build_ui()

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

        dur_spin = tk.Spinbox(
            dur_frame, from_=1, to=8, width=3,
            textvariable=self.duration_var,
            font=("Consolas", 11), justify="center",
            bg=BG_INPUT, fg=ACCENT, insertbackground=ACCENT,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, relief="flat", bd=2,
            buttonbackground=BG_CARD
        )
        dur_spin.pack(side="left")

        tk.Label(
            dur_frame, text="hours",
            font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            dur_frame, text="(applies to timed modes)",
            font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_DARK
        ).pack(side="left", padx=(12, 0))

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
        for r in range(2):
            grid_frame.rowconfigure(r, weight=1)

        # ── Footer ──
        footer = tk.Frame(self.root, bg=BG_DARK, height=30)
        footer.pack(fill="x")
        tk.Label(
            footer,
            text="ESC exits fullscreen modes  \u2022  pyautogui failsafe: move mouse to (0,0)  \u2022  Educational project",
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
            font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_CARD,
            anchor="w", justify="left", wraplength=240
        )
        desc_label.pack(anchor="w", pady=(8, 0))

        # Hover effects - bind to all children
        all_widgets = [card, inner, icon_label, title_label, sub_label, desc_label]
        for widget in all_widgets:
            widget.bind("<Enter>", lambda e, c=card, a=all_widgets, s=sim:
                self._on_hover(c, a, s, True))
            widget.bind("<Leave>", lambda e, c=card, a=all_widgets, s=sim:
                self._on_hover(c, a, s, False))
            widget.bind("<Button-1>", lambda e, s=sim: self._launch(s["id"]))

        return card

    def _on_hover(self, card, widgets, sim, entering):
        bg = BG_CARD_HOVER if entering else BG_CARD
        border = sim["color"] if entering else BORDER
        card.config(bg=bg, highlightbackground=border)
        for w in widgets:
            try:
                w.config(bg=bg)
            except Exception:
                pass

    def _launch(self, sim_id):
        """Launch the selected simulation."""
        self.root.withdraw()

        if sim_id == "bsod":
            self.active_sim = BSODSimulation(self.root, self._show_launcher)
        elif sim_id == "security_scan":
            self.active_sim = SecurityScanSimulation(
                self.root, self._show_launcher, self.duration_var.get()
            )
        elif sim_id == "windows_update":
            self.active_sim = WindowsUpdateSimulation(
                self.root, self._show_launcher, self.duration_var.get()
            )
        elif sim_id == "disk_defrag":
            self.active_sim = DiskDefragSimulation(
                self.root, self._show_launcher, self.duration_var.get()
            )
        elif sim_id == "stay_active":
            self.active_sim = StayActiveSimulation(
                self.root, self._show_launcher, self.duration_var.get()
            )
        elif sim_id == "docs":
            self.active_sim = DocumentationViewer(self.root, self._show_launcher)

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
