import math
import unittest

import volmdlr
from volmdlr import edges, faces


class TestToroidalSurface3D(unittest.TestCase):
    toroidal_surface = faces.ToroidalSurface3D(volmdlr.OXYZ, 1, 0.1)
    frame = volmdlr.Frame3D(volmdlr.Point3D(-0.005829, 0.000765110438227, -0.0002349369830163),
                            volmdlr.Vector3D(-0.6607898454031987, 0.562158151695499, -0.4973278523210991),
                            volmdlr.Vector3D(-0.7505709694705869, -0.4949144228333324, 0.43783893597935386),
                            volmdlr.Vector3D(-0.0, 0.6625993710787045, 0.748974013865705))
    toroidal_surface2 = faces.ToroidalSurface3D(frame, 0.000725, 0.000125)

    def test_arc3d_to_2d(self):
        arc1 = edges.Arc3D(volmdlr.Point3D(1-0.1/math.sqrt(2), 0, 0.1/math.sqrt(2)),
                           volmdlr.Point3D(0.9, 0, 0), volmdlr.Point3D(1-0.1/math.sqrt(2), 0, -0.1/math.sqrt(2)))

        test1 = self.toroidal_surface.arc3d_to_2d(arc3d=arc1)[0]

        # Assert that the returned object is an edges.LineSegment2D
        self.assertIsInstance(test1, edges.LineSegment2D)

        # Assert that the returned object is right on the parametric domain (take into account periodicity)
        self.assertEqual(test1.start, volmdlr.Point2D(0, 0.75 * math.pi))
        self.assertEqual(test1.end, volmdlr.Point2D(0, 1.25 * math.pi))

    def test_bsplinecurve3d_to_2d(self):
        control_points = [volmdlr.Point3D(-0.006429000000000001, 0.000765110438227, -0.0002349369830163),
                          volmdlr.Point3D(-0.006429000000000001, 0.0007527699876436001, -0.0002071780906932),
                          volmdlr.Point3D(-0.006429000000000001, 0.0007289073904888, -0.0001535567864537),
                          volmdlr.Point3D(-0.006429000000000001, 0.0006930461151679999, -7.904060141388999e-05),
                          volmdlr.Point3D(-0.006429000000000001, 0.0006567972565296, -1.323031929501e-05),
                          volmdlr.Point3D(-0.006429000000000001, 0.0006198714960685, 4.331237693835e-05),
                          volmdlr.Point3D(-0.006429000000000001, 0.0005818146300831, 9.111011896111e-05),
                          volmdlr.Point3D(-0.006429000000000001, 0.0005560693653727, 0.00011689162321630001),
                          volmdlr.Point3D(-0.006429000000000001, 0.0005431250195402, 0.00012834317593889998)]
        knot_multiplicities = [4, 1, 1, 1, 1, 1, 4]
        knots = [0.0, 0.1666666666667, 0.3333333333333, 0.5, 0.6666666666667, 0.8333333333333, 1.0]
        bspline_curve3d = edges.BSplineCurve3D(3, control_points, knot_multiplicities, knots)

        test = self.toroidal_surface2.bsplinecurve3d_to_2d(bspline_curve3d)[0]
        inv_prof = self.toroidal_surface2.bsplinecurve2d_to_3d(test)[0]

        self.assertEqual(test.start, volmdlr.Point2D(0.8489211153847066, math.pi))
        self.assertEqual(test.end, volmdlr.Point2D(1.4449243890313308, 1.5707974196708867))

        self.assertEqual(inv_prof.end, bspline_curve3d.end)


if __name__ == '__main__':
    unittest.main()
