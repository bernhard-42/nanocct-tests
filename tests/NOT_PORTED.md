# OCCT GTests not ported

C++ GTest files of OCCT 8.0.2 that have no Python port here, each with the reason. A file whose cases are only partly portable has a port, and its header names every case it does not translate, with the reason. Rows marked **pending** wait for a binding fix in nanocct and get ported once it is in.

| C++ test file | Cases | Why it is not ported |
|---|---|---|
| `src/ApplicationFramework/TKTObj/GTests/TObj_Model_Test.cxx` | 41 | TKTObj is out of scope (nanocct docs/Design.md); its fixture subclasses abstract classes |
| `src/DataExchange/TKDESTEP/GTests/StepTidy_Axis2Placement3dReducer_Test.cxx` | 14 | the private reducer header (`.pxx`) through a test-only fixture; not installed, not bound (only `StepTidy_DuplicateCleaner` is public) |
| `src/DataExchange/TKDESTEP/GTests/StepTidy_CartesianPointReducer_Test.cxx` | 13 | the private reducer header (`.pxx`) through a test-only fixture; not installed, not bound (only `StepTidy_DuplicateCleaner` is public) |
| `src/DataExchange/TKDESTEP/GTests/StepTidy_CircleReducer_Test.cxx` | 4 | the private reducer header (`.pxx`) through a test-only fixture; not installed, not bound (only `StepTidy_DuplicateCleaner` is public) |
| `src/DataExchange/TKDESTEP/GTests/StepTidy_DirectionReducer_Test.cxx` | 4 | the private reducer header (`.pxx`) through a test-only fixture; not installed, not bound (only `StepTidy_DuplicateCleaner` is public) |
| `src/DataExchange/TKDESTEP/GTests/StepTidy_LineReducer_Test.cxx` | 6 | the private reducer header (`.pxx`) through a test-only fixture; not installed, not bound (only `StepTidy_DuplicateCleaner` is public) |
| `src/DataExchange/TKDESTEP/GTests/StepTidy_PlaneReducer_Test.cxx` | 3 | the private reducer header (`.pxx`) through a test-only fixture; not installed, not bound (only `StepTidy_DuplicateCleaner` is public) |
| `src/DataExchange/TKDESTEP/GTests/StepTidy_VectorReducer_Test.cxx` | 2 | the private reducer header (`.pxx`) through a test-only fixture; not installed, not bound (only `StepTidy_DuplicateCleaner` is public) |
| `src/FoundationClasses/TKMath/GTests/BVH_BinnedBuilder_Test.cxx` | 14 | a class template that no bound OCCT signature instantiates (nanocct binds templates per used instantiation, docs/Excluded.md); **pending: no BVH builder can be constructed although bound setters take one** |
| `src/FoundationClasses/TKMath/GTests/BVH_LinearBuilder_Test.cxx` | 15 | a class template that no bound OCCT signature instantiates (nanocct binds templates per used instantiation, docs/Excluded.md); **pending: as BVH_BinnedBuilder** |
| `src/FoundationClasses/TKMath/GTests/BVH_QuickSorter_Test.cxx` | 13 | a class template that no bound OCCT signature instantiates (nanocct binds templates per used instantiation, docs/Excluded.md) (`BVH_QuickSorter`, `BVH_Triangulation<double,3>`) |
| `src/FoundationClasses/TKMath/GTests/BVH_Ray_Test.cxx` | 19 | a class template that no bound OCCT signature instantiates (nanocct binds templates per used instantiation, docs/Excluded.md) (`BVH_Ray`); one case is `constexpr` |
| `src/FoundationClasses/TKMath/GTests/BVH_SpatialMedianBuilder_Test.cxx` | 15 | a class template that no bound OCCT signature instantiates (nanocct binds templates per used instantiation, docs/Excluded.md) |
| `src/FoundationClasses/TKMath/GTests/BVH_SweepPlaneBuilder_Test.cxx` | 10 | a class template that no bound OCCT signature instantiates (nanocct binds templates per used instantiation, docs/Excluded.md) |
| `src/FoundationClasses/TKMath/GTests/BVH_Tools_Test.cxx` | 45 | a class template that no bound OCCT signature instantiates (nanocct binds templates per used instantiation, docs/Excluded.md) (`BVH_Tools<T,N>`) |
| `src/FoundationClasses/TKMath/GTests/MathInteg_Comparison_Test.cxx` | 21 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) and math_* subclasses for the comparisons |
| `src/FoundationClasses/TKMath/GTests/MathInteg_New_Test.cxx` | 24 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathInteg_Test.cxx` | 34 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathOpt_1D_Comparison_Test.cxx` | 13 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) and math_* subclasses for the comparisons |
| `src/FoundationClasses/TKMath/GTests/MathOpt_1D_Test.cxx` | 25 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathOpt_FRPR_Test.cxx` | 11 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathOpt_GlobOpt_Test.cxx` | 18 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathOpt_NDim_Comparison_Test.cxx` | 12 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) and math_* subclasses for the comparisons |
| `src/FoundationClasses/TKMath/GTests/MathOpt_NDim_Test.cxx` | 13 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathOpt_Newton_Test.cxx` | 12 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathOpt_PSO_Test.cxx` | 22 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathRoot_Comparison_Test.cxx` | 15 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) and math_* subclasses for the comparisons |
| `src/FoundationClasses/TKMath/GTests/MathRoot_Multiple_Test.cxx` | 21 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathRoot_Test.cxx` | 29 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathSys_Comparison_Test.cxx` | 9 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) and math_* subclasses for the comparisons |
| `src/FoundationClasses/TKMath/GTests/MathSys_LM_Test.cxx` | 19 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathSys_Newton2D_Test.cxx` | 9 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathSys_Newton3D_Test.cxx` | 7 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathSys_Newton4D_Test.cxx` | 6 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/MathUtils_Bracket_Test.cxx` | 3 | functor-template algorithms on C++ functors and lambdas (not bound by decision, nanocct docs/Excluded.md, docs/Coverage.md) |
| `src/FoundationClasses/TKMath/GTests/math_BFGS_Test.cxx` | 13 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_BracketedRoot_Test.cxx` | 14 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (`math_Function`) |
| `src/FoundationClasses/TKMath/GTests/math_FRPR_Test.cxx` | 14 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_FunctionAllRoots_Test.cxx` | 16 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_FunctionRoot_Test.cxx` | 12 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_FunctionRoots_Test.cxx` | 15 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_FunctionSetRoot_Test.cxx` | 17 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_GlobOptMin_Test.cxx` | 16 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_Integration_Test.cxx` | 16 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_NewtonFunctionRoot_Test.cxx` | 16 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_NewtonFunctionSetRoot_Test.cxx` | 14 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_NewtonMinimum_Test.cxx` | 15 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_PSO_Test.cxx` | 13 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKMath/GTests/math_Powell_Test.cxx` | 11 | the test's own subclasses of an abstract OCCT class (Python subclasses are not supported: no trampolines, nanocct docs/Excluded.md) (the `math_*` function classes) |
| `src/FoundationClasses/TKernel/GTests/Handle_Advanced_Test.cxx` | 7 | test classes with their own `DEFINE_STANDARD_RTTI` chain and the C++ `occ::handle` template itself (a Python subclass of `Standard_Transient` gets no OCCT type of its own; a handle is the Python object, R-HANDLE); the allocator case would only be a stand-in |
| `src/FoundationClasses/TKernel/GTests/Handle_Operations_Test.cxx` | 7 | as Handle_Advanced: test RTTI classes and `occ::handle`'s own C++ operations |
| `src/FoundationClasses/TKernel/GTests/Message_Messenger_Test.cxx` | 2 | a custom `Message_Printer` subclass (no trampolines) and `operator<<` into `Message_Messenger::StreamBuffer` (a member template) |
| `src/FoundationClasses/TKernel/GTests/NCollection_CellFilter_Test.cxx` | 8 | a custom C++ inspector type as template argument; the bound instantiations take BRepMesh's inspectors |
| `src/FoundationClasses/TKernel/GTests/NCollection_FlatDataMap_Test.cxx` | 40 | no `<int,AsciiString>`/`<int,int>` instantiation; **pending: FlatMap/FlatDataMap are bound generically (no `Seek`, `items()`, `len()`/`in`/iteration; `Items()` raises TypeError) -- port after that fix** |
| `src/FoundationClasses/TKernel/GTests/NCollection_FlatMap_Test.cxx` | 24 | no `<int>`/`<AsciiString>` instantiation; **pending: as NCollection_FlatDataMap** |
| `src/FoundationClasses/TKernel/GTests/NCollection_ForwardRange_Test.cxx` | 22 | C++ templates on mock iterators (SFINAE, range-for, iterator traits); ForwardRange is not bound |
| `src/FoundationClasses/TKernel/GTests/NCollection_KDTree_Test.cxx` | 187 | `NCollection_KDTree` is not bound (docs/Excluded.md); custom point types |
| `src/FoundationClasses/TKernel/GTests/NCollection_LocalArray_Test.cxx` | 32 | the cases use `int` and custom element types, a compile-time size other than the default 1024, move semantics, or the `T*` conversion; nanocct binds only `NCollection_LocalArray<double>` (its `ToArray1()` view is guarded since 2026-11-24), so the 6 cases that do not depend on the element type would need it as a stand-in |
| `src/FoundationClasses/TKernel/GTests/NCollection_OrderedDataMap_Test.cxx` | 47 | `NCollection_OrderedDataMap` is not bound (docs/Excluded.md) |
| `src/FoundationClasses/TKernel/GTests/NCollection_OrderedMap_Test.cxx` | 38 | `NCollection_OrderedMap` is not bound (docs/Excluded.md) |
| `src/FoundationClasses/TKernel/GTests/NCollection_SparseArray_Test.cxx` | 8 | `NCollection_SparseArray` is not bound (docs/Excluded.md); a custom item type |
| `src/FoundationClasses/TKernel/GTests/NCollection_UBTree_Test.cxx` | 16 | Python subclasses of the abstract `UBTree::Selector` (no trampolines) and move semantics; the rest only through a stand-in instantiation |
| `src/FoundationClasses/TKernel/GTests/OSD_Parallel_Test.cxx` | 2 | `OSD_Parallel::For` is a member template on C++ functors |
| `src/FoundationClasses/TKernel/GTests/Standard_ArrayStreamBuffer_Test.cxx` | 20 | not bound: its base `std::streambuf` and the raw char buffer |
| `src/FoundationClasses/TKernel/GTests/Standard_Atomic_Test.cxx` | 1 | `std::atomic` under `OSD_Parallel::For` |
| `src/FoundationClasses/TKernel/GTests/Standard_Handle_Test.cxx` | 1 | the C++ `occ::handle` template (a null handle is `None` in Python) |
| `src/FoundationClasses/TKernel/GTests/Standard_Strtod_Test.cxx` | 4 | 3 cases: `OSD_Parallel::For` with lambdas; the fourth needs `Strtod(const char*, char**)`, whose `char**` out pointer is a raw pointer nanocct does not bind (R-UNSUPPORTED; `Atof` from the same `extern "C"` block is bound) |
| `src/FoundationClasses/TKernel/GTests/TopLoc_Location_Test.cxx` | 1 | `OSD_Parallel::For` with a functor and `std::atomic` |
| `src/ModelingAlgorithms/TKBO/GTests/BRepAlgoAPI_BuilderAlgo_Test.cxx` | 10 | compile-time type traits (`std::is_copy_constructible` and the like) |
| `src/ModelingAlgorithms/TKExpress/GTests/Expr_GeneralExpression_Test.cxx` | 3 | TKExpress is out of scope (nanocct docs/Design.md) |
| `src/ModelingData/TKBRep/GTests/BRepGraph_TypedIdDispatch_Test.cxx` | 2 | `BRepGraph_NodeId::Visit` / `RefId::Visit` are member templates taking a C++ generic lambda |
| `src/ModelingData/TKGeomBase/GTests/AppCont_ContMatrices_Test.cxx` | 9 | the private header `AppCont_ContMatrices.pxx` (not installed, not bound) |
| `src/ModelingData/TKGeomBase/GTests/GeomBndLib_Curve2d_Test.cxx` | 21 | **pending: as GeomBndLib_Curve (`GeomBndLib_Curve2d`)** |
| `src/ModelingData/TKGeomBase/GTests/GeomBndLib_Curve_Test.cxx` | 25 | **pending: `GeomBndLib_Curve` is not bound -- its public header includes `GeomBndLib_InfiniteHelpers.pxx`, which OCCT 8.0.2 does not install (nanocct generator/overrides.toml)**; one case uses the private `GeomBndLib_SamplingHelpers.pxx` |
| `src/ModelingData/TKGeomBase/GTests/GeomBndLib_OffsetCurve2d_Test.cxx` | 10 | **pending: as GeomBndLib_Curve (`GeomBndLib_Curve2d`)** |
| `src/ModelingData/TKGeomBase/GTests/GeomBndLib_OffsetCurve_Test.cxx` | 14 | **pending: as GeomBndLib_Curve** |
| `src/Visualization/TKService/GTests/Aspect_Grid_Bounds_Test.cxx` | 5 | stub subclasses of the abstract `Aspect_RectangularGrid` / `Aspect_CircularGrid` (no trampolines) |
| `src/Visualization/TKService/GTests/Graphic3d_ShaderManager_Test.cxx` | 3 | protected members reached through a C++ test subclass |
| `src/Visualization/TKV3d/GTests/AIS_ColoredShape_Test.cxx` | 6 | the protected static `dispatchColors`, reached through a C++ test subclass |
