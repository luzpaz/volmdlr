#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common abstract primitives
"""

import math
import warnings
from typing import Dict, List

from numpy import zeros
from scipy.optimize import linprog

# import dessia_common as dc
import volmdlr
import volmdlr.edges


class RoundedLineSegments:
    """
    Rounded Line Segments class.

    """
    _non_serializable_attributes = ['line_class', 'arc_class', 'basis_primitives', 'primitives']

    line_class = volmdlr.edges.LineSegment
    arc_class = volmdlr.edges.Arc

    def __init__(self, points: List[volmdlr.Point3D], radius: Dict[str, float],
                 closed: bool = False, adapt_radius: bool = False, name: str = ''):

        self.points = points
        self.radius = {int(k): v for k, v in radius.items()}
        self.closed = closed
        self.adapt_radius = adapt_radius
        self.name = name
        self.npoints = len(points)

    def frame_mapping(self, frame: volmdlr.Frame3D, side: str):
        """
        Changes frame_mapping and return a new RoundedLineSegments.

        side = 'old' or 'new'
        """
        return self.__class__([point.frame_mapping(frame, side)
                               for point in self.points], radius=self.radius,
                              adapt_radius=self.adapt_radius,
                              name=self.name)

    def frame_mapping_inplace(self, frame: volmdlr.Frame3D, side: str):
        """
        Changes frame_mapping and the object is updated inplace.

        side = 'old' or 'new'
        """
        warnings.warn("'inplace' methods are deprecated. Use a not inplace method instead.", DeprecationWarning)

        for point in self.points:
            point.frame_mapping_inplace(frame, side)

    def arc_features(self, point_index: int):
        raise NotImplementedError('The method arc_features should be overloaded.')

    def _primitives(self):
        alpha = {}
        dist = {}
        lines_length = {}
        # Computing optimal radii
        rounded_points_indices = [int(i) for i in sorted(self.radius.keys())]
        groups = []
        arcs = {}

        if self.radius != {}:
            group = [rounded_points_indices[0]]
            _, _, _, dist0, alpha0 = self.arc_features(rounded_points_indices[0])
            dist[rounded_points_indices[0]] = dist0
            alpha[rounded_points_indices[0]] = alpha0

            for i in rounded_points_indices[1:]:
                # Computing the arc
                _, pi2, _, dist2, alpha2 = self.arc_features(i)
                dist[i] = dist2
                alpha[i] = alpha2
                if i - 1 in self.radius:
                    p1 = self.points[i - 1]
                    p2 = self.points[i]
                    length = (p2 - p1).norm()
                    lines_length[i - 1] = length
                    dist1 = dist[i - 1]

                    if dist1 + dist2 <= length:
                        groups.append(group)
                        group = [i]
                    else:
                        if not self.adapt_radius:
                            raise ValueError
                        group.append(i)
                else:
                    if group != []:
                        groups.append(group)
                    group = [i]
            if group != []:
                groups.append(group)
            if self.adapt_radius:
                if self.closed:
                    if 0 in groups[0]:
                        if self.npoints in groups[-1]:
                            new_group = groups[0] + groups[-1]
                            groups[0] = new_group
                            del groups[-1]

                groups2 = []
                ndof = 0
                dof = {}
                neq_ub = 0
                bounds = []
                for group in groups:
                    lg = len(group)
                    if lg == 1:
                        # Single point, reducing its radius by simple computation if needed
                        ipoint = group[0]
                        if self.closed:
                            if ipoint == 0:
                                p1 = self.points[-1]
                                p2 = self.points[0]
                                p3 = self.points[1]
                            elif ipoint == self.npoints - 1:
                                p1 = self.points[-2]
                                p2 = self.points[-1]
                                p3 = self.points[0]
                            else:
                                p1 = self.points[ipoint - 1]
                                p2 = self.points[ipoint]
                                p3 = self.points[ipoint + 1]

                        else:
                            p1 = self.points[ipoint - 1]
                            p2 = self.points[ipoint]
                            p3 = self.points[ipoint + 1]

                        d1 = p1.point_distance(p2)
                        d2 = p2.point_distance(p3)

                        if dist[ipoint] > (min(d1, d2)):
                            self.radius[ipoint] = min(self.radius[ipoint], min(d1, d2) * math.tan(alpha[ipoint]))

                    else:
                        # Adding to dof
                        bounds.extend([(0, self.radius[j] / math.tan(alpha[j])) for j in group])
                        dof.update({j: ndof + i for i, j in enumerate(group)})
                        ndof += lg
                        groups2.append(group)
                        neq_ub += lg - 1

                # Constructing simplex problem
                # C matrix:
                if ndof > 0:
                    C = zeros(ndof)
                    for j, i in dof.items():
                        C[i] = -math.tan(alpha[j])

                    A_ub = zeros((neq_ub, ndof))
                    b_ub = zeros(neq_ub)
                    ieq_ub = 0

                    for group in groups2:
                        for ip1, ip2 in zip(group[:-1], group[1:]):
                            A_ub[ieq_ub, dof[ip1]] = 1
                            A_ub[ieq_ub, dof[ip2]] = 1
                            b_ub[ieq_ub] = lines_length[ip1]
                            ieq_ub += 1

                    d = linprog(C, A_ub, b_ub, bounds=bounds)

                    for ipoint, dof_point in dof.items():
                        r = d.x[dof_point] * math.tan(alpha[ipoint])
                        if r > 1e-10:
                            self.radius[ipoint] = r
                        else:
                            del self.radius[ipoint]

            # Creating geometry
            # Creating arcs
            for ipoint, r in self.radius.items():
                ps, pi, pe, _, _ = self.arc_features(ipoint)
                arcs[ipoint] = self.arc_class(ps, pi, pe)

        return self.primitives_from_arcs(arcs)

    def primitives_from_arcs(self, arcs):
        primitives = []
        # Creating lines
        for iline in range(self.npoints - 1):
            if iline in self.radius:
                arc1 = arcs[iline]
                primitives.append(arc1)
                if iline + 1 in self.radius:
                    arc2 = arcs[iline + 1]
                    if arc1.end != arc2.start:
                        primitives.append(self.line_class(arc1.end, arc2.start))
                else:
                    if arc1.end != self.points[iline + 1]:
                        primitives.append(self.line_class(arc1.end, self.points[iline + 1]))
            else:
                p1 = self.points[iline]
                if iline + 1 in self.radius:
                    arc2 = arcs[iline + 1]
                    if p1 != arc2.start:
                        primitives.append(self.line_class(p1, arc2.start))
                else:
                    primitives.append(self.line_class(p1, self.points[iline + 1]))

        if self.closed:
            if self.npoints - 1 in self.radius:
                arc1 = arcs[self.npoints - 1]
                primitives.append(arc1)
                if 0 in self.radius:
                    arc2 = arcs[0]
                    if arc1.end != arc2.start:
                        primitives.append(self.line_class(arc1.end, arc2.start))
                else:
                    primitives.append(self.line_class(arc1.end, self.points[iline + 1]))
            else:
                p1 = self.points[self.npoints - 1]
                if 0 in self.radius:
                    arc2 = arcs[0]
                    if p1 != arc2.start:
                        primitives.append(self.line_class(p1, arc2.start))
                else:
                    primitives.append(self.line_class(p1, self.points[0]))

        return primitives
