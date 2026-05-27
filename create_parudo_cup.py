#!/usr/bin/env python3

"""
Creates the flat pattern for a dice cup of specified dimensions.

Extension for InkScape 1.4

Author: Cyrille Médard de Chardon
Mail: cyrille@frakturmedia.net
Date: 2026-05-27
License: GNU GPL v3
"""

import math, inkex
from inkex.utils import debug


class GenerateCup(inkex.EffectExtension):
    """Generates the path desigh for a parudo cup."""

    base_holes_count = 14
    climb_holes_count = 12
    cap_holes_count = 24

    # styling
    base_style = {
        "stroke": "#0000ff",
        "stroke-width": "0.5",
        "fill": "none",
    }

    def effect(self):
        """Create the cup, base, and cap. Perforated."""
        self.calculate()
        self.makeCup(self.options.s3, self.options.s2, self.options.theta)
        self.makeBase(
            "Cup base",
            (0, 100),
            self.options.r2,
            self.options.mat_thickness,
            self.base_holes_count,
            self.options.holes_offset,
            self.options.holes_radii,
        )
        self.makeBase(
            "Cup cap",
            # + 7 make the cap a little larger than the cup
            (self.options.r1 + 7 + self.options.r2, 100),
            self.options.r1 + 7,
            self.options.mat_thickness,
            self.cap_holes_count,
            self.options.holes_offset,
            self.options.holes_radii,
        )

    def makeBase(
        self,
        group_name,
        loc,
        bradius,
        mat_thickness,
        holes_count,
        holes_offset,
        holes_radii,
    ):
        """Makes the parudo cup base and holes."""
        group = inkex.Group()
        group.label = group_name

        debug(f"Bradius is {bradius}")
        base = inkex.Circle()
        # locate the base under the origin
        base.center = loc
        # reduce the base radius by half of the material thickness
        base.radius = bradius - mat_thickness / 2
        base.style = self.base_style

        # Add to current layer
        group.add(base)

        # Add the holes #####################
        rad_shift = 2 * math.pi / holes_count
        # need to compensate radius for offset and material thickness
        radalt = bradius - mat_thickness / 2 - holes_offset
        for i in range(holes_count):
            # make and locate each hole
            hole = inkex.Circle()
            cx = loc[0] + radalt * math.cos(rad_shift * i)
            cy = loc[1] + radalt * math.sin(rad_shift * i)
            hole.center = (cx, cy)
            hole.radius = holes_radii
            hole.style = self.base_style

            # Add to current layer
            group.add(hole)

        # add the group to the SVG layer
        self.svg.get_current_layer().add(group)

    def makeCup(self, radsm, radlg, arcangle):
        """Create the parudo cup."""
        group = inkex.Group()
        group.label = "Cup shape"

        # Make the cup #####################
        radangle = arcangle / 180 * math.pi

        # arc origin coordinats
        cx = 0
        cy = 0

        x1 = cx + radsm * math.cos(-radangle / 2)
        y1 = cy + radsm * math.sin(-radangle / 2)

        x2 = cx + radsm * math.cos(radangle / 2)
        y2 = cy + radsm * math.sin(radangle / 2)

        x3 = cx + radlg * math.cos(radangle / 2)
        y3 = cy + radlg * math.sin(radangle / 2)

        x4 = cx + radlg * math.cos(-radangle / 2)
        y4 = cy + radlg * math.sin(-radangle / 2)

        large_arc = 1 if arcangle > 180 else 0
        # sweep = 1

        arc = inkex.PathElement()
        arc.path = f"""
            M {x1},{y1}
            A {radsm},{radsm} 0 {large_arc},1 {x2},{y2}
            L {x3},{y3}
            A {radlg},{radlg} 0 {large_arc},0 {x4},{y4}
            L {x1},{y1}
            Z
            """

        arc.style = self.base_style
        arc.label = "Cup arc"

        # Add to current layer
        group.add(arc)

        # Add the perforations along the bottom #####################

        # adjust the hole distance
        radalt = radsm + self.options.holes_offset
        # convert the hole offset to angular
        angular_offset = math.atan(self.options.holes_offset / radalt)
        # determine the angular shift between holes
        rad_shift = (radangle - 2 * angular_offset) / (self.base_holes_count - 1)

        for i in range(self.base_holes_count):
            # locate the hole
            cx = radalt * math.cos(angular_offset - radangle / 2 + rad_shift * i)
            cy = radalt * math.sin(angular_offset - radangle / 2 + rad_shift * i)

            # make hole, attributes, style
            hole = inkex.Circle()
            hole.center = (cx, cy)
            hole.radius = self.options.holes_radii
            hole.style = self.base_style

            # add to group
            group.add(hole)

        # Add the holes climbing the edges ######################
        radius_gap = (radlg - radsm - 2 * self.options.holes_offset) / (
            self.climb_holes_count - 1
        )

        for i in range(1, self.climb_holes_count):
            var_rad = radalt + radius_gap * i
            # need to calculate the angular_offset for each hole here
            angular_offset = math.atan(self.options.holes_offset / var_rad)
            # locate the hole
            cx = var_rad * math.cos(angular_offset - radangle / 2)
            cy = var_rad * math.sin(angular_offset - radangle / 2)

            # make two holes and set attributes, style
            # on hole for each side of arc
            hole1 = inkex.Circle()
            hole2 = inkex.Circle()
            hole1.center = (cx, cy)
            hole2.center = (cx, -cy)
            hole1.radius = self.options.holes_radii
            hole2.radius = self.options.holes_radii
            hole1.style = self.base_style
            hole2.style = self.base_style

            # add to group
            group.add(hole1)
            group.add(hole2)

        # add the group to the SVG layer
        self.svg.get_current_layer().add(group)

    def add_arguments(self, pars):
        """Process the GUI parameters."""
        pars.add_argument("--r1", type=float, help="Top radius")
        pars.add_argument("--r2", type=float, help="Bottom radius")
        pars.add_argument("--h", type=float, help="Cup height")
        pars.add_argument("--holes_offset", type=float, help="Hole offset")
        pars.add_argument("--holes_radii", type=float, help="Hole radii")
        pars.add_argument("--mat_thickness", type=float, help="Material thickness")
        # these are then available as self.options.r1/r2/h

    def calculate(self):
        """Calculates all the measurements based on passed parameters."""

        #  A        R1
        # ---|---|-------   /
        # \  |   |      /  /
        #  \ |H  |H2   /  /
        # S1\|   | R2 /  /
        #    ----|----  S2
        #     \  |  /  /
        #    S3\ | /  /
        #       \|/  /
        #        V  /

        # calculate radial difference (A)
        self.options.a = self.options.r1 - self.options.r2

        # calculate truncated slant height (S1)
        self.options.s1 = math.sqrt(
            math.pow(self.options.a, 2) + math.pow(self.options.h, 2)
        )

        # calculate full slant height (S2): A/S1 = R1/S2
        self.options.s2 = self.options.r1 * self.options.s1 / self.options.a
        self.options.s3 = self.options.s2 - self.options.s1

        # calculate theta: 360 * (r1 / s2) (convert from radians to degrees)
        self.options.theta = 360 * self.options.r1 / self.options.s2

        # calculate theta
        debug(self.options.r1)
        debug(self.options.r2)
        debug(self.options.h)
        debug(self.options.a)
        debug(self.options.s1)
        debug(self.options.s2)
        debug(self.options.s3)
        debug(self.options.theta)


if __name__ == "__main__":
    """Run process if not imported."""
    GenerateCup().run()
