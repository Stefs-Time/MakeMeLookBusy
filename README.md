# MakeMeLookBusy

Desktop activity simulator with a glassmorphic launcher menu. Built with Python and Tkinter for educational purposes -- demonstrates fullscreen overlays, threaded UI, canvas animation, and cross-platform idle-prevention techniques.

> **Disclaimer:** This is an educational/demonstration project. See [DISCLAIMER.md](./DISCLAIMER.md) for full terms. The authors do not encourage or endorse workplace deception of any kind.

## Simulation Modes

| Mode | Description |
|---|---|
| **Blue Screen of Death** | Pixel-perfect Windows 11 BSOD with random stop codes, looping progress, and hidden cursor. Auto-exits on duration expiry. |
| **Cyber Threat Scanner** | Enterprise security dashboard with live console, dual progress bars, AI threat scoring, and pause/resume with elapsed-time tracking. |
| **Windows Update** | Classic Windows Update with animated spinner dots and slow, erratic progress. Fullscreen with hidden cursor. |
| **Disk Optimization** | Drive defragmentation visualizer with per-drive status tracking, live block map, and completion finalization. |
| **Stay Active** | Silent keep-alive using micro mouse movements and shift key presses. Countdown timer with minimize support. Set duration and walk away. |
| **Code Compiler** | Developer build & test pipeline: resolves dependencies, compiles modules, bundles assets, and runs a passing test suite with live scrolling output. |
| **AI Model Training** | Neural-net training dashboard with live loss/accuracy curves, epoch counter, animated layer activations, and GPU telemetry. |
| **Matrix Rain** | Fullscreen cascading green digital rain with glowing lead characters and fading trails. Hidden cursor, always-on-top, auto-exit. |
| **Documentation** | Built-in viewer explaining every mode, keep-alive mechanics, and technical details. |

## Launcher Options

- **Duration** — set the runtime for any timed mode, in **hours or minutes**.
- **Keep-alive intensity** — choose **Stealth**, **Normal**, or **Aggressive** timing profiles.
- **🎲 Surprise Me** — launch a random simulation.
- **Universal ESC** — press ESC to exit *any* simulation instantly.

## Requirements

- Python 3.8+
- Tkinter (included with most Python installations)
- `pyautogui` (optional -- keep-alive features are disabled without it)

## Installation

```bash
git clone https://github.com/Stefs-Time/MakeMeLookBusy.git
cd MakeMeLookBusy
pip install -r requirements.txt
```

## Usage

```bash
python MakeMeLookBusy.py
```

The glassmorphic launcher will open. Pick a simulation mode, set a duration (in hours or minutes), choose a keep-alive intensity, or hit **🎲 Surprise Me** for a random mode. All timed modes auto-return to the launcher on completion.

### Controls

- **ESC** -- Exit *any* simulation instantly (fullscreen or windowed)
- **Stop / Minimize buttons** -- Exit or hide windowed simulations (Scanner, Defrag, Stay Active, Code Compiler, AI Training)
- **pyautogui failsafe** -- Move mouse to screen corner (0, 0) to force-stop input injection

## How It Works

All simulation modes share a `KeepAliveEngine` that runs in a background daemon thread. When active, it periodically:

- Moves the mouse by 1 pixel and back (plus the occasional 1-notch scroll)
- Presses a harmless key (Shift / Ctrl / F13–F15, rotated)
- Applies ±25% random jitter to every interval so the activity never looks robotic
- Tracks live stats (mouse moves / key presses)

Timing is governed by a selectable **intensity profile**:

| Profile | Mouse | Key | Use |
|---|---|---|---|
| **Stealth** | ~110s | ~150s | Minimal footprint |
| **Normal** | ~55s | ~80s | Balanced default |
| **Aggressive** | ~25s | ~35s | Never lets idle get close |

This prevents the OS and communication apps (Teams, Slack, etc.) from marking you as idle/away. The engine gracefully degrades if `pyautogui` is not installed.

## Technical Highlights

- **Single-file architecture** -- entire app (9 modes) in one Python file
- **Zero network calls** -- nothing is sent or received; fully offline
- **Thread-safe design** -- `threading.Event` and locks for clean start/stop
- **Graceful degradation** -- works without `pyautogui`, just without keep-alive
- **Cross-platform** -- Windows, macOS, and Linux via Tkinter

## License

[MIT](./LICENSE) -- Copyright (c) 2026 Stefs-Time

See [DISCLAIMER.md](./DISCLAIMER.md) for the full liability waiver.
