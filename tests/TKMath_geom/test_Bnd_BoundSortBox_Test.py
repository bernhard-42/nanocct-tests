# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_BoundSortBox_Test.cxx (LGPL-2.1 with the OCCT exception)

import pytest

from nanocct.Bnd import Bnd_BoundSortBox, Bnd_Box
from nanocct.BRepBndLib import BRepBndLib
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_HArray1
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def CreateBox(xmin, ymin, zmin, xmax, ymax, zmax):
    box = Bnd_Box()
    box.Update(xmin, ymin, zmin, xmax, ymax, zmax)
    return box


def harray(*boxes):
    arr = NCollection_HArray1[Bnd_Box](1, len(boxes))
    for i, b in enumerate(boxes, start=1):
        arr.SetValue(i, b)
    return arr


class Fixture:
    def __init__(self):
        self.mySmallBox = CreateBox(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.myLargeBox = CreateBox(-10.0, -10.0, -10.0, 10.0, 10.0, 10.0)
        self.myOffsetBox = CreateBox(5.0, 5.0, 5.0, 7.0, 7.0, 7.0)
        self.myNonIntersectingBox = CreateBox(20.0, 20.0, 20.0, 30.0, 30.0, 30.0)
        self.myBoxes = harray(self.mySmallBox, self.myLargeBox, self.myOffsetBox, self.myNonIntersectingBox)
        self.myGlobalBox = CreateBox(-20.0, -20.0, -20.0, 40.0, 40.0, 40.0)


@pytest.fixture
def f():
    return Fixture()


def test_Bnd_BoundSortBoxTest_InitializeWithBoxes(f):
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(f.myBoxes)
    result = sortBox.Compare(CreateBox(0.5, 0.5, 0.5, 1.5, 1.5, 1.5))
    assert result.Extent() == 2
    values = list(result)
    assert 1 in values
    assert 2 in values


def test_Bnd_BoundSortBoxTest_InitializeWithEnclosingBox(f):
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(f.myGlobalBox, f.myBoxes)
    result = sortBox.Compare(f.myOffsetBox)
    assert result.Extent() == 2
    values = list(result)
    assert 2 in values
    assert 3 in values


def test_Bnd_BoundSortBoxTest_InitializeWithCount(f):
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(f.myGlobalBox, 3)
    sortBox.Add(f.mySmallBox, 1)
    sortBox.Add(f.myLargeBox, 2)
    sortBox.Add(f.myNonIntersectingBox, 3)
    result = sortBox.Compare(CreateBox(-5.0, -5.0, -5.0, -2.0, -2.0, -2.0))
    assert result.Extent() == 1
    assert result.First() == 2


def test_Bnd_BoundSortBoxTest_CompareWithPlane(f):
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(f.myBoxes)
    plane = gp_Pln(gp_Pnt(0.0, 0.0, 9.0), gp_Dir(0.0, 0.0, 1.0))
    result = sortBox.Compare(plane)
    assert result.Extent() == 1
    assert result.First() == 2


def test_Bnd_BoundSortBoxTest_VoidBoxes(f):
    void_box = Bnd_Box()
    boxes = harray(void_box, f.mySmallBox)
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(boxes)
    result = sortBox.Compare(f.mySmallBox)
    assert result.Extent() == 1
    assert result.First() == 2
    assert sortBox.Compare(void_box).Extent() == 0


def test_Bnd_BoundSortBoxTest_TouchingBoxes():
    box1 = CreateBox(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box2 = CreateBox(1.0, 1.0, 1.0, 2.0, 2.0, 2.0)
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(harray(box1, box2))
    assert sortBox.Compare(box1).Extent() == 2
    assert sortBox.Compare(box2).Extent() == 2


def test_Bnd_BoundSortBoxTest_DisjointBoxes(f):
    farBox = CreateBox(100.0, 100.0, 100.0, 110.0, 110.0, 110.0)
    enclosingBox = CreateBox(-10.0, -10.0, -10.0, 120.0, 120.0, 120.0)
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(enclosingBox, harray(f.mySmallBox, farBox))
    result = sortBox.Compare(CreateBox(0.5, 0.5, 0.5, 1.5, 1.5, 1.5))
    assert result.Extent() == 1
    assert result.First() == 1


def test_Bnd_BoundSortBoxTest_DegenerateBoxes():
    pointBox = CreateBox(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    lineBox = CreateBox(2.0, 0.0, 0.0, 5.0, 0.0, 0.0)
    planeBox = CreateBox(0.0, 0.0, 3.0, 3.0, 3.0, 3.0)
    sortBox = Bnd_BoundSortBox()
    sortBox.Initialize(harray(pointBox, lineBox, planeBox))
    assert sortBox.Compare(CreateBox(0.0, 0.0, 0.0, 6.0, 6.0, 6.0)).Extent() == 3
    pointResult = sortBox.Compare(CreateBox(0.5, 0.5, 0.5, 1.5, 1.5, 1.5))
    assert pointResult.Extent() == 1
    assert pointResult.First() == 1


def test_Bnd_BoundSortBox_Test_BUC60729_InitializeWithFaceBoxes():
    aShape = BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Solid()
    aMainBox = Bnd_Box()
    BRepBndLib.Add_s(aShape, aMainBox)
    aBoundSortBox = Bnd_BoundSortBox()
    aBoundSortBox.Initialize(aMainBox, 6)
    aExplorer = TopExp_Explorer(aShape, TopAbs_FACE)
    i = 1
    while aExplorer.More():
        aBox = Bnd_Box()
        BRepBndLib.Add_s(aExplorer.Current(), aBox)
        aBoundSortBox.Add(aBox, i)
        aExplorer.Next()
        i += 1
    assert i == 7
