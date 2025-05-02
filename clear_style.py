#!/usr/bin/env python3

import inkex

"""
Extension for InkScape 1.4

Extension removes the style attribute from all selected items, recursively (contents of groups).

Author: Cyrille Médard de Chardon
Mail: cyrille@frakturmedia.net
Date: 2025-05-02
Last change: 2025-05-02
License: GNU GPL v3
"""


class ClearSelection(inkex.EffectExtension):
    """Clear the style attribute of all selected elements and their grouped children."""

    def effect(self):
        """Send each selected item for processing."""
        # For each selected element
        for elem in self.svg.selection:
            self.processItem(elem)

    def processItem(self, elem):
        """Clear style of item or recursively request group's processing."""
        # process group children recursively
        if hasattr(elem, "groupmode") and elem.groupmode == "group":
            for child in elem:
                self.processItem(child)

        # remove style attribute regardless of group or element
        if "style" in elem.attrib:
            del elem.attrib["style"]


if __name__ == "__main__":
    """Run process if not imported."""
    ClearSelection().run()
