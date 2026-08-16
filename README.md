# Sphere Gear — Spherical Gear Generator

Generates two mating gears:

- **Spherical Gear** — a sphere-shaped gear (intersection of two revolved involute profiles)
- **Monopole Gear** — a cylindrical gear whose teeth are cut by rolling the spherical gear around it

Both gears mesh together with the correct conjugate tooth profile.

## How It Works

### Spherical Gear (`spherical_gear.py`)

1. `py_gearworks` builds a precise involute tooth profile (Wire in the XY plane)
2. The profile is split in half twice — along X and along Y — producing two half-contours
3. Each half-contour is revolved around its respective axis — producing two solids of revolution
4. Boolean intersection (`^`) via `manifold3d` yields a sphere with teeth along both axes

```
     Tooth profile (XY)
            │
    ┌───────┼───────┐
    │  Half Y ≥ 0   │ → revolve around X → Body 1 ─┐
    │       │       │                                ├─ Intersection → Sphere
    │  Half X ≥ 0   │ → revolve around Y → Body 2 ─┘
    └───────┼───────┘
```

### Monopole Gear (`monopole_gear.py`)

1. A cylindrical blank is created (with a bore hole and chamfers)
2. A 3D cutter is built — the tooth profile revolved around the X axis (simulating the spherical gear)
3. The cutter rolls around the blank in 720 steps:
   - At each step the cutter spins around its own axis and orbits around the blank
   - Gear ratio: spin/orbit = `MONOPOLE_TEETH / TEETH`
4. The result is a cylinder with curved teeth perfectly conjugate to the spherical gear

```
    Cutter (revolved body)
        ╭───╮
       ╱     ╲      orbit (around Z)
      │   ●   │  ←──────────────╮
       ╲     ╱                  │
        ╰───╯                   │
    spin (around X)        ╭────┴────╮
                           │  Blank  │
                           │(cylinder)│
                           ╰─────────╯
```

### Shared Utilities (`utils.py`)

`shape_to_manifold` — converts a build123d Shape into a manifold3d Manifold via tessellation and trimesh.

### Configuration (`config.py`)

All parameters in one place: diameter, tooth count, angles, coefficients, clearances.

## Installation

Python **3.10+** (tested on 3.13).

```bash
pip install build123d numpy trimesh manifold3d py-gearworks
```

| Package | Purpose |
|---|---|
| `build123d` | Parametric 3D modeling (OpenCascade wrapper) |
| `py-gearworks` | Precise involute tooth profile generation |
| `manifold3d` | Fast boolean mesh operations (replaces slow OCCT booleans) |
| `trimesh` | Triangle mesh processing and STL export |
| `numpy` | Numeric arrays for mesh data |

> **Note:** `build123d` pulls in OpenCascade (~300 MB), the first install may take a while.

## Usage

```bash
# Generate the spherical gear
python spherical_gear.py

# Generate the monopole gear (takes several minutes)
python monopole_gear.py
```

Output: `spherical_gear.stl` and `monopole_gear.stl` in the current directory.

## Configuration

All parameters are set in `config.py`:

```python
DIAMETER = 50.0           # Outer sphere diameter (mm)
TEETH = 32                # Spherical gear tooth count
PRESSURE_ANGLE_DEG = 20.0 # Pressure angle (standard 20°)
MONOPOLE_TEETH = 16       # Monopole teeth (gear ratio = TEETH:MONOPOLE_TEETH)
MONOPOLE_BORE_DIAMETER = 8.0  # Monopole gear bore diameter (mm)
```
