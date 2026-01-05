# ==============================================================================
# Tree Density Estimator
# Version: 1.2.6
# Date: 2026-01-05
# Author: EverydayMapper (OSM)
# License: MIT
# 
# NEW IN V1.2.6:
# - CRITICAL FIX: Removed the invalid 'getHelpText()' call that caused a crash
#   when exiting or finishing the script. The status line is now cleared 
#   unconditionally.
# - RETAINED: All logic for Smart Suggestions, Cancel-to-Abort, and Imagery checks.
# ==============================================================================

import math
from threading import Thread
from org.openstreetmap.josm.gui import MainApplication
from org.openstreetmap.josm.data.osm import Node, Way
from org.openstreetmap.josm.tools import Geometry
from org.openstreetmap.josm.data.coor import LatLon
from org.openstreetmap.josm.gui.layer import OsmDataLayer
from java.awt.event import MouseListener, KeyListener
from java.awt.geom import Path2D 
from javax.swing import JOptionPane, SwingUtilities

def run_analyzer():
    # 1. Start with Disclaimer
    disclaimer = ("PRECISION & SOURCE NOTICE:\n"
                  "- Best for 'Open' or 'Scattered' vegetation.\n"
                  "- SHIFT+CLICK to count (prevents accidental selection).\n"
                  "- Please verify imagery dates for accuracy!")
    JOptionPane.showMessageDialog(None, disclaimer, "Tool Disclaimer", JOptionPane.WARNING_MESSAGE)

    layer = MainApplication.getLayerManager().getEditLayer()
    if not layer or not layer.data: return
    selection = layer.data.getSelected()
    if selection.isEmpty():
        JOptionPane.showMessageDialog(None, "Select the main area polygon first.")
        return
    
    target = selection.iterator().next()
    try:
        total_area = abs(Geometry.computeArea(target))
    except:
        JOptionPane.showMessageDialog(None, "Invalid area geometry.")
        return

    # 2. Metadata & Imagery Source Check
    active_layer_name = None
    for l in MainApplication.getLayerManager().getLayers():
        if isinstance(l, OsmDataLayer): continue
        if l.isVisible():
            active_layer_name = l.getName()
            
    # Enforce Imagery Presence
    if not active_layer_name:
        JOptionPane.showMessageDialog(None, 
            "No active imagery layer found.\n\nPlease enable a background imagery layer (e.g., Bing, Esri)\nto conduct the survey.",
            "Imagery Missing", JOptionPane.ERROR_MESSAGE)
        return

    date_prompt_msg = ("Date of Imagery (Optional)\n\n"
                       "Enter the capture date (YYYY-MM-DD) if known.\n"
                       "Leave blank if unknown.\n\n"
                       "Click OK to continue or Cancel to exit script.")
    
    img_date = JOptionPane.showInputDialog(None, date_prompt_msg, 
                                           "Imagery Metadata", JOptionPane.QUESTION_MESSAGE)
    
    if img_date is None: return
    
    if img_date and img_date.strip():
        imagery_source = "{} ({}); tree_density_estimator".format(active_layer_name, img_date.strip())
    else:
        imagery_source = "{}; tree_density_estimator".format(active_layer_name)

    options = ["Trees", "Bushes", "Heathland Plants"]
    choice = JOptionPane.showOptionDialog(None, "What are you counting?", "Vegetation Type",
                                          JOptionPane.DEFAULT_OPTION, JOptionPane.QUESTION_MESSAGE,
                                          None, options, options[0])
    if choice == -1: return
    singular, plural, tag_suffix = ("Tree", "Trees", "crown") if choice == 0 else ("Bush", "Bushes", "shrub") if choice == 1 else ("Plant", "Plants", "shrub")

    class PrecisionSampler(MouseListener, KeyListener):
        def __init__(self):
            self.step = "DRAW_BOX"
            self.start_p = None
            self.sample_way = None
            self.sample_poly = None
            self.diameters = []
            self.temp_lines = [] 
            self.tree_nodes = []
            self.finished = False
            self.sample_area_sqm = 0
            self.avg_diameter = 0

        def update_status(self, message):
            area_info = "| Area: {:.1f}m2 ".format(self.sample_area_sqm) if self.sample_area_sqm > 0 else ""
            MainApplication.getMap().statusLine.setHelpText("[Analyzer] " + area_info + "| " + message)

        def mousePressed(self, e):
            mv = MainApplication.getMap().mapView
            if not e.isShiftDown(): self.start_p = mv.getLatLon(e.getX(), e.getY())

        def mouseReleased(self, e):
            mv = MainApplication.getMap().mapView
            if not self.start_p: return
            end_p = mv.getLatLon(e.getX(), e.getY())
            
            p1 = self.start_p
            self.start_p = None
            
            # Use 'invokeLater' to let JOSM finish the mouse event before blocking with a dialog
            def process_release():
                mv.requestFocusInWindow()
                
                if self.step == "DRAW_BOX":
                    dist = p1.greatCircleDistance(end_p)
                    if dist < 1.0: return 
                    n1 = Node(p1); n2 = Node(LatLon(p1.lat(), end_p.lon()))
                    n3 = Node(end_p); n4 = Node(LatLon(end_p.lat(), p1.lon()))
                    self.sample_way = Way()
                    self.sample_way.setNodes([n1, n2, n3, n4, n1])
                    layer.data.addPrimitive(n1); layer.data.addPrimitive(n2); layer.data.addPrimitive(n3); layer.data.addPrimitive(n4); layer.data.addPrimitive(self.sample_way)
                    self.sample_area_sqm = abs(Geometry.computeArea(self.sample_way))
                    poly = Path2D.Double()
                    poly.moveTo(n1.coor.lat(), n1.coor.lon()); poly.lineTo(n2.coor.lat(), n2.coor.lon()); poly.lineTo(n3.coor.lat(), n3.coor.lon()); poly.lineTo(n4.coor.lat(), n4.coor.lon()); poly.closePath()
                    self.sample_poly = poly
                    
                    msg = ("Sample Area: {:.1f} m2\n\n"
                           "CALIBRATION STEP:\n"
                           "CLICK+DRAG your mouse from one side of a {} to the other to measure its diameter.\n"
                           "Measure 3-5 different ones for a better average, then press ENTER.").format(self.sample_area_sqm, singular)
                    
                    JOptionPane.showMessageDialog(None, msg)
                    self.step = "CALIBRATE"
                    self.update_status("CLICK+DRAG across a {} crown, then ENTER.".format(singular))

                elif self.step == "CALIBRATE":
                    dist = p1.greatCircleDistance(end_p)
                    if dist > 0.05:
                        self.diameters.append(dist)
                        self.avg_diameter = sum(self.diameters) / len(self.diameters)
                        self.update_status("Last: {:.2f}m | Avg: {:.2f}m (n={}) | ENTER".format(dist, self.avg_diameter, len(self.diameters)))
                        l1 = Node(p1); l2 = Node(end_p); line = Way(); line.setNodes([l1, l2])
                        layer.data.addPrimitive(l1); layer.data.addPrimitive(l2); layer.data.addPrimitive(line)
                        self.temp_lines.append((line, l1, l2))

            SwingUtilities.invokeLater(process_release)

        def mouseClicked(self, e):
            if self.step == "COUNTING" and e.isShiftDown():
                mv = MainApplication.getMap().mapView
                click_ll = mv.getLatLon(e.getX(), e.getY())
                if self.sample_poly and self.sample_poly.contains(click_ll.lat(), click_ll.lon()):
                    node = Node(click_ll); layer.data.addPrimitive(node); self.tree_nodes.append(node)
                    self.update_status("{} Counted: {} | ENTER to finish".format(plural, len(self.tree_nodes)))

        def keyPressed(self, e):
            if e.getKeyCode() == 10: 
                if self.step == "CALIBRATE" and self.diameters:
                    self.avg_diameter = sum(self.diameters) / len(self.diameters)
                    for line, n1, n2 in self.temp_lines: layer.data.removePrimitive(line); layer.data.removePrimitive(n1); layer.data.removePrimitive(n2)
                    self.temp_lines = []; self.step = "COUNTING"
                    self.update_status("SHIFT+CLICK to count {} inside the box.".format(plural))
                    JOptionPane.showMessageDialog(None, "Calibration Done: {:.2f}m\n\nNow SHIFT+CLICK every {} inside the sample box.".format(self.avg_diameter, singular))
                elif self.step == "COUNTING": self.finished = True
            elif e.getKeyCode() in [8, 127]: 
                if self.step == "CALIBRATE" and self.diameters:
                    self.diameters.pop(); line, n1, n2 = self.temp_lines.pop()
                    layer.data.removePrimitive(line); layer.data.removePrimitive(n1); layer.data.removePrimitive(n2)
                elif self.step == "COUNTING" and self.tree_nodes: layer.data.removePrimitive(self.tree_nodes.pop())

        def mouseEntered(self, e): pass
        def mouseExited(self, e): pass
        def keyReleased(self, e): pass
        def keyTyped(self, e): pass

    JOptionPane.showMessageDialog(None, "STEP 1: CLICK+DRAW to create a sample box inside the main area.")
    tool = PrecisionSampler(); view = MainApplication.getMap().mapView
    view.addMouseListener(tool); view.addKeyListener(tool); view.requestFocusInWindow()

    def monitor():
        import time
        while not tool.finished: time.sleep(0.1)
        view.removeMouseListener(tool); view.removeKeyListener(tool)
        def finalize():
            layer.data.beginUpdate()
            try:
                count = len(tool.tree_nodes)
                if count > 0:
                    # 1. Calculate Statistics
                    indiv_area = math.pi * ((tool.avg_diameter / 2)**2)
                    density_ratio = float(count) / tool.sample_area_sqm
                    est_total = int(density_ratio * total_area)
                    avg_spacing = math.sqrt(1.0 / density_ratio)
                    
                    canopy_pc = int(round(((est_total * indiv_area) / total_area) * 100 / 5.0) * 5)
                    canopy_pc = max(0, min(100, canopy_pc))
                    density_class = "very_dense" if canopy_pc >= 70 else "dense" if canopy_pc >= 40 else "open" if canopy_pc >= 10 else "scattered"
                    
                    # 2. Buffer proposed tags
                    proposed_tags = {}
                    proposed_tags["wood:density"] = density_class
                    proposed_tags["canopy"] = str(canopy_pc) + "%"
                    proposed_tags["est:stem_count"] = str(est_total)
                    proposed_tags["est:avg_{}".format(tag_suffix)] = "{:.1f}m".format(tool.avg_diameter)
                    proposed_tags["est:avg_spacing"] = "{:.1f}m".format(avg_spacing)
                    proposed_tags["est:source_area"] = str(round(total_area, 1))
                    proposed_tags["source"] = imagery_source
                    
                    current_nat = target.get("natural")
                    current_land = target.get("landuse")
                    
                    # 3. Smart Suggestion Logic
                    perform_save = True
                    
                    if density_class in ["dense", "very_dense"] and current_nat == "scrub":
                        msg = "Density is {}% ({}).\nSuggest changing natural=scrub to natural=wood?\n\nYES: Change tag & Save\nNO: Keep tag & Save\nCANCEL: Exit without saving".format(canopy_pc, density_class)
                        res = JOptionPane.showConfirmDialog(None, msg, "Smart Suggestion", JOptionPane.YES_NO_CANCEL_OPTION)
                        if res == JOptionPane.YES_OPTION:
                            proposed_tags["natural"] = "wood"
                        elif res == JOptionPane.CANCEL_OPTION or res == -1:
                            perform_save = False

                    elif density_class in ["scattered", "open"] and current_nat == "wood" and current_land != "forest":
                        msg = "Density is {}% ({}).\nSuggest changing natural=wood to natural=scrub?\n\nYES: Change tag & Save\nNO: Keep tag & Save\nCANCEL: Exit without saving".format(canopy_pc, density_class)
                        res = JOptionPane.showConfirmDialog(None, msg, "Smart Suggestion", JOptionPane.YES_NO_CANCEL_OPTION)
                        if res == JOptionPane.YES_OPTION:
                            proposed_tags["natural"] = "scrub"
                        elif res == JOptionPane.CANCEL_OPTION or res == -1:
                            perform_save = False
                    
                    # 4. Apply Changes
                    if perform_save:
                        for k, v in proposed_tags.items():
                            target.put(k, v)
                            
                        summary = ("ANALYSIS COMPLETE\n"
                                   "-----------------\n"
                                   "Avg Size: {:.1f}m\n"
                                   "Avg Spacing: {:.1f}m\n"
                                   "Est. Total: {}\n"
                                   "Canopy Cover: {}%").format(tool.avg_diameter, avg_spacing, est_total, canopy_pc)
                        JOptionPane.showMessageDialog(None, summary)
                    else:
                        MainApplication.getMap().statusLine.setHelpText("Density Analysis Cancelled by User.")

                # Cleanup UI elements
                for n in tool.tree_nodes: layer.data.removePrimitive(n)
                if tool.sample_way:
                    nodes = tool.sample_way.getNodes()
                    layer.data.removePrimitive(tool.sample_way)
                    for n in nodes: layer.data.removePrimitive(n)
                
                # FIXED IN V1.2.6: Unconditionally clear status line (no read check)
                MainApplication.getMap().statusLine.setHelpText("")
                    
            finally: layer.data.endUpdate(); layer.invalidate()
        SwingUtilities.invokeLater(finalize)
    Thread(target=monitor).start()

run_analyzer()
