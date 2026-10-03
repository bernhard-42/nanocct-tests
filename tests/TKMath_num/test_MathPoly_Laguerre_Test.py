# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathPoly_Laguerre_Test.cxx (LGPL-2.1 with the OCCT exception)
# MathPoly::Laguerre(const double*, int) is not bound (raw pointer); only Quintic, Sextic and Octic are.
from nanocct import MathPoly

THE_TOL = 1.0e-10


def test_MathPoly_LaguerreTest_Quintic_FiveDistinctRoots():
    res = MathPoly.Quintic(1.0, -15.0, 85.0, -225.0, 274.0, -120.0)
    assert res.IsDone()
    assert res.NbRoots == 4  # PolyResult has max 4 roots
    roots = res.Roots
    for i in range(res.NbRoots):
        assert any(abs(roots[i] - e) < THE_TOL for e in (1.0, 2.0, 3.0, 4.0, 5.0)), roots[i]


def test_MathPoly_LaguerreTest_Sextic_SixDistinctRoots():
    res = MathPoly.Sextic(1.0, -21.0, 175.0, -735.0, 1624.0, -1764.0, 720.0)
    assert res.IsDone()
    assert res.NbRoots == 4  # PolyResult has max 4 roots
    roots = res.Roots
    for i in range(res.NbRoots):
        assert any(abs(roots[i] - e) < THE_TOL for e in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)), roots[i]


def test_MathPoly_LaguerreTest_Octic_EightDistinctRoots():
    coeffs = [40320.0, -109584.0, 118124.0, -67284.0, 22449.0, -4536.0, 546.0, -36.0, 1.0]
    res = MathPoly.Octic(coeffs)
    assert res.IsDone()
    assert res.NbRoots == 8
    roots = res.Roots
    for i in range(res.NbRoots):
        assert abs(roots[i] - float(i + 1)) <= 1.0e-6, (i, roots[i])
