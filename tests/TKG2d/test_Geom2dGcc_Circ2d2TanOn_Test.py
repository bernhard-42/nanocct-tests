# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dGcc_Circ2d2TanOn_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GccEnt import GccEnt_unqualified
from nanocct.Geom2d import Geom2d_BezierCurve, Geom2d_Line
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dAPI import Geom2dAPI_ProjectPointOnCurve
from nanocct.Geom2dGcc import Geom2dGcc_Circ2d2TanOn, Geom2dGcc_QualifiedCurve
from nanocct.gp import gp_Dir2d, gp_Pnt2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1


def test_Geom2dGcc_Circ2d2TanOn_Test_OCC27357_NoExceptions():
    poles = NCollection_Array1[gp_Pnt2d](1, 3)
    poles.SetValue(1, gp_Pnt2d(0.0, 0.0))
    poles.SetValue(2, gp_Pnt2d(0.0, 1.0))
    poles.SetValue(3, gp_Pnt2d(6.0, 0.0))
    c1 = Geom2d_BezierCurve(poles)
    poles.SetValue(2, gp_Pnt2d(0.0, 1.5))
    c2 = Geom2d_BezierCurve(poles)
    results = []
    n = 100
    for i in range(n):
        u = i / (n - 1.0)
        p1, tangent = gp_Pnt2d(), gp_Vec2d()
        c1.D1(u, p1, tangent)
        normal = gp_Vec2d(-tangent.Y(), tangent.X())
        nline = Geom2d_Line(p1, gp_Dir2d(normal))
        q1 = Geom2dGcc_QualifiedCurve(Geom2dAdaptor_Curve(c1), GccEnt_unqualified)
        q2 = Geom2dGcc_QualifiedCurve(Geom2dAdaptor_Curve(c2), GccEnt_unqualified)
        g1 = Geom2dAPI_ProjectPointOnCurve(p1, c1).LowerDistanceParameter()
        g3 = Geom2dAPI_ProjectPointOnCurve(p1, nline).LowerDistanceParameter()
        builder = Geom2dGcc_Circ2d2TanOn(q1, q2, Geom2dAdaptor_Curve(nline), 1e-9, g1, g1, g3)
        results.append(builder.NbSolutions())
    assert len(results) == n
