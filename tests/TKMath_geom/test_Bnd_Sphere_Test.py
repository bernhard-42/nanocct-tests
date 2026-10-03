# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_Sphere_Test.cxx (LGPL-2.1 with the OCCT exception)

import pytest

from nanocct.Bnd import Bnd_Sphere
from nanocct.gp import gp_XYZ

ORIGIN = (0.0, 0.0, 0.0)


def sphere(center, radius, u=0, v=0):
    return Bnd_Sphere(gp_XYZ(*center), radius, u, v)


def test_Bnd_SphereTest_DefaultConstructor():
    aSphere = Bnd_Sphere()
    c = aSphere.Center()
    assert (c.X(), c.Y(), c.Z()) == (0.0, 0.0, 0.0)
    assert aSphere.Radius() == 0.0
    assert aSphere.IsValid() is False
    assert aSphere.U() == 0
    assert aSphere.V() == 0


def test_Bnd_SphereTest_ParameterizedConstructor():
    aSphere = sphere((1.0, 2.0, 3.0), 5.0, 10, 20)
    c = aSphere.Center()
    assert (c.X(), c.Y(), c.Z()) == (1.0, 2.0, 3.0)
    assert aSphere.Radius() == 5.0
    assert aSphere.U() == 10
    assert aSphere.V() == 20


def test_Bnd_SphereTest_Validity():
    aSphere = Bnd_Sphere()
    assert aSphere.IsValid() is False
    aSphere.SetValid(True)
    assert aSphere.IsValid() is True
    aSphere.SetValid(False)
    assert aSphere.IsValid() is False


def test_Bnd_SphereTest_Distance():
    assert sphere(ORIGIN, 1.0).Distance(gp_XYZ(3.0, 4.0, 0.0)) == 5.0


def test_Bnd_SphereTest_SquareDistance():
    assert sphere(ORIGIN, 1.0).SquareDistance(gp_XYZ(3.0, 4.0, 0.0)) == 25.0


def test_Bnd_SphereTest_Distances_PointOutside():
    assert sphere(ORIGIN, 2.0).Distances(gp_XYZ(5.0, 0.0, 0.0)) == (3.0, 7.0)


def test_Bnd_SphereTest_Distances_PointInside():
    assert sphere(ORIGIN, 5.0).Distances(gp_XYZ(1.0, 0.0, 0.0)) == (0.0, 6.0)


def test_Bnd_SphereTest_SquareDistances_PointOutside():
    assert sphere(ORIGIN, 2.0).SquareDistances(gp_XYZ(5.0, 0.0, 0.0)) == (21.0, 29.0)


def test_Bnd_SphereTest_SquareDistances_PointInside():
    assert sphere(ORIGIN, 5.0).SquareDistances(gp_XYZ(1.0, 0.0, 0.0)) == (0.0, 26.0)


def test_Bnd_SphereTest_SquareDistances_PointAtCenter():
    assert sphere(ORIGIN, 3.0).SquareDistances(gp_XYZ(0.0, 0.0, 0.0)) == (0.0, 9.0)


def test_Bnd_SphereTest_SquareDistances_PointOnSurface():
    assert sphere(ORIGIN, 3.0).SquareDistances(gp_XYZ(3.0, 0.0, 0.0)) == (0.0, 18.0)


def test_Bnd_SphereTest_Project():
    aSphere = sphere((1.0, 2.0, 3.0), 5.0)
    aProjNode = gp_XYZ()
    isOk, aDist, anInside = aSphere.Project(gp_XYZ(10.0, 20.0, 30.0), aProjNode)
    assert isOk is True
    assert anInside is True
    assert (aProjNode.X(), aProjNode.Y(), aProjNode.Z()) == (1.0, 2.0, 3.0)


def test_Bnd_SphereTest_Add_EnclosingSphere():
    aSphere1 = sphere(ORIGIN, 10.0)
    aSphere1.Add(sphere((1.0, 0.0, 0.0), 2.0))
    assert aSphere1.Radius() == 10.0


def test_Bnd_SphereTest_Add_EnclosedBySphere():
    aSphere1 = sphere(ORIGIN, 2.0)
    aSphere1.Add(sphere(ORIGIN, 10.0))
    assert aSphere1.Radius() == 10.0


def test_Bnd_SphereTest_Add_PartialOverlap():
    aSphere1 = sphere(ORIGIN, 3.0)
    aSphere1.Add(sphere((5.0, 0.0, 0.0), 3.0))
    assert aSphere1.Radius() == 5.5


def test_Bnd_SphereTest_IsOut_Separated():
    assert sphere(ORIGIN, 1.0).IsOut(sphere((10.0, 0.0, 0.0), 1.0)) is True


def test_Bnd_SphereTest_IsOut_Overlapping():
    assert sphere(ORIGIN, 3.0).IsOut(sphere((4.0, 0.0, 0.0), 3.0)) is False


# Bnd_Sphere::IsOut(const gp_XYZ&, double& theMaxDist) reads theMaxDist before updating it
# (Bnd_Sphere.cxx:113), so it is in/out; the binding treats it as a pure out-parameter.
# Written in the R-INOUT form (parameter kept and returned).
def test_Bnd_SphereTest_IsOut_PointWithMaxDist():
    aSphere = sphere(ORIGIN, 5.0)
    aSphere.SetValid(True)
    isOut, aMaxDist = aSphere.IsOut(gp_XYZ(20.0, 0.0, 0.0), 100.0)
    assert isOut is False
    assert aMaxDist == 25.0


def test_Bnd_SphereTest_IsOut_PointTooFar():
    aSphere = sphere(ORIGIN, 1.0)
    isOut, _ = aSphere.IsOut(gp_XYZ(20.0, 0.0, 0.0), 10.0)
    assert isOut is True


def test_Bnd_SphereTest_SquareExtent():
    assert sphere(ORIGIN, 3.0).SquareExtent() == 36.0
