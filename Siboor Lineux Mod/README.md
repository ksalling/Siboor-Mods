# Siboor Lineux Mod — Siboor Voron Trident CNC Carriage Adaptation (Iteration 4: 100% Sealed Airflow Channel & Unpierced [a]_duct Arms)

This repository contains the parametric CAD modifications (`STEP` and `STL`) to mount the **Lineux Hotswap Toolchanger Carriage** (`LineuxCarriage.step` & `LineuxTool.step`) directly onto the stock **Siboor Voron Trident CNC Carriage** (`siboorCNC.step` on an `MGN12H` linear rail block), replacing the stock `carriage_base` part.

---

## Key Engineering Highlights (Iteration 4)

1. **100% Hermetically Sealed Airflow Path (Zero Leaks):**
   - In `carriage_base` (Variant A) and `carriage` (Variant B), **all clearance cuts for the MGN12H block screws, belt clamp screws, and inner plate holes have been completely removed**.
   - Because the MGN12H block and belt clamps are fastened to `siboorCNC` prior to carriage mounting, clearance cutouts through the front face are unnecessary.
   - The vertical airflow channel ($X \in [119.68, 133.72]$, $Y \in [147.30, 154.30]$, $Z \in [44.00, 90.12]$) is now enclosed by continuous, solid ABS walls ($>1.5\text{ mm}$ thick on all sides) with **zero holes or seams for air leakage**.

2. **Unpierced `[a]_duct` Cooling Arms (Full Airflow Volume & 100% Support-Free):**
   - **All through-sleeves and bolt holes have been removed from `[a]_duct`'s side cooling arms**.
   - Cooling arms are 100% continuous, hollow, smooth, and completely unpierced by any fasteners, ensuring zero resistance or restriction to part-cooling airflow.
   - Lower standoffs of `siboorCNC` ($X = 110.45, 142.95\text{ mm}$, $Z = 29.72\text{ mm}$, $Y = 155.00\text{ mm}$) have $+0.45\text{ mm}$ of clear air clearance to the rear face of `[a]_duct` ($Y = 154.55\text{ mm}$) with zero modifications needed.
   - Top face remains 100% flat at $Z = 52.82\text{ mm}$ for upside-down ABS printing with zero internal supports.

3. **Aligned Lower Mounting Screws ($X = 121.45, 131.95\text{ mm}$, $Z = 39.05\text{ mm}$):**
   - Stock Lineux `carriage` lower tongue holes have been moved from $X = 119.55, 133.85$ ($Z = 38.47$) to **$X = 121.45, 131.95\text{ mm}$ and $Z = 39.05\text{ mm}$** ($+1.90\text{ mm}$ inward per side, $+0.58\text{ mm}$ higher).
   - These holes line up **100% dead-on** with `siboorCNC`'s lower M3 tapped holes at $Y = 165.10\text{ mm}$!
   - `carriage` features front $\varnothing 6.2\text{ mm}$ counterbores (depth $4.0\text{ mm}$) to fully recess standard M3 Socket Head Cap Screw (SHCS) heads.
   - The screws pass through `carriage`, through `[a]_duct`'s lower mounting tab, through solid standoff bosses in `carriage_base` ($Y = 148.10 \dots 165.10\text{ mm}$), and thread directly into `siboorCNC`.

4. **Option A ($\Delta Z = +8.0\text{ mm}$) Flyover Architecture:**
   - Routes `duct_extension`'s fastener sleeves ($Z = 86.82 \dots 93.83\text{ mm}$, screw axis $Z = 89.57\text{ mm}$) **100% ABOVE `siboorCNC`'s top ears ($Z_{\text{max}} = 86.57\text{ mm}$)** with $+0.25\text{ mm}$ air clearance.
   - Completely eliminates fastener collisions with solid aluminum while preserving stock straight-through M3x45mm screws and full cylindrical sleeve walls.
   - Stepper motor body ($Z_{\text{min}} = 89.82\text{ mm}$) and micro switch ($Z_{\text{min}} = 80.13\text{ mm}$) clear completely above `siboorCNC`'s top ears.

5. **Stock $37.76\text{ mm}$ `5015_standoff_x2` Spacing ($18\text{ mm}$ Gap Behind Stepper):**
   - `5015_adapter`, `5015 Blower Fan`, and `pug_collar_front/rear` shift by the exact same $(\Delta Y, \Delta Z)$ as `carriage` and `Nema 14 Stepper`.
   - `5015_standoff_x2` remains 100% stock length ($37.76\text{ mm}$ = $20.00\text{ mm}$ stepper body + $17.76\text{ mm} \approx 18\text{ mm}$ gap to `5015_adapter`).
   - `duct_extension` stays at its compact stock $28.37\text{ mm}$ length with a $2.2\text{ mm}$ forward male sealing spigot.

6. **ABS 3D Printability (Zero Internal Supports):**
   - **`[a]_duct`**: Top face is **100% flat at $Z = 52.82\text{ mm}$**, printing **upside-down directly on the build plate in ABS with zero internal supports**.
   - **`carriage_base` (Variant A)**: Front face is **100% flat at $Y = 146.10\text{ mm}$**, printing **flat on its front face on the build plate with zero internal supports**.
   - **`carriage` (Variant A)**: Rear face is **100% flat at $Y = 146.10\text{ mm}$**, printing flat on its back just like stock Lineux.
   - **`duct_extension`**: Prints flat on its rear flange with zero internal supports.

7. **Direct Siboor CNC Cartographer Mount (`siboor_cartographer_mount`):**
   - Mounts Cartographer probe directly to `siboorCNC`'s bottom vertical M3 threaded holes at $Z = 14.52\text{ mm}$ ($X = 110.90, 142.50\text{ mm}$, $Y = 167.30\text{ mm}$).
   - Calibrated for shifted nozzle height ($Z = +7.12\text{ mm}$): probe bottom sits at $Z = 9.52\text{ mm}$ ($2.40\text{ mm}$ above the nozzle tip), providing optimal trigger distance and heatbed clearance.

---

## Fastener Bill of Materials (BOM) & Joint Mapping

| Fastener | Location | Connects | Features & Access |
| :--- | :--- | :--- | :--- |
| **2x M3x16mm SHCS** | $X = 111.20, 142.20$, $Z = 73.02$ | `carriage` + `carriage_base` $\to$ `siboorCNC` Upper Standoffs ($Y = 155.00$) | $\varnothing 6.2\text{ mm}$ front counterbores on `carriage`, straight-in hex driver access |
| **2x M3x25mm SHCS** | $X = 121.45, 131.95$, $Z = 39.05$ | `carriage` + `[a]_duct` + `carriage_base` $\to$ `siboorCNC` Lower Plate ($Y = 165.10$) | Front $\varnothing 6.2\text{ mm}$ counterbores on `carriage` tongue, threads into `siboorCNC` |
| **2x M3x45mm SHCS** | $X = 111.98, 141.42$, $Z = 89.57$ | `5015_adapter` $\to$ `duct_extension` $\to$ `carriage_base` $\to$ `carriage` | Flies above `siboorCNC` ($Z_{\text{max}} = 86.57$); threads into M3 heat-sets in `carriage` |
| **4x M3x8mm SHCS** | $X = 112.90, 140.50$ ($Z=84.57$), $X = 106.20, 147.20$ ($Z=57.32$) | `carriage` $\to$ `carriage_base` Front Face ($Y = 146.10$) | Front counterbores in `carriage`, M3 heat-set inserts in `carriage_base` |
| **2x M3x8mm BHCS** | $X = 106.30, 147.10$, $Z = 49.57$, $Y = 150.80$ | `[a]_duct` Upper Side Tabs $\to$ `carriage_base` | $\varnothing 3.4\text{ mm}$ clearance in side skirts, M3 heat-sets in `[a]_duct` |
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
