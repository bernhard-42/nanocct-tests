# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntCurveSurface_ThePolyhedronOfHInter_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_Plane
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_XYZ
from nanocct.IntCurveSurface import IntCurveSurface_ThePolyhedronOfHInter
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import Standard_OutOfRange


def _plane():
    return GeomAdaptor_Surface(Geom_Plane(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))), -1.0, 1.0, -1.0, 1.0)


def _arr(values):
    a = NCollection_Array1[float](1, len(values))
    for i, v in enumerate(values, 1):
        a.SetValue(i, v)
    return a


def test_IntCurveSurface_ThePolyhedronOfHInter_SingularityFlags_InitializedFalse():
    surf = _plane()
    poly = IntCurveSurface_ThePolyhedronOfHInter(surf, 3, 3, -1.0, -1.0, 1.0, 1.0)
    assert not poly.HasUMinSingularity()
    assert not poly.HasUMaxSingularity()
    assert not poly.HasVMinSingularity()
    assert not poly.HasVMaxSingularity()


def test_IntCurveSurface_ThePolyhedronOfHInter_SingularitySetters_UpdateFlags():
    surf = _plane()
    poly = IntCurveSurface_ThePolyhedronOfHInter(surf, 3, 3, -1.0, -1.0, 1.0, 1.0)
    poly.UMinSingularity(True)
    assert poly.HasUMinSingularity()
    assert not poly.HasUMaxSingularity()
    poly.VMaxSingularity(True)
    assert poly.HasVMaxSingularity()
    assert not poly.HasVMinSingularity()


def test_IntCurveSurface_ThePolyhedronOfHInter_BasicConstruction_ValidMesh():
    surf = _plane()
    poly = IntCurveSurface_ThePolyhedronOfHInter(surf, 4, 4, -1.0, -1.0, 1.0, 1.0)
    nb_u, nb_v = poly.Size()
    assert nb_u == 4
    assert nb_v == 4
    assert poly.NbTriangles() == 4 * 4 * 2
    assert poly.NbPoints() == 5 * 5


def test_IntCurveSurface_ThePolyhedronOfHInter_ParamArrayConstructor_MinimumSize():
    surf = _plane()
    upars = _arr([-1.0, 1.0])
    vpars = _arr([-1.0, 1.0])
    poly = IntCurveSurface_ThePolyhedronOfHInter(surf, upars, vpars)
    nb_u, nb_v = poly.Size()
    assert nb_u >= 1
    assert nb_v >= 1
    assert poly.NbTriangles() > 0


def test_IntCurveSurface_ThePolyhedronOfHInter_ParamArrayConstructor_RejectsSingleValueArrays():
    surf = _plane()
    single = _arr([0.0])
    valid = _arr([-1.0, 1.0])
    with pytest.raises(Standard_OutOfRange):
        IntCurveSurface_ThePolyhedronOfHInter(surf, single, valid)
    with pytest.raises(Standard_OutOfRange):
        IntCurveSurface_ThePolyhedronOfHInter(surf, valid, single)


def test_IntCurveSurface_ThePolyhedronOfHInter_PlaneEquation_FiniteResults():
    surf = _plane()
    poly = IntCurveSurface_ThePolyhedronOfHInter(surf, 3, 3, -1.0, -1.0, 1.0, 1.0)
    normal = gp_XYZ()
    polar = poly.PlaneEquation(1, normal)
    assert math.isfinite(normal.X())
    assert math.isfinite(normal.Y())
    assert math.isfinite(normal.Z())
    assert math.isfinite(polar)
