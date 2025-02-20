# LLVM CMake target exports.  Do not include directly.
add_library(LLVMLTO STATIC IMPORTED)
set_property(TARGET LLVMLTO PROPERTY IMPORTED_LOCATION "//lib/libLLVMLTO.a")
add_library(LLVMObjCARCOpts STATIC IMPORTED)
set_property(TARGET LLVMObjCARCOpts PROPERTY IMPORTED_LOCATION "//lib/libLLVMObjCARCOpts.a")
add_library(LLVMLinker STATIC IMPORTED)
set_property(TARGET LLVMLinker PROPERTY IMPORTED_LOCATION "//lib/libLLVMLinker.a")
add_library(LLVMBitWriter STATIC IMPORTED)
set_property(TARGET LLVMBitWriter PROPERTY IMPORTED_LOCATION "//lib/libLLVMBitWriter.a")
add_library(LLVMTableGen STATIC IMPORTED)
set_property(TARGET LLVMTableGen PROPERTY IMPORTED_LOCATION "//lib/libLLVMTableGen.a")
add_library(LLVMNaClBitTestUtils STATIC IMPORTED)
set_property(TARGET LLVMNaClBitTestUtils PROPERTY IMPORTED_LOCATION "//lib/libLLVMNaClBitTestUtils.a")
add_library(LLVMNaClBitAnalysis STATIC IMPORTED)
set_property(TARGET LLVMNaClBitAnalysis PROPERTY IMPORTED_LOCATION "//lib/libLLVMNaClBitAnalysis.a")
add_library(LLVMNaClBitWriter STATIC IMPORTED)
set_property(TARGET LLVMNaClBitWriter PROPERTY IMPORTED_LOCATION "//lib/libLLVMNaClBitWriter.a")
add_library(LLVMLineEditor STATIC IMPORTED)
set_property(TARGET LLVMLineEditor PROPERTY IMPORTED_LOCATION "//lib/libLLVMLineEditor.a")
add_library(LLVMInstrumentation STATIC IMPORTED)
set_property(TARGET LLVMInstrumentation PROPERTY IMPORTED_LOCATION "//lib/libLLVMInstrumentation.a")
add_library(LLVMOrcJIT STATIC IMPORTED)
set_property(TARGET LLVMOrcJIT PROPERTY IMPORTED_LOCATION "//lib/libLLVMOrcJIT.a")
add_library(LLVMMinSFITransforms STATIC IMPORTED)
set_property(TARGET LLVMMinSFITransforms PROPERTY IMPORTED_LOCATION "//lib/libLLVMMinSFITransforms.a")
add_library(LLVMIRReader STATIC IMPORTED)
set_property(TARGET LLVMIRReader PROPERTY IMPORTED_LOCATION "//lib/libLLVMIRReader.a")
add_library(LLVMNaClBitReader STATIC IMPORTED)
set_property(TARGET LLVMNaClBitReader PROPERTY IMPORTED_LOCATION "//lib/libLLVMNaClBitReader.a")
add_library(LLVMNaClAnalysis STATIC IMPORTED)
set_property(TARGET LLVMNaClAnalysis PROPERTY IMPORTED_LOCATION "//lib/libLLVMNaClAnalysis.a")
add_library(LLVMAsmParser STATIC IMPORTED)
set_property(TARGET LLVMAsmParser PROPERTY IMPORTED_LOCATION "//lib/libLLVMAsmParser.a")
add_library(LLVMARMDisassembler STATIC IMPORTED)
set_property(TARGET LLVMARMDisassembler PROPERTY IMPORTED_LOCATION "//lib/libLLVMARMDisassembler.a")
add_library(LLVMARMCodeGen STATIC IMPORTED)
set_property(TARGET LLVMARMCodeGen PROPERTY IMPORTED_LOCATION "//lib/libLLVMARMCodeGen.a")
add_library(LLVMARMAsmParser STATIC IMPORTED)
set_property(TARGET LLVMARMAsmParser PROPERTY IMPORTED_LOCATION "//lib/libLLVMARMAsmParser.a")
add_library(LLVMARMDesc STATIC IMPORTED)
set_property(TARGET LLVMARMDesc PROPERTY IMPORTED_LOCATION "//lib/libLLVMARMDesc.a")
add_library(LLVMARMInfo STATIC IMPORTED)
set_property(TARGET LLVMARMInfo PROPERTY IMPORTED_LOCATION "//lib/libLLVMARMInfo.a")
add_library(LLVMARMAsmPrinter STATIC IMPORTED)
set_property(TARGET LLVMARMAsmPrinter PROPERTY IMPORTED_LOCATION "//lib/libLLVMARMAsmPrinter.a")
add_library(LLVMMipsDisassembler STATIC IMPORTED)
set_property(TARGET LLVMMipsDisassembler PROPERTY IMPORTED_LOCATION "//lib/libLLVMMipsDisassembler.a")
add_library(LLVMMipsCodeGen STATIC IMPORTED)
set_property(TARGET LLVMMipsCodeGen PROPERTY IMPORTED_LOCATION "//lib/libLLVMMipsCodeGen.a")
add_library(LLVMNaClTransforms STATIC IMPORTED)
set_property(TARGET LLVMNaClTransforms PROPERTY IMPORTED_LOCATION "//lib/libLLVMNaClTransforms.a")
add_library(LLVMMipsAsmParser STATIC IMPORTED)
set_property(TARGET LLVMMipsAsmParser PROPERTY IMPORTED_LOCATION "//lib/libLLVMMipsAsmParser.a")
add_library(LLVMMipsDesc STATIC IMPORTED)
set_property(TARGET LLVMMipsDesc PROPERTY IMPORTED_LOCATION "//lib/libLLVMMipsDesc.a")
add_library(LLVMMipsInfo STATIC IMPORTED)
set_property(TARGET LLVMMipsInfo PROPERTY IMPORTED_LOCATION "//lib/libLLVMMipsInfo.a")
add_library(LLVMMipsAsmPrinter STATIC IMPORTED)
set_property(TARGET LLVMMipsAsmPrinter PROPERTY IMPORTED_LOCATION "//lib/libLLVMMipsAsmPrinter.a")
add_library(LLVMOption STATIC IMPORTED)
set_property(TARGET LLVMOption PROPERTY IMPORTED_LOCATION "//lib/libLLVMOption.a")
add_library(LLVMX86Disassembler STATIC IMPORTED)
set_property(TARGET LLVMX86Disassembler PROPERTY IMPORTED_LOCATION "//lib/libLLVMX86Disassembler.a")
add_library(LLVMX86AsmParser STATIC IMPORTED)
set_property(TARGET LLVMX86AsmParser PROPERTY IMPORTED_LOCATION "//lib/libLLVMX86AsmParser.a")
add_library(LLVMX86CodeGen STATIC IMPORTED)
set_property(TARGET LLVMX86CodeGen PROPERTY IMPORTED_LOCATION "//lib/libLLVMX86CodeGen.a")
add_library(LLVMSelectionDAG STATIC IMPORTED)
set_property(TARGET LLVMSelectionDAG PROPERTY IMPORTED_LOCATION "//lib/libLLVMSelectionDAG.a")
add_library(LLVMAsmPrinter STATIC IMPORTED)
set_property(TARGET LLVMAsmPrinter PROPERTY IMPORTED_LOCATION "//lib/libLLVMAsmPrinter.a")
add_library(LLVMX86Desc STATIC IMPORTED)
set_property(TARGET LLVMX86Desc PROPERTY IMPORTED_LOCATION "//lib/libLLVMX86Desc.a")
add_library(LLVMMCDisassembler STATIC IMPORTED)
set_property(TARGET LLVMMCDisassembler PROPERTY IMPORTED_LOCATION "//lib/libLLVMMCDisassembler.a")
add_library(LLVMX86Info STATIC IMPORTED)
set_property(TARGET LLVMX86Info PROPERTY IMPORTED_LOCATION "//lib/libLLVMX86Info.a")
add_library(LLVMX86AsmPrinter STATIC IMPORTED)
set_property(TARGET LLVMX86AsmPrinter PROPERTY IMPORTED_LOCATION "//lib/libLLVMX86AsmPrinter.a")
add_library(LLVMX86Utils STATIC IMPORTED)
set_property(TARGET LLVMX86Utils PROPERTY IMPORTED_LOCATION "//lib/libLLVMX86Utils.a")
add_library(LLVMMCJIT STATIC IMPORTED)
set_property(TARGET LLVMMCJIT PROPERTY IMPORTED_LOCATION "//lib/libLLVMMCJIT.a")
add_library(LLVMDebugInfoDWARF STATIC IMPORTED)
set_property(TARGET LLVMDebugInfoDWARF PROPERTY IMPORTED_LOCATION "//lib/libLLVMDebugInfoDWARF.a")
add_library(LLVMPasses STATIC IMPORTED)
set_property(TARGET LLVMPasses PROPERTY IMPORTED_LOCATION "//lib/libLLVMPasses.a")
add_library(LLVMipo STATIC IMPORTED)
set_property(TARGET LLVMipo PROPERTY IMPORTED_LOCATION "//lib/libLLVMipo.a")
add_library(LLVMVectorize STATIC IMPORTED)
set_property(TARGET LLVMVectorize PROPERTY IMPORTED_LOCATION "//lib/libLLVMVectorize.a")
add_library(LLVMInterpreter STATIC IMPORTED)
set_property(TARGET LLVMInterpreter PROPERTY IMPORTED_LOCATION "//lib/libLLVMInterpreter.a")
add_library(LLVMExecutionEngine STATIC IMPORTED)
set_property(TARGET LLVMExecutionEngine PROPERTY IMPORTED_LOCATION "//lib/libLLVMExecutionEngine.a")
add_library(LLVMRuntimeDyld STATIC IMPORTED)
set_property(TARGET LLVMRuntimeDyld PROPERTY IMPORTED_LOCATION "//lib/libLLVMRuntimeDyld.a")
add_library(LLVMCodeGen STATIC IMPORTED)
set_property(TARGET LLVMCodeGen PROPERTY IMPORTED_LOCATION "//lib/libLLVMCodeGen.a")
add_library(LLVMTarget STATIC IMPORTED)
set_property(TARGET LLVMTarget PROPERTY IMPORTED_LOCATION "//lib/libLLVMTarget.a")
add_library(LLVMScalarOpts STATIC IMPORTED)
set_property(TARGET LLVMScalarOpts PROPERTY IMPORTED_LOCATION "//lib/libLLVMScalarOpts.a")
add_library(LLVMProfileData STATIC IMPORTED)
set_property(TARGET LLVMProfileData PROPERTY IMPORTED_LOCATION "//lib/libLLVMProfileData.a")
add_library(LLVMObject STATIC IMPORTED)
set_property(TARGET LLVMObject PROPERTY IMPORTED_LOCATION "//lib/libLLVMObject.a")
add_library(LLVMMCParser STATIC IMPORTED)
set_property(TARGET LLVMMCParser PROPERTY IMPORTED_LOCATION "//lib/libLLVMMCParser.a")
add_library(LLVMBitReader STATIC IMPORTED)
set_property(TARGET LLVMBitReader PROPERTY IMPORTED_LOCATION "//lib/libLLVMBitReader.a")
add_library(LLVMInstCombine STATIC IMPORTED)
set_property(TARGET LLVMInstCombine PROPERTY IMPORTED_LOCATION "//lib/libLLVMInstCombine.a")
add_library(LLVMTransformUtils STATIC IMPORTED)
set_property(TARGET LLVMTransformUtils PROPERTY IMPORTED_LOCATION "//lib/libLLVMTransformUtils.a")
add_library(LLVMipa STATIC IMPORTED)
set_property(TARGET LLVMipa PROPERTY IMPORTED_LOCATION "//lib/libLLVMipa.a")
add_library(LLVMMC STATIC IMPORTED)
set_property(TARGET LLVMMC PROPERTY IMPORTED_LOCATION "//lib/libLLVMMC.a")
add_library(LLVMAnalysis STATIC IMPORTED)
set_property(TARGET LLVMAnalysis PROPERTY IMPORTED_LOCATION "//lib/libLLVMAnalysis.a")
add_library(LLVMCore STATIC IMPORTED)
set_property(TARGET LLVMCore PROPERTY IMPORTED_LOCATION "//lib/libLLVMCore.a")
add_library(LLVMDebugInfoPDB STATIC IMPORTED)
set_property(TARGET LLVMDebugInfoPDB PROPERTY IMPORTED_LOCATION "//lib/libLLVMDebugInfoPDB.a")
add_library(LLVMSupport STATIC IMPORTED)
set_property(TARGET LLVMSupport PROPERTY IMPORTED_LOCATION "//lib/libLLVMSupport.a")
# Explicit library dependency information.
#
# The following property assignments tell CMake about link
# dependencies of libraries imported from LLVM.
set_property(TARGET LLVMSupport PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES )
set_property(TARGET LLVMMC PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMMCParser PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMSupport)
set_property(TARGET LLVMCore PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMAnalysis PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMSupport)
set_property(TARGET LLVMipa PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMSupport)
set_property(TARGET LLVMTransformUtils PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMSupport LLVMipa)
set_property(TARGET LLVMInstCombine PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMSupport LLVMTransformUtils)
set_property(TARGET LLVMBitReader PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMSupport)
set_property(TARGET LLVMObject PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMBitReader LLVMCore LLVMMC LLVMMCParser LLVMSupport)
set_property(TARGET LLVMProfileData PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMObject LLVMSupport)
set_property(TARGET LLVMScalarOpts PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMInstCombine LLVMProfileData LLVMSupport LLVMTransformUtils)
set_property(TARGET LLVMTarget PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMMC LLVMSupport)
set_property(TARGET LLVMCodeGen PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMMC LLVMScalarOpts LLVMSupport LLVMTarget LLVMTransformUtils)
set_property(TARGET LLVMAsmPrinter PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCodeGen LLVMCore LLVMMC LLVMMCParser LLVMSupport LLVMTarget LLVMTransformUtils)
set_property(TARGET LLVMSelectionDAG PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCodeGen LLVMCore LLVMMC LLVMSupport LLVMTarget LLVMTransformUtils)
set_property(TARGET LLVMMCDisassembler PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMSupport)
set_property(TARGET LLVMARMAsmPrinter PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMSupport)
set_property(TARGET LLVMARMInfo PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMARMDesc PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMARMAsmPrinter LLVMARMInfo LLVMMC LLVMMCDisassembler LLVMSupport)
set_property(TARGET LLVMARMAsmParser PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMARMDesc LLVMARMInfo LLVMMC LLVMMCParser LLVMSupport)
set_property(TARGET LLVMVectorize PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMSupport LLVMTransformUtils)
set_property(TARGET LLVMipo PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMInstCombine LLVMScalarOpts LLVMSupport LLVMTransformUtils LLVMVectorize LLVMipa)
set_property(TARGET LLVMNaClTransforms PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMScalarOpts LLVMSupport LLVMTransformUtils LLVMipo)
set_property(TARGET LLVMARMCodeGen PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMARMAsmPrinter LLVMARMDesc LLVMARMInfo LLVMAnalysis LLVMAsmPrinter LLVMCodeGen LLVMCore LLVMMC LLVMNaClTransforms LLVMScalarOpts LLVMSelectionDAG LLVMSupport LLVMTarget)
set_property(TARGET LLVMARMDisassembler PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMARMDesc LLVMARMInfo LLVMMCDisassembler LLVMSupport)
set_property(TARGET LLVMAsmParser PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMSupport)
set_property(TARGET LLVMBitWriter PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMSupport)
set_property(TARGET LLVMDebugInfoDWARF PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMObject LLVMSupport)
set_property(TARGET LLVMDebugInfoPDB PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMRuntimeDyld PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMObject LLVMSupport)
set_property(TARGET LLVMExecutionEngine PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMMC LLVMObject LLVMRuntimeDyld LLVMSupport)
set_property(TARGET LLVMMCJIT PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMExecutionEngine LLVMObject LLVMRuntimeDyld LLVMSupport LLVMTarget)
set_property(TARGET LLVMNaClAnalysis PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMSupport)
set_property(TARGET LLVMNaClBitReader PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMBitReader LLVMCore LLVMNaClAnalysis LLVMSupport)
set_property(TARGET LLVMIRReader PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAsmParser LLVMBitReader LLVMCore LLVMNaClBitReader LLVMSupport)
set_property(TARGET LLVMInstrumentation PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMMC LLVMSupport LLVMTransformUtils)
set_property(TARGET LLVMInterpreter PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCodeGen LLVMCore LLVMExecutionEngine LLVMSupport)
set_property(TARGET LLVMLinker PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMSupport LLVMTransformUtils)
set_property(TARGET LLVMObjCARCOpts PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMSupport LLVMTransformUtils)
set_property(TARGET LLVMLTO PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMBitReader LLVMBitWriter LLVMCodeGen LLVMCore LLVMInstCombine LLVMLinker LLVMMC LLVMObjCARCOpts LLVMObject LLVMScalarOpts LLVMSupport LLVMTarget LLVMipa LLVMipo)
set_property(TARGET LLVMLineEditor PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMMinSFITransforms PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMNaClAnalysis LLVMNaClTransforms LLVMSupport LLVMipo)
set_property(TARGET LLVMMipsAsmPrinter PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMSupport)
set_property(TARGET LLVMMipsInfo PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMMipsDesc PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMMipsAsmPrinter LLVMMipsInfo LLVMSupport)
set_property(TARGET LLVMMipsAsmParser PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMMCParser LLVMMipsDesc LLVMMipsInfo LLVMSupport)
set_property(TARGET LLVMMipsCodeGen PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMAsmPrinter LLVMCodeGen LLVMCore LLVMMC LLVMMipsAsmPrinter LLVMMipsDesc LLVMMipsInfo LLVMNaClTransforms LLVMSelectionDAG LLVMSupport LLVMTarget)
set_property(TARGET LLVMMipsDisassembler PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMCDisassembler LLVMMipsInfo LLVMSupport)
set_property(TARGET LLVMNaClBitWriter PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMNaClBitReader LLVMSupport)
set_property(TARGET LLVMNaClBitAnalysis PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMNaClAnalysis LLVMNaClBitReader LLVMNaClBitWriter LLVMSupport)
set_property(TARGET LLVMNaClBitTestUtils PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMNaClBitAnalysis LLVMNaClBitReader LLVMNaClBitWriter LLVMSupport)
set_property(TARGET LLVMX86Utils PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMSupport)
set_property(TARGET LLVMX86AsmPrinter PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMSupport LLVMX86Utils)
set_property(TARGET LLVMX86Info PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMX86Desc PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMMCDisassembler LLVMObject LLVMSupport LLVMX86AsmPrinter LLVMX86Info)
set_property(TARGET LLVMX86CodeGen PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMAsmPrinter LLVMCodeGen LLVMCore LLVMMC LLVMSelectionDAG LLVMSupport LLVMTarget LLVMX86AsmPrinter LLVMX86Desc LLVMX86Info LLVMX86Utils)
set_property(TARGET LLVMOption PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMOrcJIT PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMCore LLVMExecutionEngine LLVMObject LLVMRuntimeDyld LLVMSupport LLVMTransformUtils)
set_property(TARGET LLVMPasses PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMAnalysis LLVMCore LLVMInstCombine LLVMScalarOpts LLVMSupport LLVMTransformUtils LLVMVectorize LLVMipa LLVMipo)
set_property(TARGET LLVMTableGen PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMSupport)
set_property(TARGET LLVMX86AsmParser PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMC LLVMMCParser LLVMSupport LLVMX86CodeGen LLVMX86Desc LLVMX86Info)
set_property(TARGET LLVMX86Disassembler PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES LLVMMCDisassembler LLVMSupport LLVMX86Info)
set_property(TARGET LLVMSupport APPEND PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES pthread rt dl m )
