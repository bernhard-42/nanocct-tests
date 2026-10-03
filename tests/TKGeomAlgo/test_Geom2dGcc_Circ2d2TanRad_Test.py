# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dGcc_Circ2d2TanRad_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GccEnt import GccEnt_outside
from nanocct.Geom2d import Geom2d_BezierCurve, Geom2d_Line
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dGcc import Geom2dGcc_Circ2d2TanRad, Geom2dGcc_QualifiedCurve
from nanocct.gp import gp_Dir2d, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1


def test_Geom2dGcc_Circ2d2TanRadTest_BUC60897_TangentToLineAndBezier():
    line = Geom2d_Line(gp_Pnt2d(100, 0), gp_Dir2d(gp_Dir2d.D.NX))
    pts = NCollection_Array1[gp_Pnt2d](1, 3)
    pts.SetValue(1, gp_Pnt2d(0, 0))
    pts.SetValue(2, gp_Pnt2d(50, 50))
    pts.SetValue(3, gp_Pnt2d(0, 100))
    curve = Geom2d_BezierCurve(pts)

    c_line = Geom2dAdaptor_Curve(line)
    c_curve = Geom2dAdaptor_Curve(curve)
    q1 = Geom2dGcc_QualifiedCurve(c_line, GccEnt_outside)
    q2 = Geom2dGcc_QualifiedCurve(c_curve, GccEnt_outside)

    gcc = Geom2dGcc_Circ2d2TanRad(q1, q2, 10.0, 1e-7)
    assert gcc.IsDone()
    assert gcc.NbSolutions() > 0
    for i in range(1, gcc.NbSolutions() + 1):
        circ = gcc.ThisSolution(i)
        center = circ.Location()
        r = circ.Radius()
        p1, p2 = gp_Pnt2d(), gp_Pnt2d()
        gcc.Tangency1(i, p1)
        gcc.Tangency2(i, p2)
        assert abs(p1.Distance(center) - r) / r * 100.0 <= 1.0
        assert abs(p2.Distance(center) - r) / r * 100.0 <= 1.0
