# Translated from OCCT src/ModelingData/TKGeomBase/GTests/Hermit_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom import Geom_BSplineCurve
from nanocct.Geom2d import Geom2d_BSplineCurve
from nanocct.gp import gp_Pnt, gp_Pnt2d
from nanocct.Hermit import Hermit
from nanocct.NCollection import NCollection_Array1


def _arr(typ, values):
    a = NCollection_Array1[typ](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


def _bs3d(w1, w2, w3):
    poles = _arr(gp_Pnt, [gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 0), gp_Pnt(2, 0, 0)])
    return Geom_BSplineCurve(poles, _arr(float, [w1, w2, w3]), _arr(float, [0.0, 1.0]), _arr(int, [3, 3]), 2)


def _bs2d(w1, w2, w3):
    poles = _arr(gp_Pnt2d, [gp_Pnt2d(0, 0), gp_Pnt2d(1, 1), gp_Pnt2d(2, 0)])
    return Geom2d_BSplineCurve(poles, _arr(float, [w1, w2, w3]), _arr(float, [0.0, 1.0]), _arr(int, [3, 3]), 2)


def _ends(bs, y0, y1, tol):
    r = Hermit.Solution_s(bs)
    assert r is not None
    assert abs(r.Value(r.FirstParameter()).Y() - y0) <= tol
    assert abs(r.Value(r.LastParameter()).Y() - y1) <= tol
    return r


def test_HermitTest_Solution3D_UniformWeights_ReturnsValidCurve():
    r = _ends(_bs3d(1.0, 1.0, 1.0), 1.0, 1.0, 1.0e-6)
    assert r.NbPoles() >= 4


def test_HermitTest_Solution3D_DistinctWeights_ReturnsValidCurve():
    _ends(_bs3d(2.0, 1.5, 3.0), 0.5, 1.0 / 3.0, 1.0e-4)


def test_HermitTest_Solution3D_HighWeightRatio_Endpoint():
    _ends(_bs3d(0.5, 1.0, 5.0), 2.0, 0.2, 1.0e-4)


def test_HermitTest_Solution3D_ReversedWeightRatio_Endpoint():
    _ends(_bs3d(5.0, 1.0, 0.5), 0.2, 2.0, 1.0e-4)


def test_HermitTest_Solution3D_PositivePoles():
    r = Hermit.Solution_s(_bs3d(2.0, 3.0, 1.5))
    assert r is not None
    for i in range(1, r.NbPoles() + 1):
        assert r.Pole(i).Y() > 0.0


def test_HermitTest_Solution2D_UniformWeights_ReturnsValidCurve():
    _ends(_bs2d(1.0, 1.0, 1.0), 1.0, 1.0, 1.0e-6)


def test_HermitTest_Solution2D_DistinctWeights_ReturnsValidCurve():
    _ends(_bs2d(2.0, 1.5, 3.0), 0.5, 1.0 / 3.0, 1.0e-4)


def test_HermitTest_Solution2D_HighWeightRatio_Endpoint():
    _ends(_bs2d(0.5, 1.0, 5.0), 2.0, 0.2, 1.0e-4)


def test_HermitTest_Solutionbis_UniformWeights_KnotsUnchanged():
    kmin, kmax = Hermit.Solutionbis_s(_bs3d(1.0, 1.0, 1.0), 0.0, 1.0)
    assert kmin >= 0.0
    assert kmax <= 1.0


def test_HermitTest_Solutionbis_DistinctWeights_ReturnsValidKnots():
    kmin, kmax = Hermit.Solutionbis_s(_bs3d(2.0, 1.5, 3.0), 0.0, 1.0)
    assert kmin >= 0.0
    assert kmax <= 1.0
    assert kmin <= kmax


def test_HermitTest_Solution3D_Symmetric_WeightsProduceSymmetricResult():
    _ends(_bs3d(2.0, 1.0, 2.0), 0.5, 0.5, 1.0e-4)
