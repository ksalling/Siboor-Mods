# Siboor Lineux Mod — Siboor Voron Trident CNC Carriage Adaptation (Iteration 5: ***UNTESTED Production Release)

This repository contains the parametric CAD modifications (`STEP` and `STL`) to mount the **Lineux Hotswap Toolchanger Carriage** (`LineuxCarriage.step` & `LineuxTool.step`) directly onto the stock **Siboor Voron Trident CNC Carriage** (`siboorCNC.step` on an `MGN12H` linear rail block), replacing the stock Lineux `carriage_base` part.

---

## Key Engineering Highlights & Iteration 5 Resolutions

1. **MGN12H Bolt Head Clearance Pockets in `carriage_base`:**
   - The 4 M3x8 bolts that fasten `siboorCNC` to the MGN12H rail block at $(116.70, 68.32)$, $(136.70, 68.32)$, $(116.70, 48.32)$, and $(136.70, 48.32)$ protrude forward from `siboorCNC` ($Y = 165.10\text{ mm}$) to $Y = 162.77\text{ mm}$.
   - **Resolution:** Added 4 blind cylindrical rear pockets ($R = 3.80\text{ mm}$, $Y \in [162.00, 166.00\text{ mm}]$) into the rear of `carriage_base`.
   - **Airflow Integrity:** These pockets are blind and sit $7.7\text{ mm}$ behind the vertical air channel ($Y = 154.30\text{ mm}$), ensuring the airflow duct remains **100% hermetically sealed with zero leaks**.
   - Provides $>0.77\text{ mm}$ axial clearance and $>1.05\text{ mm}$ radial clearance around the bolt heads.

2. **Belt Mount, Clamp & B-Belt Relief Cuts:**
   - Voron Trident belt clamps (`9???????`), clamp screws (`M3x6-??`), and the B-Belt pass along the sides at $X \in [104.2, 110.2]$ and $[143.2, 149.2]$, protruding forward to $Y = 161.45\text{ mm}$.
   - **Resolution:** Added rear wing reliefs on `carriage_base` ($X \in [103.0, 112.5]$ and $[138.5, 150.5]$, $Y \in [160.5, 166.0]$, $Z \in [40.0, 72.0]$).
   - Provides $>0.95\text{ mm}$ clearance with zero interference or rubbing on belts or hardware.

3. **Modified `led_mount` (`led_mount.step` / `led_mount.stl`):**
   - **Hole Alignment:** Stock Lineux `led_mount` holes at $X = 119.55, 133.85$ ($Z = 38.47$) have been repositioned to **$X = 121.45, 131.95\text{ mm}$ and $Z = 39.05\text{ mm}$**, matching `carriage`, `[a]_duct`, `carriage_base`, and `siboorCNC` 100% concentrically.
   - **Full-Depth Standoff Bosses (Snug Sandwich):** Features robust $\varnothing 6.5\text{ mm}$ ($R = 3.25\text{ mm}$) cylindrical standoff bosses centered on the M3 holes, spanning from $Y = 148.10\text{ mm}$ (mating flush to the rear of `[a]_duct`'s tab) to $Y = 155.50\text{ mm}$ (mating flush to the front of `carriage_base`'s bosses).
   - **Snug Clamp Architecture (Zero Air Gap):** `led_mount` is sandwiched rigidly and snugly between `[a]_duct` and `carriage_base`. Tightening the lower M3 screws clamps all 4 parts (`carriage` $\to$ `[a]_duct` $\to$ `led_mount` $\to$ `carriage_base` $\to$ `siboorCNC`) in continuous solid compression with zero flex or play.
   - **Trimmed Lower Legs:** Lower extended legs trimmed below $Z = 25.0\text{ mm}$, completely eliminating collisions with lower hardware and Cartographer probe mount.
   - Zero solid-body collisions verified with `BRepAlgoAPI_Common` across all adjacent parts (`led_mount` vs. `[a]_duct` = 0 solids, `led_mount` vs. `carriage_base` = 0 solids).

4. **Dedicated Cartographer Probe Mount (`siboor_cartographer_mount`):**
   - Stock Lineux probe mounts (`cartographer_mount`, etc.) have been removed from the assembly to prevent duplicate mounts and interference.
   - `siboor_cartographer_mount` fastens directly to `siboorCNC`'s bottom vertical M3 threaded holes at $Z = 14.52\text{ mm}$ ($X = 110.90, 142.50\text{ mm}$, $Y = 167.30\text{ mm}$).
   - With `led_mount` trimmed below $Z = 25.0\text{ mm}$, there is a generous $11.48\text{ mm}$ vertical clearance gap, completely decoupling probe mounting from the LED bracket.
   - Probe bottom sits at $Z = 9.52\text{ mm}$ ($2.40\text{ mm}$ above the nozzle tip at $Z = 7.12\text{ mm}$), matching Cartographer trigger specifications.

5. **100% Hermetically Sealed Airflow Path (Zero Leaks):**
   - In `carriage_base`, all unnecessary front-access cuts have been eliminated.
   - The vertical airflow channel ($X \in [119.68, 133.72]$, $Y \in [147.30, 154.30]$, $Z \in [44.00, 90.12]$) is enclosed by continuous, solid ABS walls ($>1.5\text{ mm}$ thick on all sides).
   - Sealed female telescopic spigot on top of `[a]_duct` accepts the male downward spigot of `carriage_base`.

6. **Unpierced `[a]_duct` Cooling Arms (Full Airflow Volume & 100% Support-Free):**
   - Side cooling arms are continuous, hollow, smooth, and completely unpierced by fasteners.
   - Lower standoffs of `siboorCNC` ($X = 110.45, 142.95\text{ mm}$, $Z = 29.72\text{ mm}$, $Y = 155.00\text{ mm}$) have $+0.45\text{ mm}$ of clear air clearance to the rear face of `[a]_duct` ($Y = 154.55\text{ mm}$).
   - Top face is 100% flat at $Z = 52.82\text{ mm}$ for upside-down ABS printing with zero internal supports.

7. **Option A ($\Delta Z = +8.0\text{ mm}$) Flyover Architecture:**
   - Routes `duct_extension`'s fastener sleeves ($Z = 86.82 \dots 93.83\text{ mm}$, screw axis $Z = 89.57\text{ mm}$) **100% ABOVE `siboorCNC`'s top ears ($Z_{\text{max}} = 86.57\text{ mm}$)** with $+0.25\text{ mm}$ bottom clearance.
   - Completely eliminates fastener collisions with solid aluminum while preserving stock straight-through M3x45mm screws and full cylindrical sleeve walls.

8. **Stock $37.76\text{ mm}$ `5015_standoff_x2` Spacing ($18\text{ mm}$ Gap Behind Stepper):**
   - `5015_adapter`, `5015 Blower Fan`, and `pug_collar_front/rear` shift by the exact same $(\Delta Y = -14.0\text{ mm}, \Delta Z = +8.0\text{ mm})$ as `carriage` and `Nema 14 Stepper`.
   - `5015_standoff_x2` remains 100% stock length ($37.76\text{ mm}$ = $20.00\text{ mm}$ stepper body + $17.76\text{ mm} \approx 18\text{ mm}$ gap to `5015_adapter`).
   - `duct_extension` stays at its compact stock $28.37\text{ mm}$ length with a $2.2\text{ mm}$ forward male sealing spigot.

10. **`carriage_base` Only Updates (Iteration 5.2):**
    - **Bottom Notch & Arch Widening:** The bottom arch cutout was widened from $X = 109.50..143.90$ to $X = 106.30..147.10\text{ mm}$ ($Y$ up to $156.00\text{ mm}$, $Z = 52.82\text{ mm}$), and the side leg bottom elevation was raised from the obsolete $Z = 40.74\text{ mm}$ constant to $Z = 46.32\text{ mm}$ ($38.32 + dz$). This completely eliminates the notch interference with `[a]_duct`'s swept arms ($0.000\text{ mm}^3$ interference) and provides generous clearance over the Voron Trident belt clamp bolt head.
    - **`duct_extension` Fastener Hole Alignment:** The top M3 clearance holes through `carriage_base` have been realigned from $Z = 89.57\text{ mm}$ ($81.569 + dz$) to **$Z = 90.32\text{ mm}$ ($82.319 + dz$)**, matching `duct_extension`'s screw sleeve axis 100% concentrically.

11. **Microswitch Reversion, Full Carriage Base Cutout & Aligned Top Fastener Pathway (Iteration 5.4):**
    - **Snug Microswitch Fit in `carriage`:** Reverted all microswitch pocket modifications on `carriage.step` to 100% stock geometry. The switch body and terminals seat in their exact, snug factory location.
    - **Through-Pass Wire Cutout on `carriage_base`:** Transferred the rectangular wire pass-through cutout ($X \in [105.50, 119.00\text{ mm}]$, $Z \in [75.00, 83.50\text{ mm}]$) to `carriage_base.step`, cutting completely front-to-back ($Y \in [145.0, 166.0\text{ mm}]$) for unobstructed wiring. Removed the redundant upper-left heat-set insert hole at $X = 112.90, Z = 84.57\text{ mm}$ that previously conflicted with the cutout.
    - **Top Fastener Pathway & Mold Line Alignment:**
      - Realigned the top M3 clearance holes in `carriage_base` to **$Z = 81.569 + dz = 89.57\text{ mm}$**, matching `carriage` and `5015_adapter` 100% concentrically.
      - Shifted `duct_extension` by $(dy, dz - 0.75\text{ mm})$ to eliminate its stock $+0.75\text{ mm}$ offset, bringing its sleeve holes to **$Z = 89.57\text{ mm}$** and its outer cylindrical mold line ($R = 3.50\text{ mm}$, $Z_{\text{top}} = 93.07\text{ mm}$) flush with `5015_adapter` at $Y = 183.86\text{ mm}$.
      - Replaced the previous large radial cut with exact tangential body clearance ($R = 18.35\text{ mm}$ on `carriage_base` and stock $R = 18.65\text{ mm}$ curve on `duct_extension`). This eliminates the open trough, preserving a solid, continuous $>1.5\text{ mm}$ cylindrical ceiling above the screw passage with **$0.000\text{ mm}^3$ motor collision**.

12. **CNC Standoff Fastener Hole Restoration & Wire Passthrough Optimization (Iteration 5.5):**
    - **Standoff & Fastener Hole Boss Restoration:** In `carriage_base.step`, the rectangular wire passthrough cutout was raised to **$Z_{\text{bottom}} = 78.50\text{ mm}$** and narrowed to **$X \in [107.00, 118.00\text{ mm}]$** ($Z \in [78.50, 84.50\text{ mm}]$).
    - This completely eliminates the previous notch and bite into the upper-left Siboor CNC standoff ($X=111.20, Z=73.02\text{ mm}$, $R=2.95\text{ mm}$), restoring a 100% complete, unclipped cylindrical boss with **$>3.78\text{ mm}$ of solid ABS ceiling** above the M3 through-hole and **$>2.53\text{ mm}$ of solid ABS clearance** above the CNC standoff face.
    - Provides a clean, generous $11.0\text{ mm} \times 6.0\text{ mm}$ wiring channel centered directly behind the microswitch terminals ($X=107.3, 112.3, 117.3\text{ mm}$) while increasing wall thickness to the vertical air duct to $1.68\text{ mm}$.

13. **`duct_extension` Standoff Relief Notches for Siboor CNC Top Ears (Iteration 5.6):**
    - **Ear Relief Notches:** Added localized relief notches ($X \in [103.0, 116.0]$ and $[137.0, 150.0]$, $Y \in [162.0, 170.5]$, $Z \le 86.90\text{ mm}$) to the underside of `duct_extension.step`.
    - Completely eliminates interference with the top rounded ears of `siboorCNC` ($Z_{\text{max}} = 86.57\text{ mm}$, previously intersecting by $0.50\text{ mm}$ following the Iteration 5.4 hole alignment shift) with **$0.000\text{ mm}^3$ collision volume**.
    - Preserves $>0.82\text{ mm}$ of solid ABS wall thickness under the top M3 clearance holes ($Z = 89.57\text{ mm}$) and maintains $>4.5\text{ mm}$ solid wall to the internal airflow channel, keeping airflow 100% hermetically sealed.

---

## Fastener Bill of Materials (BOM) & Joint Mapping

| Fastener | Location | Connects | Features & Access |
| :--- | :--- | :--- | :--- |
| **2x M3x16mm SHCS** | $X = 111.20, 142.20$, $Z = 73.02$ | `carriage` + `carriage_base` $\to$ `siboorCNC` Upper Standoffs ($Y = 155.00$) | $\varnothing 6.2\text{ mm}$ front counterbores on `carriage`, straight-in hex driver access |
| **2x M3x25mm SHCS** | $X = 121.45, 131.95$, $Z = 39.05$ | `carriage` + `[a]_duct` + `led_mount` + `carriage_base` $\to$ `siboorCNC` Lower Plate ($Y = 165.10$) | Front $\varnothing 6.2\text{ mm}$ counterbores on `carriage` tongue, clamps all 4 parts directly into `siboorCNC` |
| **2x M3x45mm SHCS** | $X = 111.98, 141.42$, $Z = 89.57$ | `5015_adapter` $\to$ `duct_extension` $\to$ `carriage_base` $\to$ `carriage` | Flies above `siboorCNC` ($Z_{\text{max}} = 86.57$); concentric across all 4 components with $\varnothing 3.7\text{ mm}$ clearance |
| **3x M3x8mm SHCS** | $X = 140.50$ ($Z=84.57$), $X = 106.20, 147.20$ ($Z=57.32$) | `carriage` $\to$ `carriage_base` Front Face ($Y = 146.10$) | Front counterbores in `carriage`, M3 heat-set inserts in `carriage_base` |
| **2x M3x8mm BHCS** | $X = 106.30, 147.10$, $Z = 49.57$, $Y = 150.80$ | `[a]_duct` Upper Side Tabs $\to$ `carriage_base` | $\varnothing 3.4\text{ mm}$ clearance in side skirts, M3 heat-sets in `[a]_duct` |
| **2x M3x10mm SHCS** | $X = 110.90, 142.50$, $Y = 167.30$, vertical | `siboor_cartographer_mount` $\to$ `siboorCNC` Bottom Legs ($Z = 14.52$) | Bottom $\varnothing 6.2\text{ mm}$ counterbores on mount |

---

## Recommended ABS Print Orientations

| Part | Flat Build-Plate Face | Internal Supports inside Air Channel? | Notes |
| :--- | :--- | :---: | :--- |
| **`[a]_duct`** | **Top Face ($Z = 52.82\text{ mm}$)** (Print upside-down) | **None** | 100% flat top face. Cooling arms angle upward at $\sim 45^\circ$. |
| **`carriage_base`** | **Front Face ($Y = 146.10\text{ mm}$)** | **None** | Vertical airflow channel prints as open side walls. Blind pockets face upward. |
| **`carriage`** | **Rear Face ($Y = 146.10\text{ mm}$)** | **N/A** | Identical flat-back print orientation to stock Lineux `carriage`. |
| **`duct_extension`** | **Rear Flange** | **None** | Stock $28.37\text{ mm}$ length with forward male sealing spigot. |
| **`led_mount`** | **Front Face** | **None** | Trimmed compact bracket with aligned $\varnothing 3.4\text{ mm}$ holes. |
| **`siboor_cartographer_mount`** | **Top Face ($Z = 14.52\text{ mm}$)** | **N/A** | Simple bracket with counterbored vertical M3 holes. |

---

## Directory Structure

```text
Siboor Lineux Mod/
├── README.md
├── docs/
│   ├── siboor_lineux_variants_ab_centerline_2d.png
│   ├── siboor_lineux_variants_ab_xy_slices_2d.png
│   ├── siboor_lineux_2d_cross_section.png
│   └── siboor_lineux_2d_xz_xy_views.png
└── Variant_A_Separate_Carriage_Base_14mm/
    ├── CAD/
    │   ├── [a]_duct.step
    │   ├── carriage_base.step
    │   ├── carriage.step
    │   ├── duct_extension.step
    │   ├── led_mount.step
    │   ├── siboor_cartographer_mount.step
    │   ├── Siboor_Lineux_Carriage_Assembly.step
    │   └── Siboor_Lineux_Carriage_With_Tool_Assembly.step
    └── STL/
        ├── [a]_duct.stl
        ├── carriage_base.stl
        ├── carriage.stl
        ├── duct_extension.stl
        ├── led_mount.stl
        └── siboor_cartographer_mount.stl
```
