# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Intf_InterferencePolygon2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.gp import gp_Pnt2d
from nanocct.Intf import Intf_InterferencePolygon2d, Intf_Polygon2d

pytestmark = pytest.mark.skip(reason="a Python subclass of an abstract OCCT class: nanocct binds no trampolines (docs/Excluded.md, Python subclasses of OCCT's abstract interfaces)")


class _TestPolygon2d(Intf_Polygon2d):
    """Exact test polyline, including empty input and closed endpoint handling."""

    def __init__(self, points, closed=False):
        super().__init__()
        self._points = [gp_Pnt2d(p.X(), p.Y()) for p in points]   # copied, as the C++ test copies its array
        self._closed = closed
        for point in self._points:
            self.myBox.Add(point)

    def Closed(self):
        return self._closed

    def DeflectionOverEstimation(self):
        return 0.0                                  # segments are exact

    def NbSegments(self):
        return max(0, len(self._points) - 1)       # empty input has no segments

    def Segment(self, index, first, last):          # one-based indices
        first.SetCoord(self._points[index - 1].X(), self._points[index - 1].Y())
        last.SetCoord(self._points[index].X(), self._points[index].Y())


def _pts(*coords):
    return [gp_Pnt2d(x, y) for x, y in coords]


def test_Intf_InterferencePolygon2d_Test_CrossingPolylinesPreserveSegmentOrder():
    zigzag = _TestPolygon2d(_pts((-1, -1), (1, 1), (3, -1), (5, 1)))
    line = _TestPolygon2d(_pts((-2, 0), (6, 0)))
    intersection = Intf_InterferencePolygon2d(zigzag, line)
    assert intersection.NbSectionPoints() == 3
    assert intersection.NbTangentZones() == 0
    for i in range(1, 4):
        assert intersection.Pnt2dValue(i).X() == pytest.approx(2.0 * (i - 1), abs=1e-14)
        assert intersection.Pnt2dValue(i).Y() == pytest.approx(0.0, abs=1e-14)
    reverse = Intf_InterferencePolygon2d(line, zigzag)
    assert reverse.NbSectionPoints() == 3
    for i in range(1, 4):
        assert reverse.Pnt2dValue(i).Distance(intersection.Pnt2dValue(i)) == pytest.approx(0.0, abs=1e-14)


def test_Intf_InterferencePolygon2d_Test_ClosedBowTieHasOneSelfIntersection():
    polygon = _TestPolygon2d(_pts((-1, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)), True)
    intersection = Intf_InterferencePolygon2d(polygon)
    assert intersection.NbSectionPoints() == 1
    assert intersection.Pnt2dValue(1).Distance(gp_Pnt2d(0, 0)) == pytest.approx(0.0, abs=1e-14)
    assert intersection.NbTangentZones() == 0


def test_Intf_InterferencePolygon2d_Test_EmptySelfIntersection():
    intersection = Intf_InterferencePolygon2d(_TestPolygon2d([]))
    assert intersection.NbSectionPoints() == 0
    assert intersection.NbTangentZones() == 0


def test_Intf_InterferencePolygon2d_Test_ClosedPolygonDoesNotReportItsClosureVertex():
    intersection = Intf_InterferencePolygon2d(_TestPolygon2d(_pts((0, 0), (2, 0), (1, 1), (0, 0)), True))
    assert intersection.NbSectionPoints() == 0
    assert intersection.NbTangentZones() == 0


def test_Intf_InterferencePolygon2d_Test_ReuseRefreshesClosureSegmentCount():
    crossing = _TestPolygon2d(_pts((-1, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)), True)
    simple = _TestPolygon2d(_pts((0, 0), (2, 0), (1, 1), (0, 0)), True)
    intersection = Intf_InterferencePolygon2d(simple, crossing)
    for _ in range(2):
        intersection.Perform(crossing)
        assert intersection.NbSectionPoints() == 1
        assert intersection.Pnt2dValue(1).Distance(gp_Pnt2d(0, 0)) == pytest.approx(0.0, abs=1e-14)
        intersection.Perform(simple)
        assert intersection.NbSectionPoints() == 0
    intersection.Perform(_TestPolygon2d([]))
    assert intersection.NbSectionPoints() == 0


def test_Intf_InterferencePolygon2d_Test_OpenBowTieRetainsFirstSegmentCrossing():
    intersection = Intf_InterferencePolygon2d(_TestPolygon2d(_pts((-1, -1), (1, 1), (-1, 1), (1, -1))))
    assert intersection.NbSectionPoints() == 1
    assert intersection.Pnt2dValue(1).Distance(gp_Pnt2d(0, 0)) == pytest.approx(0.0, abs=1e-14)
