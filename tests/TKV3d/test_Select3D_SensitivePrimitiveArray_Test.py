# Translated from OCCT src/Visualization/TKV3d/GTests/Select3D_SensitivePrimitiveArray_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Graphic3d import Graphic3d_ArrayOfTriangles
from nanocct.Precision import Precision
from nanocct.Select3D import Select3D_SensitivePrimitiveArray
from nanocct.SelectMgr import SelectMgr_EntityOwner
from nanocct.TopLoc import TopLoc_Location


def test_Select3D_SensitivePrimitiveArrayTest_GetVertex_ReturnsTriangleVertices():
    tris = Graphic3d_ArrayOfTriangles(3)
    tris.AddVertex(0.0, 0.0, 0.0)
    tris.AddVertex(1.0, 0.0, 0.0)
    tris.AddVertex(0.0, 1.0, 0.0)

    owner = SelectMgr_EntityOwner()
    sens = Select3D_SensitivePrimitiveArray(owner)
    assert sens.InitTriangulation(tris.Attributes(), tris.Indices(), TopLoc_Location())

    verts = sens.GetVertex(0)
    assert len(verts) == 3
    tol = Precision.Confusion_s()
    expected = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    for v, (x, y, z) in zip(verts, expected):
        assert abs(v.x() - x) <= tol
        assert abs(v.y() - y) <= tol
        assert abs(v.z() - z) <= tol
