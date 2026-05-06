# Kalo Rituals

Kalo Rituals is a CSE423 computer graphics project built with OpenGL. The game is a horror-themed ritual survival experience that focuses on real-time rendering, camera control, and interactive gameplay mechanics.

## Map

![Map 1 Floor](Map%201%20Floor.jpg)
![Map 2 Floor](Map%202%20Floor.jpg)

## Gameplay Features

- Two-floor level design with teleport pad transitions.
- First-person and third-person camera toggle.
- Ritual artifact collection and placement logic.
- Enemy (ghost) behavior with timed visibility and stun states.
- Health system, HUD, and item inventory display.
- Difficulty selection and limited-use survival tools (regen/invisibility).

## Controls

- `W`, `A`, `S`, `D`: Move and rotate (after selecting difficulty).
- `1`, `2`, `3`: Select difficulty (Easy, Medium, Hard).
- `E`: Pick up gun (when prompted).
- Left Click: Fire the gun (single bullet).
- Right Click: Toggle first-person/third-person camera.
- `Space`: Look back.
- `F`: Use regen/invisibility (limited uses).
- `C`: Toggle cheat mode.
- `R`: Restart the game.
- `1` to `7`: Place ritual items (only in ritual rooms).

## Project Structure

```
.
├─ game.py
├─ OpenGL/
│  ├─ DLLS/
│  └─ ...
├─ Map 1 Floor.jpg
├─ Map 2 Floor.jpg
└─ README.md
```

## Libraries Used

- OpenGL bindings via the bundled `OpenGL/` package (PyOpenGL-style API).
- GLUT (FreeGLUT) for windowing and input, DLLs included in `OpenGL/DLLS`.

## How To Run

1. Ensure Python 3.x is installed.
2. Keep the `OpenGL/` folder in the project root (it is required for imports).
3. Make sure FreeGLUT DLLs are discoverable:
	- Add `OpenGL/DLLS` to your system `PATH`, or
	- Copy the correct DLL (for example, `freeglut64.vc14.dll` for 64-bit Python) into the project root.
4. Run the game:

```bash
python game.py
```