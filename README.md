# Kalo Rituals

A horror-themed ritual survival game built with Python and OpenGL for CSE423 (Computer Graphics). The player navigates a two-floor arena, collects ritual artifacts, and survives against a ghost enemy while managing limited survival resources.

## Map

![Map 1 Floor](Map%201%20Floor.jpg)
![Map 2 Floor](Map%202%20Floor.jpg)

## Gameplay Features

- Two-floor level design with teleport pad transitions between floors.
- First-person and third-person camera toggle.
- Ritual artifact collection and placement across seven item types: Candle, Lemon, Lighter, Rope, Doll, Wood, Red Powder.
- Ghost enemy with timed visibility, bullet collision, and freeze states.
- Health system with on-screen HUD displaying health, inventory, and status.
- Three difficulty modes selectable at game start (Easy, Medium, Hard).
- Gun pickup and single-bullet firing mechanic.
- Three regenerator charges usable for health recovery or temporary player invisibility (10-second duration).
- Ghost freeze triggered by bullet hit (30-second duration).
- Cheat mode for testing and development.
- Game restart without relaunching the process.

## Controls

| Input | Action |
|---|---|
| `W` / `A` / `S` / `D` | Move and rotate the player |
| `1` / `2` / `3` | Select difficulty (Easy / Medium / Hard) at start |
| `E` | Pick up the gun when in range |
| Left Click | Fire the gun (consumes the single available bullet) |
| Right Click | Toggle first-person / third-person camera |
| `Space` | Look back |
| `F` | Use a regenerator charge (health regen or invisibility) |
| `1` to `7` | Place a ritual item (only valid inside ritual rooms) |
| `C` | Toggle cheat mode |
| `R` | Restart the game |

## Project Structure

```
.
├── game.py                 # Full game source (single-file)
├── build.bat               # Windows build script (PyInstaller)
├── kalo_rituals.spec       # PyInstaller packaging configuration
├── hook-OpenGL.py          # PyInstaller hook for vendored OpenGL package
├── requirements.txt        # Build-time dependencies
├── OpenGL/                 # Vendored PyOpenGL package (no pip install required)
│   └── DLLS/               # FreeGLUT and GLE DLLs for Windows
├── Map 1 Floor.jpg
├── Map 2 Floor.jpg
└── README.md
```

## Dependencies

| Dependency | Source |
|---|---|
| Python 3.x stdlib (`math`, `random`, `time`) | Standard library — no install needed |
| PyOpenGL | Vendored locally in `OpenGL/` — no pip install needed |
| FreeGLUT | Bundled DLLs in `OpenGL/DLLS/` |

No external pip packages are required to run the game.

## Running the Game

1. Install Python 3.x (3.11 or 3.12 recommended).
2. Keep the `OpenGL/` folder in the project root — it is required for imports.
3. Ensure the FreeGLUT DLL is accessible. Either:
   - Add `OpenGL/DLLS` to your system `PATH`, or
   - Copy the matching DLL (e.g., `freeglut64.vc14.dll` for 64-bit Python) to the project root.
4. Run:

```bash
python game.py
```

## Building a Standalone Executable (Windows)

A PyInstaller-based build pipeline is included for producing a standalone `.exe` that does not require Python to be installed on the target machine.

**Requirements:** Python 3.11 or 3.12. Python 3.14 is not guaranteed to be supported by PyInstaller.

```bat
build.bat
```

The script installs PyInstaller, cleans previous artifacts, and runs `kalo_rituals.spec`. On success, the distributable folder is produced at:

```
dist\KaloRituals\KaloRituals.exe
```

Zip the entire `dist\KaloRituals\` folder for distribution.

To build manually:

```bash
pip install "pyinstaller>=6.0"
pyinstaller kalo_rituals.spec --clean
```
