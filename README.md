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
| **Stay Active** | Silent keep-alive using micro mouse movements and shift key presses. Countdown timer with minimize support. Set 1-8 hours and walk away. |
| **Documentation** | Built-in viewer explaining every mode, keep-alive mechanics, and technical details. |

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

The glassmorphic launcher will open. Select a simulation mode and set a duration (1-8 hours). All timed modes auto-return to the launcher on completion.

### Controls

- **ESC** -- Exit fullscreen simulations (BSOD, Windows Update)
- **Stop/Exit buttons** -- Exit windowed simulations (Scanner, Defrag, Stay Active)
- **pyautogui failsafe** -- Move mouse to screen corner (0, 0) to force-stop input injection

## How It Works

All simulation modes share a `KeepAliveEngine` that runs in a background daemon thread. When active, it periodically:

- Moves the mouse by 1 pixel and back (~every 55 seconds)
- Presses the Shift key (~every 80 seconds)

This prevents the OS and communication apps (Teams, Slack, etc.) from marking you as idle/away. The engine gracefully degrades if `pyautogui` is not installed.

## Technical Highlights

- **Single-file architecture** -- entire app in one 1,500-line Python file
- **Zero network calls** -- nothing is sent or received; fully offline
- **Thread-safe design** -- `threading.Event` and locks for clean start/stop
- **Graceful degradation** -- works without `pyautogui`, just without keep-alive
- **Cross-platform** -- Windows, macOS, and Linux via Tkinter

## License

[MIT](./LICENSE) -- Copyright (c) 2026 Stefs-Time

See [DISCLAIMER.md](./DISCLAIMER.md) for the full liability waiver.
