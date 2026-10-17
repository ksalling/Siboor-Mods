# Siboor Lineux Mod — Siboor Voron Trident CNC Carriage Adaptation

This repository contains the parametric CAD modifications (`STEP` and `STL`) to mount the **Lineux Hotswap Toolchanger Carriage** (`LineuxCarriage.step` & `LineuxTool.step`) directly onto the stock **Siboor Voron Trident CNC Carriage** (`siboorCNC.step` on an `MGN12H` linear rail block), replacing the stock `carriage_base` part.

---

## Key Engineering Highlights

1. **Zero Modifications to `siboorCNC.step`:**
   - The machined aluminum Siboor CNC carriage is untouched and uses only its existing M3 threaded/clearance holes.
2. **Option A Forward Offset ($\Delta Y = -18.0\text{ mm}$):**
   - Shifts the Lineux carriage interface and `LineuxTool` forward by $18.0\text{ mm}$ so the stock $20\text{ mm}$-deep `Nema 14 Stepper` (`Y = 142.10..162.10\text{ mm}`) clears the front of `siboorCNC`'s upper-left ear (`Y = 162.90\text{ mm}`) by $0.80\text{ mm}$ without modifying `gear_plate`, and the `micro switch` clears `siboorCNC`'s $Y = 155.00\text{ mm}$ standoffs.
3. **100% Sealed Part-Cooling Airflow:**
   - Air enters through the extended `duct_extension` over the top of `siboorCNC` / `MGN12H`, passes through a sealed internal telescopic spigot joint into the vertical manifold in front of `siboorCNC`, and exits exclusively through the bottom bifurcated nozzle outlets of `[a]_duct` (`Z = -1.29\text{ mm}`).
4. **Two Complete Design Variants Included:**
   - **`Variant_A_Modular_Carriage`**: Integrates the vertical airflow channel ($14.04 \times 7.00\text{ mm} = 98.3\text{ mm}^2$, 100% of stock flow area) and the `siboorCNC` mounting bridge directly into `carriage`, paired with a separate modified `[a]_duct` featuring an upward telescopic sealing spigot and lower `siboorCNC` mounting bosses.
   - **`Variant_B_Integrated_Duct` (Forked Expanded `[a]_duct`)**: Expands `[a]_duct` upward and rearward into a single monolithic part integrating an oversized vertical plenum ($14.04 \times 14.20\text{ mm} = 199.4\text{ mm}^2$, **+103% internal cross-sectional flow area**), the `siboorCNC` mounting bridge, and a direct top telescopic connection to `duct_extension`.
5. **Dual Cartographer & LED Mounting Options:**
   - **Standard `[a]_duct` Mount**: Both `led_mount` and `cartographer_mount` bolt directly to their stock locations on `[a]_duct` (shifted by $\Delta Y = -18.0\text{ mm}$).
   - **Optional Direct `siboorCNC` Cartographer Mount (`siboor_cartographer_mount`)**: Bolts directly to `siboorCNC`'s two bottom vertical M3 holes (`X = 110.90, 142.50\text{ mm}, Y = 167.30\text{ mm}, Z = 14.52\text{ mm}`), holding the Cartographer probe at $Z = 1.524\text{ mm}$ ($2.40\text{ mm}$ above the nozzle tip at $Z = -0.88\text{ mm}$) while `led_mount` remains mounted on `[a]_duct`.

---

## Directory Structure

```text
Siboor Lineux Mod/
├── README.md
├── docs/
│   ├── siboor_lineux_2d_cross_section.png
│   ├── siboor_lineux_2d_xz_xy_views.png
│   ├── siboor_lineux_variants_ab_centerline_2d.png
│   └── siboor_lineux_variants_ab_xy_slices_2d.png
├── Variant_A_Modular_Carriage/
│   ├── CAD/
│   │   ├── carriage.step
│   │   ├── [a]_duct.step
│   │   ├── duct_extension.step
│   │   ├── 5015_standoff_x2.step
│   │   ├── 5015_standoff_x2 (1).step
│   │   ├── siboor_cartographer_mount.step
│   │   ├── Siboor_Lineux_Carriage_Assembly.step
│   │   └── Siboor_Lineux_Carriage_With_Tool_Assembly.step
│   └── STL/
│       ├── carriage.stl
│       ├── [a]_duct.stl
│       ├── duct_extension.stl
│       ├── 5015_standoff_x2.stl
│       ├── 5015_standoff_x2 (1).stl
│       └── siboor_cartographer_mount.stl
└── Variant_B_Integrated_Duct/
    ├── CAD/
    │   ├── [a]_duct.step
    │   ├── carriage.step
    │   ├── duct_extension.step
    │   ├── 5015_standoff_x2.step
    │   ├── 5015_standoff_x2 (1).step
    │   ├── siboor_cartographer_mount.step
    │   ├── Siboor_Lineux_Carriage_Assembly.step
    │   └── Siboor_Lineux_Carriage_With_Tool_Assembly.step
    └── STL/
        ├── [a]_duct.stl
        ├── carriage.stl
        ├── duct_extension.stl
        ├── 5015_standoff_x2.stl
        ├── 5015_standoff_x2 (1).stl
        └── siboor_cartographer_mount.stl
```

---

## Hardware & Fastener Map (`siboorCNC` Connections)

| Location on `siboorCNC` | World Coords $(X, Y, Z)\text{ [mm]}$ | Hole Type | Fastener |
| :--- | :--- | :--- | :--- |
| **Upper Forward Standoffs (2x)** | $X = 111.20, 142.20$, $Y = 155.00$, $Z = 73.02$ | M3 Tapped ($\varnothing 2.46$) | 2x M3x12 SHCS (Variant A) / M3x10 SHCS (Variant B) |
| **Inner Plate Pattern (4x)** | $X = 118.70, 134.70$, $Y = 165.10$, $Z = 65.82, 50.82$ | $\varnothing 3.00$ Through | 4x M3x16 SHCS (with rear M3 nut or thread engagement) |
| **Top Ear Rear Mounts (2x)** | $X = 110.50, 142.90$, $Y = 163.14..169.50$, $Z = 81.32$ | M3 Tapped ($\varnothing 2.46$) | 2x M3x35 SHCS through `duct_extension` rear ears |
| **Lower Outer Plate Holes (2x)** | $X = 108.75, 144.65$, $Y = 165.10$, $Z = 43.27$ | $\varnothing 3.00$ Through | 2x M3x12 SHCS |
| **Lower Bridge Holes (2x)** | $X = 121.45, 131.95$, $Y = 165.10$, $Z = 39.05$ | M3 Tapped ($\varnothing 2.46$) | 2x M3x16 SHCS |
| **Lower Forward Standoffs (2x)** | $X = 110.45, 142.95$, $Y = 155.00$, $Z = 29.72$ | M3 Tapped ($\varnothing 2.46$) | 2x M3x8 SHCS |
| **Bottom Vertical Probe Mounts (2x)** | $X = 110.90, 142.50$, $Y = 167.30$, $Z = 14.52$ | M3 Tapped ($\varnothing 2.46$) | 2x M3x8 SHCS (for optional `siboor_cartographer_mount`) |

---

## Parametric Regeneration & Future Iterations

All CAD generation and 2D cross-section verification scripts are stored in `src/siboor_lineux/`:
- `src/siboor_lineux/cache_inputs.py`: Extracts and caches individual `.brep` solids and RGB metadata from `inputs/*.step` into `cache/siboor_lineux/`.
- `src/siboor_lineux/generator.py`: Parametric OpenCASCADE generator for Variant A and Variant B (`CARRIAGE_DY = -18.0` at top of file).
- `src/siboor_lineux/verify_2d.py`: 2D planar cross-section verification plotter (`BRepAlgoAPI_Section`).
