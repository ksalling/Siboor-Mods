# Siboor Lineux Mod — Siboor Voron Trident CNC Carriage Adaptation (Iteration 2: ABS Printable & Reduced Depth)

This repository contains the parametric CAD modifications (`STEP` and `STL`) to mount the **Lineux Hotswap Toolchanger Carriage** (`LineuxCarriage.step` & `LineuxTool.step`) directly onto the stock **Siboor Voron Trident CNC Carriage** (`siboorCNC.step` on an `MGN12H` linear rail block), replacing the stock `carriage_base` part.

---

## Key Engineering Highlights (Iteration 2)

1. **Zero Modifications to `siboorCNC.step`:**
   - The machined aluminum Siboor CNC carriage is untouched and uses only its existing M3 threaded/clearance holes.
2. **Stock $37.76\text{ mm}$ `5015_standoff_x2` Spacing ($18\text{ mm}$ Stepper-to-Adapter Gap):**
   - `5015_adapter`, `5015 Blower Fan`, and `pug_collar_front/rear` shift forward by the same $(\Delta Y, \Delta Z)$ as `carriage` and `Nema 14 Stepper`, keeping `5015_standoff_x2` 100% stock length ($37.76\text{ mm}$ = $20.00\text{ mm}$ stepper body + $17.76\text{ mm} \approx 18\text{ mm}$ gap to `5015_adapter`) and keeping `duct_extension` at its compact stock $28.37\text{ mm}$ length.
3. **100% ABS 3D Printable (Flat Build-Plate Faces & Zero Internal Duct Supports):**
   - **`[a]_duct`**: Keeps its **100% flat top face ($Z = 47.32\text{ mm}$)** with no upward-sticking lips so it prints **upside-down on the build plate in ABS with zero internal supports**.
   - **`carriage_base` (Variant A)**: Has a **100% flat front face ($Y = 146.10\text{ mm}$)** so it prints **flat on its front face on the build plate in ABS with zero supports**, and features a downward male sealing spigot that telescopes inside `[a]_duct`'s top throat.
   - **`carriage` (Variant A)**: Retains its **100% flat rear face ($Y = 146.10\text{ mm}$)** so it prints flat on its back on the build plate just like stock Lineux.
4. **Reduced Forward Depth ($\Delta Z = +2.5\text{ mm}$ Stepper Clearance Lift):**
   - Lifting the Lineux mounting pattern by $+2.5\text{ mm}$ relative to `siboorCNC` allows the round $\varnothing 36\text{ mm}$ `Nema 14 Stepper` to clear `siboorCNC`'s upper-left ear in the $(X, Z)$ plane, reducing forward depth by **$4.0\text{ mm}$ (Variant A: $\Delta Y = -14.0\text{ mm}$)** to **$9.5\text{ mm}$ (Variant B: $\Delta Y = -8.5\text{ mm}$)** compared to v1 ($\Delta Y = -18.0\text{ mm}$).
5. **Two Complete Comparison Variants Included:**
   - **`Variant_A_Separate_Carriage_Base_14mm` ($\Delta Y = -14.0\text{ mm}, \Delta Z = +2.5\text{ mm}$):**
     - Uses a dedicated ABS-printable `carriage_base` (flat front build-plate face) paired with a flat-backed `carriage` and uncontoured flat-top `[a]_duct`.
   - **`Variant_B_Integrated_Carriage_UltraCompact_8.5mm` ($\Delta Y = -8.5\text{ mm}, \Delta Z = +2.5\text{ mm}$):**
     - Tucks the $7.0\text{ mm}$-deep vertical airflow channel inside `siboorCNC`'s central front pocket ($Y = 155.00 \dots 165.10\text{ mm}$), integrates the manifold into `carriage`, and contours `[a]_duct`'s lower arms around `siboorCNC`'s lower standoffs ($Y = 155.00\text{ mm}$) with a sealed forward internal air bypass.

---

## Recommended ABS Print Orientations

| Part | Flat Build-Plate Face | Internal Supports inside Air Channel? | Notes |
| :--- | :--- | :---: | :--- |
| **`[a]_duct`** (Both Variants) | **Top Face ($Z = 47.32\text{ mm}$)** (Print upside-down) | **None** | Curved cooling arms angle upward at $\sim 45^\circ$ from the flat top face. |
| **`carriage_base`** (Variant A) | **Front Face ($Y = 146.10\text{ mm}$)** | **None** | Straight-through vertical channel prints as open side walls. |
| **`carriage`** (Variant A) | **Rear Face ($Y = 146.10\text{ mm}$)** | **N/A** | Identical flat-back print orientation to stock Lineux `carriage`. |
| **`carriage`** (Variant B) | **Top / Rear Face** | **None** | Straight-through vertical channel is open at top and bottom. |
| **`duct_extension`** (Both Variants) | **Rear Flange ($Y_{max}$)** or **Top Face** | **None** | Compact stock $28.37\text{ mm}$ length with forward sealing spigot. |
| **`siboor_cartographer_mount`** | **Top Pillars ($Z = 14.52\text{ mm}$)** or **Bottom Face** | **N/A** | Simple U-bracket with counterbored M3 holes. |

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
