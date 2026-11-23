# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepData_StepReaderData_Test.cxx (LGPL-2.1 with the OCCT exception)
import io

from nanocct.IFSelect import IFSelect_RetDone
from nanocct.STEPControl import STEPControl_Reader
from nanocct.StepGeom import StepGeom_Direction
from nanocct.StepVisual import StepVisual_StyledItem


def test_StepData_StepReaderDataTest_ReadEntity_UnresolvedReferenceDoesNotBindRecord():
    for reference in (11, 999, 10):
        text = ("ISO-10303-21;\nHEADER;\n"
                "FILE_DESCRIPTION(('Unresolved reference'),'2;1');\n"
                "FILE_NAME('reference.stp','',(''),(''),'','','');\n"
                "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n"
                "#10=DIRECTION('',(0.,0.,1.));\n"
                "#20=DIRECTION('',(1.,0.,0.));\n"
                "#30=COLOUR_RGB('',1.,0.,0.);\n"
                "#40=FILL_AREA_STYLE_COLOUR('',#30);\n"
                "#50=FILL_AREA_STYLE('',(#40));\n"
                "#60=SURFACE_STYLE_FILL_AREA(#50);\n"
                "#70=SURFACE_SIDE_STYLE('',(#60));\n"
                "#80=SURFACE_STYLE_USAGE(.BOTH.,#70);\n"
                "#90=PRESENTATION_STYLE_ASSIGNMENT((#80));\n"
                f"#100=STYLED_ITEM('color',(#90),#{reference});\nENDSEC;\nEND-ISO-10303-21;\n")
        reader = STEPControl_Reader()
        assert reader.ReadStream("reference.stp", io.StringIO(text)) == IFSelect_RetDone, reference
        model = reader.StepModel()
        styled_items = 0
        for i in range(1, model.NbEntities() + 1):
            styled = model.Value(i)
            if isinstance(styled, StepVisual_StyledItem) is False:
                continue
            styled_items += 1
            if reference == 10:
                direction = styled.Item()
                assert isinstance(direction, StepGeom_Direction), reference
                assert model.IdentLabel(direction) == 10
            else:
                assert styled.Item() is None, reference
        assert styled_items == 1, reference
