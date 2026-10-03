# Translated from OCCT src/ApplicationFramework/TKLCAF/GTests/TDataStd_TreeNode_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.TDataStd import TDataStd_TreeNode
from nanocct.TDF import TDF_Data


def test_TDataStd_TreeNode_Test_BUC60817_DescendantRelationship():
    df = TDF_Data()
    label1 = df.Root().FindChild(2, True)
    label2 = df.Root().FindChild(3, True)
    tn1 = TDataStd_TreeNode.Set_s(label1)
    tn2 = TDataStd_TreeNode.Set_s(label2)
    tn1.Append(tn2)
    assert tn2.IsDescendant(tn1)
    assert not tn1.IsDescendant(tn2)
