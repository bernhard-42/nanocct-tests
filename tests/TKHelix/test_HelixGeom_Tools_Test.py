# Translated from OCCT src/ModelingAlgorithms/TKHelix/GTests/HelixGeom_Tools_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GeomAbs import GeomAbs_C0, GeomAbs_C1, GeomAbs_C2
from nanocct.gp import gp_Pnt
from nanocct.HelixGeom import HelixGeom_HelixCurve, HelixGeom_Tools

TOL = 1.0e-6


def test_HelixGeom_Tools_Test_ApprHelix():
    result, bspl, max_err = HelixGeom_Tools.ApprHelix_s(0.0, 2.0 * math.pi, 10.0, 5.0, 0.0, True, TOL)
    assert result == 0
    assert bspl is not None
    assert max_err <= TOL
    assert bspl.Degree() > 0
    assert bspl.NbPoles() > 0


def test_HelixGeom_Tools_Test_ApprCurve3D():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 2.0 * math.pi, 10.0, 3.0, 0.0, True)
    h_adaptor = HelixGeom_HelixCurve(helix)
    result, bspl, max_err = HelixGeom_Tools.ApprCurve3D_s(h_adaptor, TOL, GeomAbs_C1, 50, 6)
    assert result == 0
    assert bspl is not None
    assert max_err <= TOL * 10
    n = 10
    for i in range(n + 1):
        param = helix.FirstParameter() + i * (helix.LastParameter() - helix.FirstParameter()) / n
        orig = helix.Value(param)
        bparam = bspl.FirstParameter() + i * (bspl.LastParameter() - bspl.FirstParameter()) / n
        approx = gp_Pnt()
        bspl.D0(bparam, approx)
        assert orig.Distance(approx) <= max_err * 2


def test_HelixGeom_Tools_Test_DifferentContinuity():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 6.0 * math.pi, 15.0, 4.0, 0.05, True)
    h_adaptor = HelixGeom_HelixCurve(helix)
    res_c0, bspl_c0, _ = HelixGeom_Tools.ApprCurve3D_s(h_adaptor, TOL, GeomAbs_C0, 30, 4)
    assert res_c0 == 0
    assert bspl_c0 is not None
    res_c2, bspl_c2, _ = HelixGeom_Tools.ApprCurve3D_s(h_adaptor, TOL, GeomAbs_C2, 30, 6)
    assert res_c2 == 0
    assert bspl_c2 is not None
    assert bspl_c2.Degree() >= bspl_c0.Degree()
