# Tree Density Estimator for JOSM

**Version:** 1.0.0 
**Author:** EverydayMapper  
**License:** MIT  

## Overview
The **Tree Density Estimator** is a JOSM script designed to bridge the gap between "Scrub" and "Wood" in OpenStreetMap. Instead of relying on binary choices or solid green fills, this tool allows mappers to provide nuanced data such as canopy percentage, stem counts, and wood density classes based on FAO Global Forest Resources Assessment standards.

It uses a **sampling and extrapolation** method: measure a small representative area, count the individuals, and let the script handle the complex math for the entire polygon.

---

## Technical Environment & Compatibility
The script has been rigorously tested to ensure cross-platform parity and stability.

* **Verified Operating Systems:** macOS (Sequoia 15.x / 26.2) and Windows 11 (Version 24H2).
* **JOSM Version:** v19277 or newer (supports both Official and Microsoft Store versions).
* **Host Runtime:** Java 21 (macOS Bundled) or Java 17+.
* **Scripting Engine:** Jython Standalone v2.7.4 (Unified version for both OS).
* **Zero-Config Ready:** The script utilizes JOSM's internal Java runtime; no system-wide Java PATH configuration is required.

---

## Key Features
* **Statistical Extrapolation:** Calculates total counts and canopy cover based on a sample area.
* **Imagery Guard:** Detects background layers and prevents "blind" surveys by requiring a visible imagery source to start.
* **Contextual Visualization:** Dynamically switches markers based on vegetation type (Trees use `natural=tree`, while Bushes/Heathland use `natural=shrub`).
* **Silent Suggestions:** Intelligent logic that only prompts for a primary tag change (e.g., `natural=scrub` to `natural=wood`) if the measured density conflicts with existing tags.
* **macOS & Trackpad Optimization:** Wrapped in `invokeLater` logic to ensure smooth UI interaction and prevent drawing glitches common with modern macOS versions.
* **Standardized Output:** Automatically applies `wood:density` classes and calculates the mean inter-tree distance using the formula: $d = \sqrt{\frac{1}{\text{density}}}$.

---

## Installation
1.  **Install the Scripting Plugin:** Go to JOSM Preferences > Plugins and search for "Scripting".
2.  **Configure Jython:** * Download the **Jython Standalone v2.7.4** JAR file.
    * In JOSM Preferences > Scripting > Script Engines, point the "JAR files" path to this file.
3.  **Add Script:** Save `tree_density_estimator.py` to your local scripts folder and execute it via the Scripting Console.

---

## How to Use

1.  **Select:** Highlight a **closed way** or a **multipolygon relation** (e.g., `natural=wood` or `natural=scrub`).
2.  **Setup:** Ensure background imagery is visible. When prompted, enter the **Imagery Date** (YYYY-MM-DD) and select the **Vegetation Type**.
3.  **Draw Sample Box:** **CLICK+DRAW** a sample box over a representative section. Dimensions snap to the nearest 0.5m for mathematical consistency.
4.  **Calibrate Diameter:** **CLICK+DRAG** the diameter of several tree crowns or bush widths to establish a high-accuracy average. Press **Enter**.
5.  **Count:** **SHIFT+CLICK** every tree/shrub strictly inside the box.
    * Use **Backspace/Delete** to undo a misclick.
    * Markers will automatically appear as trees or shrubs based on your initial selection.
6.  **Finalize:** Press **Enter**. Review the results and the **Smart Suggestion** prompt:
    * **Yes:** Apply density tags and update the primary tag (e.g., scrub → wood) based on canopy cover.
    * **No:** Apply density tags only.
    * **Cancel:** Exit without changes.
7.  **Log:** Choose **Yes** to export a `TreeSurvey_{ID}_{Time}.txt` file for your audit records.

---

## Tagging Applied
The tool applies the following metadata to the selected object:
* `canopy=*` (Percentage rounded to nearest 5%)
* `wood:density=*` (Scattered, Open, Dense, Very Dense)
* `est:stem_count=*` (Total estimated plants)
* `est:avg_crown` or `est:avg_shrub` (Mean diameter measured)
* `est:avg_spacing=*` (Mean Inter-Tree Distance)
* `est:source_area=*` (Total polygon area in $m^2$ used for calculation)
* `source=*` (Imagery name, date, and tool attribution)

---

## Vital Best Practices
1.  **The "Time Travel" Trap:** Satellite imagery can be outdated. Always verify the capture date (e.g., via Esri Wayback). If imagery is $>10$ years old, treat results with caution as they may not reflect ground reality.
2.  **Area Verification:** The script snaps sample box corners to 0.5m. Periodically compare the `est:source_area` tag against the value in the JOSM Measurement Plugin to ensure geometry hasn't drifted.
3.  **Accuracy Limits:** This tool is most effective where individual crowns are visible. Avoid using it for "closed-canopy" forests where individual tree counts become guesswork.

---

## Logging & Data Export
The generated survey log serves as a permanent record of your methodology and includes:
* **Survey Metadata:** Original tags ("Surveyed Type"), Imagery Source, and OSM ID.
* **Applied Tags:** The exact key/value pairs added to the map.
* **Raw Data Appendix:** * Exact GPS coordinates of the sample box corners.
    * Start and End coordinates for every diameter measurement.
    * Coordinates for every individual plant counted.

---
*Mapping with nuance. Join the effort to move beyond the green blob.*
