# Voron Trident 350 3D Printing & CAD Automation Pipeline

Modular, open-source pipeline for generating, repairing, validating, and slicing 3D models for the **Voron Trident 350** ($350 \times 350 \times 250\text{ mm}$) using local **NVIDIA RTX 3090** GPU acceleration, **Build123d** parametric CAD, and **OrcaSlicer**.

---

## Key Features

1. **Voron 350 Pre-Flight Checks**:
   - Manifold & watertightness verification.
   - Exact bed fit check ($350 \times 350 \times 250\text{ mm}$ with safe margins).
   - Automatic bed orientation (maximizes contact area, minimizes overhangs).
   - Accurate volume and filament weight estimation for ABS, ASA, PETG, PLA.
2. **Parametric CAD (Build123d)**:
   - Generate engineering parts programmatically.
   - Dual-export: Lossless `.step` for CAD and high-precision `.stl` / `.3mf` for 3D printing.
3. **OrcaSlicer GUI Workflow (Default)**:
   - Cleans and prepares STLs into `outputs/<project>/` and automatically opens the file in OrcaSlicer GUI for manual support and seam adjustments.
4. **Optional Headless Slicing & Klipper Dispatch**:
   - Add `--slice` to run headless OrcaSlicer CLI slicing to `.gcode`.
   - Add `--upload` to send G-code directly to your Voron's Moonraker API.

---

## Quick Start

### 1. Check System & Hardware Status
```bash
.venv\Scripts\python.exe src/pipeline.py status
```

### 2. Process an Existing 3D File (STL / OBJ / 3MF)
```bash
# Validates, auto-orients, saves clean STL/3MF, and opens in OrcaSlicer GUI
.venv\Scripts\python.exe src/pipeline.py process "inputs/my_model.stl"

# Stop at clean STL export without launching GUI
.venv\Scripts\python.exe src/pipeline.py process "inputs/my_model.stl" --no-gui
```

### 3. Generate a Parametric Engineering Component
```bash
# Generate a Voron extrusion mount / bracket / Gridfinity bin
.venv\Scripts\python.exe src/pipeline.py template l-bracket
.venv\Scripts\python.exe src/pipeline.py template extrusion-mount
.venv\Scripts\python.exe src/pipeline.py template gridfinity
.venv\Scripts\python.exe src/pipeline.py template cable-clip
```

---

## Project Structure

```
├── inputs/                # Drop reference images, prompts, or downloaded STLs here
├── outputs/               # Clean STLs, 3MFs, STEP files, and slice logs
├── src/
│   ├── config.py          # Voron Trident specs & paths
│   ├── generators/        # Build123d parametric CAD & AI Image-to-3D
│   ├── mesh_prep/         # Validator, auto-orienter, bed scaler
│   ├── slicer/            # OrcaSlicer GUI launcher & CLI runner
│   ├── klipper/           # Moonraker REST API client
│   └── pipeline.py        # Master CLI entrypoint
└── pyproject.toml         # Python virtual environment dependencies
```
