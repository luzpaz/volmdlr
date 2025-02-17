"""
Unit tests for CylindriSurface3D
"""
import math
import unittest

import dessia_common.core
import volmdlr
from volmdlr import OXYZ, Z3D, Point2D, Point3D, edges, faces, wires


class TestCylindricalSurface3D(unittest.TestCase):
    cylindrical_surface = faces.CylindricalSurface3D(volmdlr.OXYZ, 0.32)
    cylindrical_surface2 = faces.CylindricalSurface3D(volmdlr.OXYZ, 1.0)
    frame = volmdlr.Frame3D(volmdlr.Point3D(-0.005829, 0.000765110438227, -0.0002349369830163),
                            volmdlr.Vector3D(-0.6607898454031987, 0.562158151695499, -0.4973278523210991),
                            volmdlr.Vector3D(-0.7505709694705869, -0.4949144228333324, 0.43783893597935386),
                            volmdlr.Vector3D(-0.0, 0.6625993710787045, 0.748974013865705))
    cylindrical_surface3 = faces.CylindricalSurface3D(frame, 0.003)
    cylindrical_surface4 = faces.CylindricalSurface3D(OXYZ, radius=0.03)

    def test_line_intersections(self):
        line3d = edges.Line3D(volmdlr.O3D, volmdlr.Point3D(0.3, 0.3, .3))
        line_inters = self.cylindrical_surface.line_intersections(line3d)
        self.assertEqual(len(line_inters), 2)
        self.assertEqual(line_inters[0], volmdlr.Point3D(0.22627416, 0.22627416, 0.22627416))
        self.assertEqual(line_inters[1], volmdlr.Point3D(-0.22627416, -0.22627416, -0.22627416))

    def test_plane_intersections(self):
        plane_surface = faces.Plane3D(volmdlr.OZXY)
        parallel_plane_secant_cylinder = plane_surface.frame_mapping(volmdlr.Frame3D(
            volmdlr.O3D, volmdlr.Point3D(.5, 0, 0), volmdlr.Point3D(0, .5, 0), volmdlr.Point3D(0, 0, .2)), 'new')
        cylinder_tanget_plane = plane_surface.frame_mapping(volmdlr.Frame3D(
            volmdlr.Point3D(0, 0.32/2, 0), volmdlr.Point3D(.5, 0, 0),
            volmdlr.Point3D(0, .5, 0), volmdlr.Point3D(0, 0, .2)), 'new')
        not_intersecting_cylinder_parallel_plane = plane_surface.frame_mapping(volmdlr.Frame3D(
            volmdlr.Point3D(0, 0.32, 0), volmdlr.Point3D(.5, 0, 0),
            volmdlr.Point3D(0, .5, 0), volmdlr.Point3D(0, 0, .2)), 'new')
        cylinder_concurrent_plane = plane_surface.rotation(volmdlr.O3D, volmdlr.X3D, math.pi/4)
        cylinder_perpendicular_plane = plane_surface.rotation(volmdlr.O3D, volmdlr.X3D, math.pi/2)

        cylinder_surface_secant_parallel_plane_intersec = self.cylindrical_surface.plane_intersection(
            parallel_plane_secant_cylinder)
        self.assertEqual(len(cylinder_surface_secant_parallel_plane_intersec), 2)
        self.assertTrue(isinstance(cylinder_surface_secant_parallel_plane_intersec[0], edges.Line3D))
        self.assertTrue(isinstance(cylinder_surface_secant_parallel_plane_intersec[1], edges.Line3D))

        cylinder_surface_tangent_plane = self.cylindrical_surface.plane_intersection(
            cylinder_tanget_plane)
        self.assertEqual(len(cylinder_surface_tangent_plane), 1)
        self.assertTrue(isinstance(cylinder_surface_tangent_plane[0], edges.Line3D))

        cylinder_surface_tangent_plane_not_intersecting = self.cylindrical_surface.plane_intersection(
            not_intersecting_cylinder_parallel_plane)
        self.assertEqual(len(cylinder_surface_tangent_plane_not_intersecting), 0)

        cylinder_surface_concurrent_plane_intersec = self.cylindrical_surface.plane_intersection(
            cylinder_concurrent_plane)
        self.assertTrue(isinstance(cylinder_surface_concurrent_plane_intersec[0], wires.Ellipse3D))

        cylinder_surface_perpendicular_plane_intersec = self.cylindrical_surface.plane_intersection(
            cylinder_perpendicular_plane)
        self.assertTrue(isinstance(cylinder_surface_perpendicular_plane_intersec[0], wires.Circle3D))

    def test_is_coincident(self):
        cyl_surface1 = faces.CylindricalSurface3D(volmdlr.OXYZ, 1)
        cyl_surface2 = faces.CylindricalSurface3D(volmdlr.OXYZ.translation(volmdlr.Vector3D(0, 0, 1)), 1)
        plane_face = faces.Plane3D(volmdlr.OXYZ)
        self.assertTrue(cyl_surface1.is_coincident(cyl_surface2))
        self.assertFalse(cyl_surface1.is_coincident(plane_face))
        self.assertFalse(self.cylindrical_surface.is_coincident(cyl_surface1))

    def test_point_on_surface(self):
        point = volmdlr.Point3D(0.32, 0, 1)
        point2 = volmdlr.Point3D(1, 1, 1)
        self.assertTrue(self.cylindrical_surface.point_on_surface(point))
        self.assertFalse((self.cylindrical_surface.point_on_surface(point2)))

    def test_arcellipse3d_to_2d(self):
        pass

    def test_arc3d_to_2d(self):
        arc1 = edges.Arc3D(volmdlr.Point3D(1, 0, 0), volmdlr.Point3D(1/math.sqrt(2), 1/math.sqrt(2), 0),
                           volmdlr.Point3D(0, 1, 0))
        arc2 = edges.Arc3D(volmdlr.Point3D(1, 0, 0), volmdlr.Point3D(1/math.sqrt(2), -1/math.sqrt(2), 0),
                           volmdlr.Point3D(0, -1, 0))
        arc3 = edges.Arc3D(volmdlr.Point3D(-1/math.sqrt(2), 1/math.sqrt(2), 0), volmdlr.Point3D(-1, 0, 0),
                           volmdlr.Point3D(-1/math.sqrt(2), -1/math.sqrt(2), 0))
        arc4 = edges.Arc3D(volmdlr.Point3D(0, -1, 0), volmdlr.Point3D(-1 / math.sqrt(2), 1 / math.sqrt(2), 0),
                           volmdlr.Point3D(1, 0, 0))
        test1 = self.cylindrical_surface2.arc3d_to_2d(arc3d=arc1)[0]
        test2 = self.cylindrical_surface2.arc3d_to_2d(arc3d=arc2)[0]
        test3 = self.cylindrical_surface2.arc3d_to_2d(arc3d=arc3)[0]
        test4 = self.cylindrical_surface2.arc3d_to_2d(arc3d=arc4)[0]

        inv_prof = self.cylindrical_surface2.linesegment2d_to_3d(test4)[0]

        # Assert that the returned object is an edges.LineSegment2D
        self.assertIsInstance(test1, edges.LineSegment2D)
        self.assertIsInstance(test2, edges.LineSegment2D)
        self.assertIsInstance(test3, edges.LineSegment2D)
        self.assertIsInstance(test4, edges.LineSegment2D)

        # Assert that the returned object is right on the parametric domain (take into account periodicity)
        self.assertEqual(test1.start, volmdlr.Point2D(0, 0))
        self.assertEqual(test1.end, volmdlr.Point2D(0.5*math.pi, 0))
        self.assertEqual(test2.start, volmdlr.Point2D(0, 0))
        self.assertEqual(test2.end, volmdlr.Point2D(-0.5*math.pi, 0))
        self.assertEqual(test3.start, volmdlr.Point2D(0.75*math.pi, 0))
        self.assertEqual(test3.end, volmdlr.Point2D(1.25*math.pi, 0))
        self.assertEqual(test4.start, volmdlr.Point2D(-0.5 * math.pi, 0))
        self.assertEqual(test4.end, volmdlr.Point2D(-2 * math.pi, 0))

        # Verifies the inversion operation
        self.assertIsInstance(inv_prof, edges.Arc3D)
        self.assertEqual(inv_prof, arc4)

    def test_contour3d_to_2d(self):
        primitives_cylinder = [edges.LineSegment3D(Point3D(0.03, 0, 0.003), Point3D(0.03, 0, 0.013)),
                               edges.FullArc3D(Point3D(0, 0, 0.013), Point3D(0.03, 0, 0.013), Z3D),
                               edges.LineSegment3D(Point3D(0.03, 0, 0.013), Point3D(0.03, 0, 0.003)),
                               edges.FullArc3D(Point3D(0, 0, 0.003), Point3D(0.03, 0, 0.003), Z3D)
                               ]
        contour_cylinder = wires.Contour3D(primitives_cylinder)

        contour2d_cylinder = self.cylindrical_surface4.contour3d_to_2d(contour_cylinder)

        area = contour2d_cylinder.area()
        fullarc2d = contour2d_cylinder.primitives[3]
        linesegment2d = contour2d_cylinder.primitives[2]

        self.assertEqual(area, 0.02*math.pi)
        self.assertEqual(fullarc2d.start, Point2D(-2*math.pi, 0.003))
        self.assertEqual(fullarc2d.end, Point2D(0, 0.003))
        self.assertEqual(linesegment2d.start, Point2D(-2*math.pi, 0.013))
        self.assertEqual(linesegment2d.end, Point2D(-2*math.pi, 0.003))

    def test_face_from_contours3d(self):
        surface = dessia_common.core.DessiaObject.load_from_file(
            'faces/objects_cylindrical_tests/surface3d_1.json')
        contour0 = dessia_common.core.DessiaObject.load_from_file(
            'faces/objects_cylindrical_tests/contour_1_0.json')
        contour1 = dessia_common.core.DessiaObject.load_from_file(
            'faces/objects_cylindrical_tests/contour_1_1.json')

        face = surface.face_from_contours3d([contour0, contour1])

        self.assertEqual(face.surface2d.area(), 0.00077*2*math.pi)

        frame = volmdlr.Frame3D(volmdlr.O3D, volmdlr.X3D, volmdlr.Y3D, volmdlr.Z3D)
        cylindrical = faces.CylindricalSurface3D(frame, 0.2)
        fullarc1 = edges.FullArc3D(center=volmdlr.O3D, start_end=volmdlr.Point3D(0.2, 0.0, 0.0), normal=volmdlr.Z3D)
        fullarc2 = edges.FullArc3D(center=volmdlr.O3D, start_end=volmdlr.Point3D(-0.2, 0.0, 0.2), normal=volmdlr.Z3D)
        contour1 = wires.Contour3D([fullarc1])
        contour2 = wires.Contour3D([fullarc2])
        face = cylindrical.face_from_contours3d([contour1, contour2])
        self.assertEqual(face.surface2d.area(), 0.2*2*math.pi)


if __name__ == '__main__':
    unittest.main()
