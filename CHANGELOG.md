# Release Notes

## [1.4.1] - 2026-01-07
### Fixed
- **Area Accuracy:** The script now physically moves the sample box corners to match the rounded dimensions (nearest 0.5m) exactly. This guarantees the area calculation matches the visual label (e.g., 100m × 50m = 5000m²).
- **Decimal Precision:** Tree diameters and averages in the log and display are now strictly limited to one decimal place (e.g., 12.1m instead of 12.14m).
- **Message Restoration:** The "ANALYSIS COMPLETE" summary dialog has been restored to its full original text.

## [1.4.0] - 2026-01-07
### Added
- **Survey Logging:** New option to export a detailed text file at the end of the process. 
  - Includes metadata (Date, OSM ID, Script Version).
  - Lists all tags applied to the OSM object.
  - **Appendix:** Contains raw coordinates for the sample box corners, start/end points of every calibration measurement, and coordinates for every tree counted.
- **Console Feedback:** Restored the live dimension readout (e.g., "Drawing Sample Box: 10.5m x 15.0m") in the JOSM status bar during the drawing phase.

### Changed
- **Rounding Logic:** - Sample Area dimensions now strictly round to the nearest **0.5 meters** (e.g., 10.0m, 10.5m) to reflect the approximate nature of the sampling box.
  - Tree calibration measurements remain precise to the decimal (e.g., 12.3m) for accurate density calculations.

## [1.3.3] - 2026-01-07
### Changed
- **Persistent Labels:** The sample area dimensions (e.g., "10.5m x 12.0m") now stay visible on the map after you finish drawing the box. They will only be deleted once you finish the next step (Calibration).
- **Half-Meter Rounding:** The sample area width and height now round to the nearest 0.5m.
- **Precision Maintenance:** Tree diameters remain rounded to the decimal point for accuracy.

## [1.3.2] - 2026-01-07
### Fixed
- **Visual Fix:** Added 'natural=tree' to counters and 'place=point' to labels to force JOSM to render the text/icons on standard map styles.

## [1.3.1] - 2026-01-07
### Fixed
- **BUGFIX:** Removed invalid API call 'fireSelectionChanged' that caused crash during drag.
- **Live Drage:** Box and Diameter lines update in real-time.

### Changed
- **HUD:** Live dimensions plotted directly on the map.

## [1.3.0] - 2026-01-07
### Changes
- **HUD (Head-Up Display):** Live dimensions plotted directly on the map.
- **Live Drag:** Box and Diameter lines update in real-time while dragging.
- **Visual Counting:** Number counters appear next to trees while counting.
- **Rounding:** Distances displayed rounded to 1 decimal place (0.1m).

## [1.2.6] - 2026-01-05
### Fixed
- **Status Line Crash:** Resolved an `AttributeError` when the script finished. JOSM's API does not allow reading text from the status bar via `getHelpText()`, so the script now unconditionally clears the status line without checking it first.

## [1.2.5] - 2026-01-05
### Fixed
- **Cancel Behavior:** In the Smart Suggestion prompt, clicking "Cancel" now correctly aborts the entire script without applying any tags. Previously, it behaved like "No," saving the statistics but not changing the primary tag.
- **Imagery Enforcement:** The script now checks if a background imagery layer is visible before starting. If no imagery is detected, it displays an error and exits to prevent blind surveys.

### Changed
- **UI Prompts:** Refined instruction text (capitalized actions like `CLICK+DRAG`) to better guide the user through the mouse interactions.

## [1.2.4] - 2026-01-05
### Fixed
- **Critical Trackpad Bug:** Fixed the "red line ghosting" issue where the selection tool remained active after drawing the sample box. This was caused by the dialog pop-up blocking the mouse release event. All dialogs in the event loop are now wrapped in `SwingUtilities.invokeLater` to ensure JOSM processes the input cleanly before showing messages.

## [1.2.3] - 2026-01-05
### Changed
- **Refined Smart Suggestions:** The script now respects "Silent Mapping" for specialized areas. Suggestions to switch between `scrub` and `wood` only trigger if those specific tags (or `landuse=forest`) are present. This prevents the script from incorrectly suggesting a tag change for surveys performed on `grassland`, `heath`, or `wetland`.
- **Improved Feedback:** The suggestion dialog now explicitly mentions the Density Class (e.g., "Open", "Dense") to educate the user on FAO terminology.

## [1.2.2] - 2026-01-04
### Fixed
- **Mouse Event Ghosting:** Resolved a rare but annoying bug where the cursor would remain stuck in "selection mode" (red line following cursor) after releasing the mouse button. Fixed by forcing a UI focus reset (`requestFocusInWindow`) and immediate state clearing in the `mouseReleased` event.

### Changed
- **Documentation:** Updated the internal HOW-TO guide to include the Esri World Imagery Wayback (Living Atlas) workflow for retrieving precise imagery capture dates.

## [1.2.1] - 2026-01-04
### Fixed
- **Source Layer Detection:** Replaced keyword-based filtering ("Imagery"/"Satellite") with a visibility-check logic. The script now correctly identifies Bing, Mapbox, and local WMS layers as the source.
- **Multipolygon Area Accuracy:** Refined the area calculation to ensure it consistently accounts for the total area of all outer members minus inner members.

### Added
- **Smart Tagging Logic:** Added prompts to suggest switching primary tags between `natural=scrub` and `natural=wood` based on the calculated canopy density (10% threshold).

### Changed
- **Documentation:** Updated README and internal documentation to clarify behavior regarding complex multipolygons with multiple independent outer rings.

## [1.2.0] - 2026-01-04
### Added
- **`est:source_area` tag:** Records the exact area used for the calculation to help future mappers identify geometry bias.
- **Graceful Exit:** Added logic to stop the script safely if the user clicks "Cancel" on the date prompt.

## [1.1.0] - 2026-01-04
### Changed
- **Renamed Project:** Changed from "Vegetation Analyzer" to **Tree Density Estimator** for better clarity and impact.
- **Improved Logic:** Enhanced the area calculation to support JOSM Multipolygon Relations (handles 'inner' and 'outer' members correctly).

### Added
- **Smart Tag Suggestions:** The tool now prompts the mapper to switch between `natural=wood` and `natural=scrub` if density thresholds are met.
- **Mean Inter-Tree Distance:** Added calculation for the average gap between plants.
- **FAO Standards:** Tagging thresholds for `wood:density` are now officially aligned with FAO Global Forest Resources Assessment classes.
- **Imagery Metadata:** Support for adding Esri Wayback capture dates to the `source` tag.

## [1.0.0] - 2026-01-03
### Added
- Initial official release by **EverydayMapper**.
- Statistical extrapolation logic for `canopy` and `wood:density`.
- Live diameter calibration tool.
- Average spacing calculation (`est:avg_spacing`).
- Support for Esri Wayback imagery date metadata.
- Precision sampler with Shift+Click counting.
