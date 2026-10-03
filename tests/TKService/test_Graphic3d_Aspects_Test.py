# Translated from OCCT src/Visualization/TKService/GTests/Graphic3d_Aspects_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Graphic3d import (
    Graphic3d_AspectFillArea3d,
    Graphic3d_Aspects,
    Graphic3d_MaterialAspect,
    Graphic3d_NameOfMaterial_DEFAULT,
    Graphic3d_NameOfMaterial_Plastified,
    Graphic3d_TOR_AMBIENT,
    Graphic3d_TOR_DIFFUSE,
    Graphic3d_TOR_EMISSION,
    Graphic3d_TOR_SPECULAR,
    Graphic3d_TypeOfShadingModel_DEFAULT,
    Graphic3d_TypeOfShadingModel_Gouraud,
    Graphic3d_TypeOfShadingModel_Pbr,
    Graphic3d_TypeOfShadingModel_PbrFacet,
    Graphic3d_TypeOfShadingModel_Phong,
    Graphic3d_TypeOfShadingModel_PhongFacet,
    Graphic3d_TypeOfShadingModel_Unlit,
)
from nanocct.Quantity import Quantity_Color, Quantity_NOC_AZURE, Quantity_NOC_BLACK


def _zero_material():
    mat = Graphic3d_MaterialAspect()
    black = Quantity_Color(Quantity_NOC_BLACK)
    mat.SetAmbientColor(black)
    mat.SetDiffuseColor(black)
    mat.SetSpecularColor(black)
    mat.SetEmissiveColor(black)
    return mat


def test_Graphic3d_AspectsTest_ShadingModel_Default():
    assert Graphic3d_Aspects().ShadingModel() == Graphic3d_TypeOfShadingModel_DEFAULT


def test_Graphic3d_AspectsTest_ShadingModel_ExplicitUnlit():
    a = Graphic3d_Aspects()
    a.SetShadingModel(Graphic3d_TypeOfShadingModel_Unlit)
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Unlit


def test_Graphic3d_AspectsTest_VertexColorForBackFaces_Default():
    assert Graphic3d_Aspects().ToUseVertexColorForBackFaces()


def test_Graphic3d_AspectsTest_VertexColorForBackFaces_SetterAndEquality():
    a1 = Graphic3d_Aspects()
    a2 = Graphic3d_Aspects()
    assert a1.IsEqual(a2)
    a1.SetUseVertexColorForBackFaces(False)
    assert not a1.ToUseVertexColorForBackFaces()
    assert not a1.IsEqual(a2)
    a2.SetUseVertexColorForBackFaces(False)
    assert a1.IsEqual(a2)


def test_Graphic3d_AspectsTest_VertexColorForBackFaces_FillAreaAspect():
    a = Graphic3d_AspectFillArea3d()
    assert a.ToUseVertexColorForBackFaces()
    a.SetUseVertexColorForBackFaces(False)
    assert not a.ToUseVertexColorForBackFaces()


def test_Graphic3d_AspectsTest_ShadingModel_IndependentOfMaterial():
    a = Graphic3d_Aspects()
    a.SetShadingModel(Graphic3d_TypeOfShadingModel_Phong)
    a.SetFrontMaterial(_zero_material())
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Phong


def test_Graphic3d_AspectsTest_ShadingModel_AllValues():
    a = Graphic3d_Aspects()
    for model in (
        Graphic3d_TypeOfShadingModel_Unlit,
        Graphic3d_TypeOfShadingModel_PhongFacet,
        Graphic3d_TypeOfShadingModel_Gouraud,
        Graphic3d_TypeOfShadingModel_Phong,
        Graphic3d_TypeOfShadingModel_Pbr,
        Graphic3d_TypeOfShadingModel_PbrFacet,
    ):
        a.SetShadingModel(model)
        assert a.ShadingModel() == model


def test_Graphic3d_AspectsTest_ShadingModel_ExplicitUnlitWithColor():
    a = Graphic3d_Aspects()
    a.SetShadingModel(Graphic3d_TypeOfShadingModel_Unlit)
    a.SetInteriorColor(Quantity_Color(Quantity_NOC_AZURE))
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Unlit
    assert a.InteriorColor() == Quantity_Color(Quantity_NOC_AZURE)


def test_Graphic3d_AspectsTest_ShadingModel_SurvivesMaterialChange():
    a = Graphic3d_AspectFillArea3d()
    a.SetShadingModel(Graphic3d_TypeOfShadingModel_Phong)
    a.SetFrontMaterial(Graphic3d_MaterialAspect(Graphic3d_NameOfMaterial_Plastified))
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Phong
    a.SetBackMaterial(Graphic3d_MaterialAspect(Graphic3d_NameOfMaterial_DEFAULT))
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Phong
    a.SetFrontMaterial(_zero_material())
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Phong


def test_Graphic3d_AspectsTest_ShadingModel_SetAfterMaterial():
    a = Graphic3d_AspectFillArea3d()
    a.SetFrontMaterial(Graphic3d_MaterialAspect(Graphic3d_NameOfMaterial_Plastified))
    a.SetShadingModel(Graphic3d_TypeOfShadingModel_Unlit)
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Unlit


def test_Graphic3d_AspectsTest_ReflectionMode_IndependentOfShadingModel():
    a = Graphic3d_Aspects()
    a.SetShadingModel(Graphic3d_TypeOfShadingModel_Phong)
    a.SetFrontMaterial(_zero_material())
    stored = a.FrontMaterial()
    assert not stored.ReflectionMode(Graphic3d_TOR_AMBIENT)
    assert not stored.ReflectionMode(Graphic3d_TOR_DIFFUSE)
    assert not stored.ReflectionMode(Graphic3d_TOR_SPECULAR)
    assert not stored.ReflectionMode(Graphic3d_TOR_EMISSION)
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Phong


def test_Graphic3d_AspectsTest_ShadingModel_PbrNotAffectedByPhongMaterial():
    a = Graphic3d_Aspects()
    a.SetShadingModel(Graphic3d_TypeOfShadingModel_Pbr)
    a.SetFrontMaterial(_zero_material())
    assert a.ShadingModel() == Graphic3d_TypeOfShadingModel_Pbr
