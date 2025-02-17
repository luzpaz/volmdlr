import unittest

from dessia_common.core import DessiaObject

import volmdlr
from volmdlr import edges, wires
from volmdlr.models.contours import contour2d_1, contour2d_2


class TestContour2D(unittest.TestCase):
    contour1 = wires.Contour2D([edges.FullArc2D(center=volmdlr.O2D, start_end=volmdlr.Point2D(0.029999999, 0))])
    not_ordered_contour = DessiaObject.load_from_file('wires/contour_not_ordered.json')
    ordered_contour = DessiaObject.load_from_file('wires/contour_ordered.json')

    def test_point_belongs(self):
        point1 = volmdlr.Point2D(0.0144822, 0.00595264)
        point2 = volmdlr.Point2D(0.02, 0.02)
        self.assertTrue(self.contour1.point_belongs(point1))
        self.assertTrue(self.contour1.point_belongs(point2))

        point3 = volmdlr.Point2D(0, 0.013)
        self.assertTrue(contour2d_1.point_belongs(point3))
        self.assertFalse(contour2d_1.point_belongs(point1))

        point4 = volmdlr.Point2D(0.745, 0.0685)
        self.assertTrue(contour2d_2.point_belongs(point4))

    def test_is_ordered(self):
        self.assertTrue(self.ordered_contour.is_ordered())
        self.assertFalse(self.not_ordered_contour.is_ordered())

    def test_order_contour(self):
        ordered_contour = self.not_ordered_contour.order_contour()
        for expected_primitive, primitve in zip(self.ordered_contour.primitives, ordered_contour.primitives):
            self.assertEqual(expected_primitive, primitve)

    def test_cut_by_wire(self):
        pass

    def test_offset(self):
        contour_to_offset = DessiaObject.load_from_file('wires/contour_to_offset.json')
        stringer_contour_offset = contour_to_offset.offset(4)
        self.assertEqual(len(stringer_contour_offset.primitives), 10)
        self.assertAlmostEqual(stringer_contour_offset.area(), 546.1486677646163)


if __name__ == '__main__':
    unittest.main()
