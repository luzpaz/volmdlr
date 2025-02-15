import unittest
from copy import deepcopy
import volmdlr
import volmdlr.edges
from volmdlr.core import CompositePrimitive2D


class TestCompositePrimitive2D(unittest.TestCase):
    def setUp(self):
        self.primitives = [
            volmdlr.edges.LineSegment2D(volmdlr.O2D, volmdlr.Point2D(volmdlr.TWO_PI, 0.0)),
            volmdlr.edges.LineSegment2D(
                volmdlr.Point2D(volmdlr.TWO_PI, 0.0),
                volmdlr.Point2D(volmdlr.TWO_PI, 0.003),
            ),
        ]
        self.composite_2d = CompositePrimitive2D(deepcopy(self.primitives), name="test")

        self.square_primitives = [
            volmdlr.edges.LineSegment2D(volmdlr.Point2D(0.0, 0.0), volmdlr.Point2D(0.0, 1.0)),
            volmdlr.edges.LineSegment2D(volmdlr.Point2D(0.0, 1.0), volmdlr.Point2D(1.0, 1.0)),
            volmdlr.edges.LineSegment2D(volmdlr.Point2D(1.0, 1.0), volmdlr.Point2D(1.0, 0.0)),
            volmdlr.edges.LineSegment2D(volmdlr.Point2D(1.0, 0.0), volmdlr.Point2D(0.0, 0.0)),
        ]
        self.square_composite_2d = CompositePrimitive2D(self.square_primitives, name="square")

    def test_plot(self):
        ax = self.composite_2d.plot()
        self.assertIsNotNone(ax)

    def test_plot2(self):
        ax = self.square_composite_2d.plot()
        for ls, line in zip(self.square_composite_2d.primitives, ax.lines):
            self.assertListEqual(line.get_xydata().tolist(), [[ls.start.x, ls.start.y], [ls.end.x, ls.end.y]])

    def test_plot_equal_aspect(self):
        ax = self.composite_2d.plot(equal_aspect=True)
        self.assertEqual(ax.get_aspect(), 1.0)

    def test_init(self):
        self.assertEqual(self.composite_2d.primitives, self.primitives)
        self.assertEqual(self.composite_2d.name, "test")

    def test_rotation(self):
        center = volmdlr.Point2D(1.2, -3.4)
        angle = 2.56
        rotated_composite_2d = self.composite_2d.rotation(center, angle)

        for p1, p2 in zip(rotated_composite_2d.primitives, self.primitives):
            self.assertNotEqual(p1, p2)
            p2 = p2.rotation(center, angle)
            self.assertEqual(p1, p2)

    def test_translation(self):
        offset = volmdlr.Vector2D(0.56, -3.4)
        rotated_composite_2d = self.composite_2d.translation(offset)

        for p1, p2 in zip(rotated_composite_2d.primitives, self.primitives):
            self.assertNotEqual(p1, p2)
            p2 = p2.translation(offset)
            self.assertEqual(p1, p2)

    def test_frame_mapping(self):
        frame = volmdlr.Frame2D(volmdlr.O2D, volmdlr.Vector2D(1.0, 1.0), volmdlr.Vector2D(1.0, -1.0))
        side = "new"
        mapped_composite_2d = self.composite_2d.frame_mapping(frame, side)

        for p1, p2 in zip(mapped_composite_2d.primitives, self.primitives):
            self.assertNotEqual(p1, p2)
            p2 = p2.frame_mapping(frame, side)
            self.assertEqual(p1, p2)


if __name__ == "__main__":
    unittest.main()
