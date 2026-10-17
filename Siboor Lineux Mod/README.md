# Siboor Lineux Mod — Siboor Voron Trident CNC Carriage Adaptation (Iteration 3: Option A Flyover Architecture & Full Fastener Accounting)

This repository contains the parametric CAD modifications (`STEP` and `STL`) to mount the **Lineux Hotswap Toolchanger Carriage** (`LineuxCarriage.step` & `LineuxTool.step`) directly onto the stock **Siboor Voron Trident CNC Carriage** (`siboorCNC.step` on an `MGN12H` linear rail block), replacing the stock `carriage_base` part.

---

## Key Engineering Highlights (Iteration 3)

1. **Option A ($\Delta Z = +8.0\text{ mm}$) Flyover Architecture:**
   - Lifts the carriage assembly by $+8.0\text{ mm}$ relative to `siboorCNC`.
   - Routes `duct_extension`'s fastener sleeves ($Z = 86.82 \dots 93.83\text{ mm}$, screw axis $Z = 89.57\text{ mm}$) **100% ABOVE `siboorCNC`'s top ears ($Z_{\text{max}} = 86.57\text{ mm}$)** with $+0.25\text{ mm}$ bottom clearance and $+3.0\text{ mm}$ screw-center clearance.
   - **Completely eliminates fastener collisions** with solid aluminum of `siboorCNC` while preserving stock straight-through M3x45mm screws and full cylindrical sleeve walls.
   - Stepper motor body ($Z_{\text{min}} = 89.82\text{ mm}$) and micro switch ($Z_{\text{min}} = 80.13\text{ mm}$) clear completely above `siboorCNC`'s top ears and upper standoffs.
   - Hotend nozzle tip ($Z = +7.12\text{ mm}$) remains $7.40\text{ mm}$ below the bottom of `siboorCNC` ($Z = 14.52\text{ mm}$), ensuring generous bed and build-volume clearance.

2. **Full 4-Standoff Fastener Accounting & Solid Mechanical Clamping:**
   - **Upper Standoffs ($X = 111.20, 142.20\text{ mm}$, $Z = 73.02\text{ mm}$, $Y = 155.00\text{ mm}$):**
     - `carriage`: Front $\varnothing 6.2\text{ mm}$ counterbores with straight-in $2.5\text{ mm}$ hex-driver access and $\varnothing 3.4\text{ mm}$ clearance holes.
     - `carriage_base` (Variant A): $\varnothing 3.4\text{ mm}$ clearance through-holes to $Y = 155.00\text{ mm}$.
     - Clamped directly to `siboorCNC` with standard **M3x16mm SHCS** screws (or M3x20mm), clamping `carriage`, `carriage_base`, and `siboorCNC` into a rigid structure.
   - **Lower Standoffs ($X = 110.45, 142.95\text{ mm}$, $Z = 29.72\text{ mm}$, $Y = 155.00\text{ mm}$):**
     - `[a]_duct`: Features **hermetically sealed internal cylindrical through-sleeves** ($\varnothing 5.8\text{ mm}$ OD, $1.20\text{ mm}$ wall) passing across the left and right airflow arms to $Y = 155.00\text{ mm}$.
     - Front face has recessed $\varnothing 6.2\text{ mm}$ counterbores for screw heads with straight-in hex-driver access.
     - Clamped directly to `siboorCNC`'s lower standoffs with **M3x16mm SHCS** screws.
     - **100% sealed airflow path** — cooling air flows freely around the sealed sleeves with full original cross-sectional area and zero leakage.

3. **Stock $37.76\text{ mm}$ `5015_standoff_x2` Spacing ($18\text{ mm}$ Gap Behind Stepper):**
   - `5015_adapter`, `5015 Blower Fan`, and `pug_collar_front/rear` shift by the exact same $(\Delta Y, \Delta Z)$ as `carriage` and `Nema 14 Stepper`.
   - `5015_standoff_x2` remains 100% stock length ($37.76\text{ mm}$ = $20.00\text{ mm}$ stepper body + $17.76\text{ mm} \approx 18\text{ mm}$ gap to `5015_adapter`).
   - `duct_extension` stays at its compact stock $28.37\text{ mm}$ length with a $2.2\text{ mm}$ forward male sealing spigot.

4. **ABS 3D Printability (Zero Internal Supports):**
   - **`[a]_duct`**: Top face is **100% flat at $Z = 52.82\text{ mm}$** with no upward-protruding lips, allowing it to print **upside-down directly on the build plate in ABS with zero internal supports**.
   - **`carriage_base` (Variant A)**: Front face is **100% flat at $Y = 146.10\text{ mm}$**, printing **flat on its front face on the build plate with zero internal supports**.
   - **`carriage` (Variant A)**: Rear face is **100% flat at $Y = 146.10\text{ mm}$**, printing flat on its back just like stock Lineux.
   - **`duct_extension`**: Prints flat on its rear flange with zero internal supports.

5. **Direct Siboor CNC Cartographer Mount (`siboor_cartographer_mount`):**
   - Mounts Cartographer probe directly to `siboorCNC`'s bottom vertical M3 threaded holes at $Z = 14.52\text{ mm}$ ($X = 110.90, 142.50\text{ mm}$, $Y = 167.30\text{ mm}$).
   - Calibrated for shifted nozzle height ($Z = +7.12\text{ mm}$): probe bottom sits at $Z = 9.52\text{ mm}$ ($2.40\text{ mm}$ above the nozzle tip), providing optimal trigger distance and heatbed clearance.

---

## Fastener Bill of Materials (BOM) & Joint Mapping

| Fastener | Location | Connects | Features & Access |
| :--- | :--- | :--- | :--- |
| **2x M3x16mm SHCS** | $X = 111.20, 142.20$, $Z = 73.02$ | `carriage` + `carriage_base` $\to$ `siboorCNC` Upper Standoffs ($Y = 155.00$) | $\varnothing 6.2\text{ mm}$ front counterbores on `carriage`, straight-in hex driver access |
| **2x M3x16mm SHCS** | $X = 110.45, 142.95$, $Z = 29.72$ | `[a]_duct` $\to$ `siboorCNC` Lower Standoffs ($Y = 155.00$) | $\varnothing 6.2\text{ mm}$ front counterbores on `[a]_duct`, sealed $\varnothing 5.8\text{ mm}$ sleeves |
| **2x M3x45mm SHCS** | $X = 111.98, 141.42$, $Z = 89.57$ | `5015_adapter` $\to$ `duct_extension` $\to$ `carriage_base` $\to$ `carriage` | Flies above `siboorCNC` ($Z_{\text{max}} = 86.57$); threads into M3 heat-sets in `carriage` |
| **4x M3x8mm SHCS** | $X = 112.90, 140.50$ ($Z=84.57$), $X = 106.20, 147.20$ ($Z=57.32$) | `carriage` $\to$ `carriage_base` Front Face ($Y = 146.10$) | Front counterbores in `carriage`, M3 heat-set inserts in `carriage_base` |
| **4x M3x8mm SHCS** | $X = 118.70, 134.70$, $Z = 65.82, 50.82$ | `carriage_base` $\to$ `siboorCNC` Inner Plate ($Y = 165.10$) | $\varnothing 6.2\text{ mm}$ counterbores in `carriage_base`, driver access through `carriage` |
| **2x M3x8mm SHCS** | $X = 108.75, 144.65$, $Z = 43.27$ | `carriage_base` $\to$ `siboorCNC` Lower Outer Plate ($Y = 165.10$) | $\varnothing 6.2\text{ mm}$ counterbores in `carriage_base` lower ribs |
| **2x M3x8mm BHCS** | $X = 106.30, 147.10$, $Z = 49.57$, $Y = 150.80$ | `[a]_duct` Upper Side Tabs $\to$ `carriage_base` | $\varnothing 3.4\text{ mm}$ clearance in side skirts, M3 heat-sets in `[a]_duct` |
| **2x M3x8mm BHCS** | $X = 119.55, 133.85$, $Z = 38.47$, $Y = 143.00$ | `led_mount` + `[a]_duct` Lower Tabs $\to$ `carriage` | Standard Lineux LED mount clamp into `carriage` lower tongue |
| **2x M3x10mm SHCS** | $X = 110.90, 142.50$, $Y = 167.30$, vertical | `siboor_cartographer_mount` $\to$ `siboorCNC` Bottom Legs ($Z = 14.52$) | Bottom $\varnothing 6.2\text{ mm}$ counterbores on mount |

---

## Recommended ABS Print Orientations

| Part | Flat Build-Plate Face | Internal Supports inside Air Channel? | Notes |
| :--- | :--- | :---: | :--- |
| **`[a]_duct`** | **Top Face ($Z = 52.82\text{ mm}$)** (Print upside-down) | **None** | No upward lips. Cooling arms angle upward at $\sim 45^\circ$. |
| **`carriage_base`** (Variant A) | **Front Face ($Y = 146.10\text{ mm}$)** | **None** | Vertical airflow channel prints as open side walls. |
| **`carriage`** (Variant A) | **Rear Face ($Y = 146.10\text{ mm}$)** | **N/A** | Identical flat-back print orientation to stock Lineux `carriage`. |
| **`carriage`** (Variant B) | **Top / Rear Face** | **None** | Vertical channel is open at top and bottom. |
| **`duct_extension`** | **Rear Flange** | **None** | Stock $28.37\text{ mm}$ length with forward male sealing spigot. |
| **`siboor_cartographer_mount`** | **Top Face ($Z = 14.52\text{ mm}$)** | **N/A** | Simple bracket with counterbored vertical M3 holes. |

---

## Directory Structure

```text
Siboor Lineux Mod/
├── README.md
├── docs/
│   ├── siboor_lineux_variants_ab_centerline_2d.png
│   └── siboor_lineux_variants_ab_xy_slices_2d.png
├── Variant_A_Separate_Carriage_Base_14mm/
│   ├── CAD/
│   │   ├── carriage_base.step
│   │   ├── carriage.step
│   │   ├── [a]_duct.step
│   │   ├── duct_extension.step
│   │   ├── siboor_cartographer_mount.step
│   │   ├── Siboor_Lineux_Carriage_Assembly.step
│   │   └── Siboor_Lineux_Carriage_With_Tool_Assembly.step
│   └── STL/
│       ├── carriage_base.stl
│       ├── carriage.stl
│       ├── [a]_duct.stl
│       ├── duct_extension.stl
│       └── siboor_cartographer_mount.stl
└── Variant_B_Integrated_Carriage_UltraCompact_8.5mm/
    ├── CAD/
    │   ├── carriage.step
    │   ├── [a]_duct.step
    │   ├── duct_extension.step
    │   ├── siboor_cartographer_mount.step
    │   ├── Siboor_Lineux_Carriage_Assembly.step
    │   └── Siboor_Lineux_Carriage_With_Tool_Assembly.step
    └── STL/
        ├── carriage.stl
        ├── [a]_duct.stl
        ├── duct_extension.stl
        └── siboor_cartographer_mount.stl
```
