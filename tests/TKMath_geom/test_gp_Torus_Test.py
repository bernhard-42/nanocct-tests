# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Torus_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_ToroidalSurface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1


def test_gp_TorusTest_OCC26746_CoefficientsCorrect():
    ax3 = gp_Ax3(
        gp_Pnt(55.52514413, 2.070076585, 73.83409062),
        gp_Dir(0.37231784651136368, 0.58886674834874120, 0.71736697293527607),
        gp_Dir(0.80682335496555135, 0.17666016102759910, -0.56376170618524390),
    )
    torus = Geom_ToroidalSurface(ax3, 87.08479625, 23.14682176)
    tol = 3.0e-7
    nb = 5
    low = 5
    step = 2.0 * math.pi / nb
    coeffs = NCollection_Array1[float](low, low + 34)
    coeffs.Init(0.0)
    torus.Torus().Coefficients(coeffs)
    c = [coeffs.Value(i) for i in range(low, low + 35)]

    u = 0.0
    for ui in range(nb + 1):
        v = 0.0
        for vi in range(nb + 1):
            pt = torus.Value(u, v)
            x, y, z = pt.X(), pt.Y(), pt.Z()
            terms = [
                x**4, y**4, z**4, x**3 * y, x**3 * z, y**3 * x, y**3 * z, z**3 * x, z**3 * y,
                x**2 * y**2, x**2 * z**2, y**2 * z**2, x**2 * y * z, x * y**2 * z, x * y * z**2,
                x**3, y**3, z**3, x**2 * y, x**2 * z, y**2 * x, y**2 * z, z**2 * x, z**2 * y,
                x * y * z, x**2, y**2, z**2, x * y, x * z, y * z, x, y, z, 1.0,
            ]
            delta = 0.0
            for ci, t in zip(c, terms):
                delta += ci * t
            assert abs(delta) <= tol, (u, v, delta)
            v = 2.0 * math.pi if vi == nb else v + step
        u = 2.0 * math.pi if ui == nb else u + step
