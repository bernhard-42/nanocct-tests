# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dGcc_Lin2d2Tan_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GccEnt import GccEnt_outside
from nanocct.Geom import Geom_Circle, Geom_Ellipse, Geom_Plane
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dGcc import Geom2dGcc_Lin2d2Tan, Geom2dGcc_QualifiedCurve
from nanocct.GeomAPI import GeomAPI
from nanocct.gp import gp_Ax2, gp_Ax3, gp_Dir, gp_Pnt, gp_Pnt2d


def _ax2():
    return gp_Ax2(gp_Pnt(1262.224429, 425.040878, 363.609716), gp_Dir(0.173648, 0.984808, 0.000000),
                  gp_Dir(-0.932169, 0.164367, -0.322560))


def test_Geom2dGcc_Lin2d2TanTest_OCC813_EllipseAndPoint():
    ax2 = _ax2()
    ell = Geom_Ellipse(ax2, 150, 100)
    pln = Geom_Plane(gp_Ax3(ax2)).Pln()
    c2d = GeomAPI.To2d_s(ell, pln)
    adapt = Geom2dAdaptor_Curve(c2d)
    q = Geom2dGcc_QualifiedCurve(adapt, GccEnt_outside)
    lin_tan = Geom2dGcc_Lin2d2Tan(q, gp_Pnt2d(200.0, 200.0), 0.1)
    assert lin_tan.NbSolutions() > 0


def test_Geom2dGcc_Lin2d2TanTest_OCC814_CircleAndEllipse():
    ax2 = _ax2()
    cir = Geom_Circle(gp_Ax2(gp_Pnt(823.687192, 502.366825, 478.960440), gp_Dir(0.173648, 0.984808, 0.000000),
                             gp_Dir(-0.932169, 0.164367, -0.322560)), 50)
    ell = Geom_Ellipse(ax2, 150, 100)
    pln = Geom_Plane(gp_Ax3(ax2)).Pln()
    a_ell = Geom2dAdaptor_Curve(GeomAPI.To2d_s(ell, pln))
    a_cir = Geom2dAdaptor_Curve(GeomAPI.To2d_s(cir, pln))
    q_ell = Geom2dGcc_QualifiedCurve(a_ell, GccEnt_outside)
    q_cir = Geom2dGcc_QualifiedCurve(a_cir, GccEnt_outside)
    lin_tan = Geom2dGcc_Lin2d2Tan(q_ell, q_cir, 0.1)
    assert lin_tan.NbSolutions() > 0
