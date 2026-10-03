# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dGcc_Circ2d2TanRad_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GccEnt import GccEnt_unqualified
from nanocct.Geom2d import Geom2d_Ellipse
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dGcc import Geom2dGcc_Circ2d2TanRad, Geom2dGcc_QualifiedCurve
from nanocct.gp import gp, gp_Ax2d, gp_Circ2d, gp_Elips2d, gp_Pnt2d


def test_Geom2dGcc_Circ2d2TanRad_Test_OCC24303_CircleTangentToTwoEllipses():
    p0, p1 = gp_Pnt2d(gp.Origin2d_s()), gp_Pnt2d(4.0, 0.0)
    e1 = gp_Elips2d(gp_Ax2d(p0, gp.DX2d_s()), 2.0, 1.0, True)
    e2 = gp_Elips2d(gp_Ax2d(p1, gp.DX2d_s()), 2.0, 1.0, True)
    c1, c2 = Geom2d_Ellipse(e1), Geom2d_Ellipse(e2)
    radius = 3.0
    theo = gp_Circ2d(gp_Ax2d(gp_Pnt2d(5.0, 0.0), gp.DX2d_s()), radius)
    q1 = Geom2dGcc_QualifiedCurve(Geom2dAdaptor_Curve(c1), GccEnt_unqualified)
    q2 = Geom2dGcc_QualifiedCurve(Geom2dAdaptor_Curve(c2), GccEnt_unqualified)
    calc = Geom2dGcc_Circ2d2TanRad(q1, q2, radius, 1.0e-9)
    nb = calc.NbSolutions()
    assert nb > 0
    for i in range(1, nb + 1):
        assert abs(radius - calc.ThisSolution(i).Radius()) <= 1.0e-6
    if nb > 0:
        assert theo.Location().Distance(calc.ThisSolution(1).Location()) < 10.0
