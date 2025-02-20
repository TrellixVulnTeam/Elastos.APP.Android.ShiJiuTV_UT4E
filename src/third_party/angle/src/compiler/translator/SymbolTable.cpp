//
// Copyright (c) 2002-2013 The ANGLE Project Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
//
// Symbol table for parsing. The design principles and most of the functionality are documented in
// the header file.
//

#if defined(_MSC_VER)
#pragma warning(disable : 4718)
#endif

#include "compiler/translator/SymbolTable.h"

#include "compiler/translator/IntermNode.h"
#include "compiler/translator/StaticType.h"

#include <stdio.h>
#include <algorithm>

namespace sh
{

//
// Symbol table levels are a map of pointers to symbols that have to be deleted.
//
TSymbolTableLevel::~TSymbolTableLevel()
{
    for (tLevel::iterator it = level.begin(); it != level.end(); ++it)
        delete (*it).second;
}

bool TSymbolTableLevel::insert(TSymbol *symbol)
{
    // returning true means symbol was added to the table
    tInsertResult result = level.insert(tLevelPair(symbol->getMangledName(), symbol));

    return result.second;
}

bool TSymbolTableLevel::insertUnmangled(TFunction *function)
{
    // returning true means symbol was added to the table
    tInsertResult result = level.insert(tLevelPair(function->name(), function));

    return result.second;
}

TSymbol *TSymbolTableLevel::find(const TString &name) const
{
    tLevel::const_iterator it = level.find(name);
    if (it == level.end())
        return 0;
    else
        return (*it).second;
}

TSymbol *TSymbolTable::find(const TString &name,
                            int shaderVersion,
                            bool *builtIn,
                            bool *sameScope) const
{
    int level = currentLevel();
    TSymbol *symbol;

    do
    {
        if (level == GLSL_BUILTINS)
            level--;
        if (level == ESSL3_1_BUILTINS && shaderVersion != 310)
            level--;
        if (level == ESSL3_BUILTINS && shaderVersion < 300)
            level--;
        if (level == ESSL1_BUILTINS && shaderVersion != 100)
            level--;

        symbol = table[level]->find(name);
    } while (symbol == 0 && --level >= 0);

    if (builtIn)
        *builtIn = (level <= LAST_BUILTIN_LEVEL);
    if (sameScope)
        *sameScope = (level == currentLevel());

    return symbol;
}

TSymbol *TSymbolTable::findGlobal(const TString &name) const
{
    ASSERT(table.size() > GLOBAL_LEVEL);
    return table[GLOBAL_LEVEL]->find(name);
}

TSymbol *TSymbolTable::findBuiltIn(const TString &name, int shaderVersion) const
{
    return findBuiltIn(name, shaderVersion, false);
}

TSymbol *TSymbolTable::findBuiltIn(const TString &name,
                                   int shaderVersion,
                                   bool includeGLSLBuiltins) const
{
    for (int level = LAST_BUILTIN_LEVEL; level >= 0; level--)
    {
        if (level == GLSL_BUILTINS && !includeGLSLBuiltins)
            level--;
        if (level == ESSL3_1_BUILTINS && shaderVersion != 310)
            level--;
        if (level == ESSL3_BUILTINS && shaderVersion < 300)
            level--;
        if (level == ESSL1_BUILTINS && shaderVersion != 100)
            level--;

        TSymbol *symbol = table[level]->find(name);

        if (symbol)
            return symbol;
    }

    return nullptr;
}

TSymbolTable::~TSymbolTable()
{
    while (table.size() > 0)
        pop();
}

constexpr bool IsGenType(const TType *type)
{
    if (type)
    {
        TBasicType basicType = type->getBasicType();
        return basicType == EbtGenType || basicType == EbtGenIType || basicType == EbtGenUType ||
               basicType == EbtGenBType;
    }

    return false;
}

constexpr bool IsVecType(const TType *type)
{
    if (type)
    {
        TBasicType basicType = type->getBasicType();
        return basicType == EbtVec || basicType == EbtIVec || basicType == EbtUVec ||
               basicType == EbtBVec;
    }

    return false;
}

constexpr const TType *SpecificType(const TType *type, int size)
{
    ASSERT(size >= 1 && size <= 4);

    if (!type)
    {
        return nullptr;
    }

    ASSERT(!IsVecType(type));

    switch (type->getBasicType())
    {
        case EbtGenType:
            return StaticType::GetForVec<EbtFloat>(type->getQualifier(),
                                                            static_cast<unsigned char>(size));
        case EbtGenIType:
            return StaticType::GetForVec<EbtInt>(type->getQualifier(),
                                                          static_cast<unsigned char>(size));
        case EbtGenUType:
            return StaticType::GetForVec<EbtUInt>(type->getQualifier(),
                                                           static_cast<unsigned char>(size));
        case EbtGenBType:
            return StaticType::GetForVec<EbtBool>(type->getQualifier(),
                                                           static_cast<unsigned char>(size));
        default:
            return type;
    }
}

constexpr const TType *VectorType(const TType *type, int size)
{
    ASSERT(size >= 2 && size <= 4);

    if (!type)
    {
        return nullptr;
    }

    ASSERT(!IsGenType(type));

    switch (type->getBasicType())
    {
        case EbtVec:
            return StaticType::GetForVecMat<EbtFloat>(static_cast<unsigned char>(size));
        case EbtIVec:
            return StaticType::GetForVecMat<EbtInt>(static_cast<unsigned char>(size));
        case EbtUVec:
            return StaticType::GetForVecMat<EbtUInt>(static_cast<unsigned char>(size));
        case EbtBVec:
            return StaticType::GetForVecMat<EbtBool>(static_cast<unsigned char>(size));
        default:
            return type;
    }
}

bool TSymbolTable::declareVariable(TVariable *variable)
{
    ASSERT(variable->symbolType() == SymbolType::UserDefined);
    return insertVariable(currentLevel(), variable);
}

bool TSymbolTable::declareStructType(TStructure *str)
{
    return insertStructType(currentLevel(), str);
}

bool TSymbolTable::declareInterfaceBlock(TInterfaceBlock *interfaceBlock)
{
    return insert(currentLevel(), interfaceBlock);
}

TVariable *TSymbolTable::insertVariable(ESymbolLevel level, const char *name, const TType &type)
{
    ASSERT(level <= LAST_BUILTIN_LEVEL);
    return insertVariable(level, NewPoolTString(name), type, SymbolType::BuiltIn);
}

TVariable *TSymbolTable::insertVariable(ESymbolLevel level,
                                        const TString *name,
                                        const TType &type,
                                        SymbolType symbolType)
{
    TVariable *var = new TVariable(this, name, type, symbolType);
    if (insert(level, var))
    {
        if (level <= LAST_BUILTIN_LEVEL)
        {
            var->getType().realize();
        }
        return var;
    }
    return nullptr;
}

TVariable *TSymbolTable::insertVariableExt(ESymbolLevel level,
                                           TExtension ext,
                                           const char *name,
                                           const TType &type)
{
    TVariable *var = new TVariable(this, NewPoolTString(name), type, SymbolType::BuiltIn, ext);
    if (insert(level, var))
    {
        if (level <= LAST_BUILTIN_LEVEL)
        {
            var->getType().realize();
        }
        return var;
    }
    return nullptr;
}

bool TSymbolTable::insertVariable(ESymbolLevel level, TVariable *variable)
{
    ASSERT(variable);
    return insert(level, variable);
}

bool TSymbolTable::insertStructType(ESymbolLevel level, TStructure *str)
{
    ASSERT(str);
    return insert(level, str);
}

bool TSymbolTable::insertInterfaceBlock(ESymbolLevel level, TInterfaceBlock *interfaceBlock)
{
    ASSERT(interfaceBlock);
    return insert(level, interfaceBlock);
}

void TSymbolTable::insertBuiltIn(ESymbolLevel level,
                                 TOperator op,
                                 TExtension ext,
                                 const TType *rvalue,
                                 const char *name,
                                 const TType *ptype1,
                                 const TType *ptype2,
                                 const TType *ptype3,
                                 const TType *ptype4,
                                 const TType *ptype5)
{
    if (ptype1->getBasicType() == EbtGSampler2D)
    {
        insertUnmangledBuiltInName(name, level);
        bool gvec4 = (rvalue->getBasicType() == EbtGVec4);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtFloat, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtSampler2D>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtISampler2D>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtUInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtUSampler2D>(), ptype2, ptype3, ptype4, ptype5);
    }
    else if (ptype1->getBasicType() == EbtGSampler3D)
    {
        insertUnmangledBuiltInName(name, level);
        bool gvec4 = (rvalue->getBasicType() == EbtGVec4);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtFloat, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtSampler3D>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtISampler3D>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtUInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtUSampler3D>(), ptype2, ptype3, ptype4, ptype5);
    }
    else if (ptype1->getBasicType() == EbtGSamplerCube)
    {
        insertUnmangledBuiltInName(name, level);
        bool gvec4 = (rvalue->getBasicType() == EbtGVec4);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtFloat, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtSamplerCube>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtISamplerCube>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtUInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtUSamplerCube>(), ptype2, ptype3, ptype4, ptype5);
    }
    else if (ptype1->getBasicType() == EbtGSampler2DArray)
    {
        insertUnmangledBuiltInName(name, level);
        bool gvec4 = (rvalue->getBasicType() == EbtGVec4);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtFloat, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtSampler2DArray>(), ptype2, ptype3, ptype4,
                      ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtISampler2DArray>(), ptype2, ptype3, ptype4,
                      ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtUInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtUSampler2DArray>(), ptype2, ptype3, ptype4,
                      ptype5);
    }
    else if (ptype1->getBasicType() == EbtGSampler2DMS)
    {
        insertUnmangledBuiltInName(name, level);
        bool gvec4 = (rvalue->getBasicType() == EbtGVec4);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtFloat, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtSampler2DMS>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtISampler2DMS>(), ptype2, ptype3, ptype4, ptype5);
        insertBuiltIn(level, gvec4 ? StaticType::GetBasic<EbtUInt, 4>() : rvalue, name,
                      StaticType::GetBasic<EbtUSampler2DMS>(), ptype2, ptype3, ptype4, ptype5);
    }
    else if (IsGImage(ptype1->getBasicType()))
    {
        insertUnmangledBuiltInName(name, level);

        const TType *floatType    = StaticType::GetBasic<EbtFloat, 4>();
        const TType *intType      = StaticType::GetBasic<EbtInt, 4>();
        const TType *unsignedType = StaticType::GetBasic<EbtUInt, 4>();

        const TType *floatImage    = StaticType::GetForFloatImage(ptype1->getBasicType());
        const TType *intImage      = StaticType::GetForIntImage(ptype1->getBasicType());
        const TType *unsignedImage = StaticType::GetForUintImage(ptype1->getBasicType());

        // GLSL ES 3.10, Revision 4, 8.12 Image Functions
        if (rvalue->getBasicType() == EbtGVec4)
        {
            // imageLoad
            insertBuiltIn(level, floatType, name, floatImage, ptype2, ptype3, ptype4, ptype5);
            insertBuiltIn(level, intType, name, intImage, ptype2, ptype3, ptype4, ptype5);
            insertBuiltIn(level, unsignedType, name, unsignedImage, ptype2, ptype3, ptype4, ptype5);
        }
        else if (rvalue->getBasicType() == EbtVoid)
        {
            // imageStore
            insertBuiltIn(level, rvalue, name, floatImage, ptype2, floatType, ptype4, ptype5);
            insertBuiltIn(level, rvalue, name, intImage, ptype2, intType, ptype4, ptype5);
            insertBuiltIn(level, rvalue, name, unsignedImage, ptype2, unsignedType, ptype4, ptype5);
        }
        else
        {
            // imageSize
            insertBuiltIn(level, rvalue, name, floatImage, ptype2, ptype3, ptype4, ptype5);
            insertBuiltIn(level, rvalue, name, intImage, ptype2, ptype3, ptype4, ptype5);
            insertBuiltIn(level, rvalue, name, unsignedImage, ptype2, ptype3, ptype4, ptype5);
        }
    }
    else if (IsGenType(rvalue) || IsGenType(ptype1) || IsGenType(ptype2) || IsGenType(ptype3) ||
             IsGenType(ptype4))
    {
        ASSERT(!ptype5);
        insertUnmangledBuiltInName(name, level);
        insertBuiltIn(level, op, ext, SpecificType(rvalue, 1), name, SpecificType(ptype1, 1),
                      SpecificType(ptype2, 1), SpecificType(ptype3, 1), SpecificType(ptype4, 1));
        insertBuiltIn(level, op, ext, SpecificType(rvalue, 2), name, SpecificType(ptype1, 2),
                      SpecificType(ptype2, 2), SpecificType(ptype3, 2), SpecificType(ptype4, 2));
        insertBuiltIn(level, op, ext, SpecificType(rvalue, 3), name, SpecificType(ptype1, 3),
                      SpecificType(ptype2, 3), SpecificType(ptype3, 3), SpecificType(ptype4, 3));
        insertBuiltIn(level, op, ext, SpecificType(rvalue, 4), name, SpecificType(ptype1, 4),
                      SpecificType(ptype2, 4), SpecificType(ptype3, 4), SpecificType(ptype4, 4));
    }
    else if (IsVecType(rvalue) || IsVecType(ptype1) || IsVecType(ptype2) || IsVecType(ptype3))
    {
        ASSERT(!ptype4 && !ptype5);
        insertUnmangledBuiltInName(name, level);
        insertBuiltIn(level, op, ext, VectorType(rvalue, 2), name, VectorType(ptype1, 2),
                      VectorType(ptype2, 2), VectorType(ptype3, 2));
        insertBuiltIn(level, op, ext, VectorType(rvalue, 3), name, VectorType(ptype1, 3),
                      VectorType(ptype2, 3), VectorType(ptype3, 3));
        insertBuiltIn(level, op, ext, VectorType(rvalue, 4), name, VectorType(ptype1, 4),
                      VectorType(ptype2, 4), VectorType(ptype3, 4));
    }
    else
    {
        TFunction *function =
            new TFunction(this, NewPoolTString(name), rvalue, SymbolType::BuiltIn, false, op, ext);

        function->addParameter(TConstParameter(ptype1));

        if (ptype2)
        {
            function->addParameter(TConstParameter(ptype2));
        }

        if (ptype3)
        {
            function->addParameter(TConstParameter(ptype3));
        }

        if (ptype4)
        {
            function->addParameter(TConstParameter(ptype4));
        }

        if (ptype5)
        {
            function->addParameter(TConstParameter(ptype5));
        }

        ASSERT(hasUnmangledBuiltInAtLevel(name, level));
        insert(level, function);
    }
}

void TSymbolTable::insertBuiltInOp(ESymbolLevel level,
                                   TOperator op,
                                   const TType *rvalue,
                                   const TType *ptype1,
                                   const TType *ptype2,
                                   const TType *ptype3,
                                   const TType *ptype4,
                                   const TType *ptype5)
{
    const char *name = GetOperatorString(op);
    ASSERT(strlen(name) > 0);
    insertUnmangledBuiltInName(name, level);
    insertBuiltIn(level, op, TExtension::UNDEFINED, rvalue, name, ptype1, ptype2, ptype3, ptype4,
                  ptype5);
}

void TSymbolTable::insertBuiltInOp(ESymbolLevel level,
                                   TOperator op,
                                   TExtension ext,
                                   const TType *rvalue,
                                   const TType *ptype1,
                                   const TType *ptype2,
                                   const TType *ptype3,
                                   const TType *ptype4,
                                   const TType *ptype5)
{
    const char *name = GetOperatorString(op);
    insertUnmangledBuiltInName(name, level);
    insertBuiltIn(level, op, ext, rvalue, name, ptype1, ptype2, ptype3, ptype4, ptype5);
}

void TSymbolTable::insertBuiltInFunctionNoParameters(ESymbolLevel level,
                                                     TOperator op,
                                                     const TType *rvalue,
                                                     const char *name)
{
    insertUnmangledBuiltInName(name, level);
    insert(level,
           new TFunction(this, NewPoolTString(name), rvalue, SymbolType::BuiltIn, false, op));
}

void TSymbolTable::insertBuiltInFunctionNoParametersExt(ESymbolLevel level,
                                                        TExtension ext,
                                                        TOperator op,
                                                        const TType *rvalue,
                                                        const char *name)
{
    insertUnmangledBuiltInName(name, level);
    insert(level,
           new TFunction(this, NewPoolTString(name), rvalue, SymbolType::BuiltIn, false, op, ext));
}

TPrecision TSymbolTable::getDefaultPrecision(TBasicType type) const
{
    if (!SupportsPrecision(type))
        return EbpUndefined;

    // unsigned integers use the same precision as signed
    TBasicType baseType = (type == EbtUInt) ? EbtInt : type;

    int level = static_cast<int>(precisionStack.size()) - 1;
    assert(level >= 0);  // Just to be safe. Should not happen.
    // If we dont find anything we return this. Some types don't have predefined default precision.
    TPrecision prec = EbpUndefined;
    while (level >= 0)
    {
        PrecisionStackLevel::iterator it = precisionStack[level]->find(baseType);
        if (it != precisionStack[level]->end())
        {
            prec = (*it).second;
            break;
        }
        level--;
    }
    return prec;
}

void TSymbolTable::insertUnmangledBuiltInName(const char *name, ESymbolLevel level)
{
    ASSERT(level >= 0 && level < static_cast<ESymbolLevel>(table.size()));
    ASSERT(mUserDefinedUniqueIdsStart == -1);
    table[level]->insertUnmangledBuiltInName(std::string(name));
}

bool TSymbolTable::hasUnmangledBuiltInAtLevel(const char *name, ESymbolLevel level)
{
    ASSERT(level >= 0 && level < static_cast<ESymbolLevel>(table.size()));
    return table[level]->hasUnmangledBuiltIn(std::string(name));
}

bool TSymbolTable::hasUnmangledBuiltInForShaderVersion(const char *name, int shaderVersion)
{
    ASSERT(static_cast<ESymbolLevel>(table.size()) > LAST_BUILTIN_LEVEL);

    for (int level = LAST_BUILTIN_LEVEL; level >= 0; --level)
    {
        if (level == ESSL3_1_BUILTINS && shaderVersion != 310)
        {
            --level;
        }
        if (level == ESSL3_BUILTINS && shaderVersion < 300)
        {
            --level;
        }
        if (level == ESSL1_BUILTINS && shaderVersion != 100)
        {
            --level;
        }

        if (table[level]->hasUnmangledBuiltIn(name))
        {
            return true;
        }
    }
    return false;
}

void TSymbolTable::markBuiltInInitializationFinished()
{
    mUserDefinedUniqueIdsStart = mUniqueIdCounter;
}

void TSymbolTable::clearCompilationResults()
{
    mUniqueIdCounter = mUserDefinedUniqueIdsStart;

    // User-defined scopes should have already been cleared when the compilation finished.
    ASSERT(table.size() == LAST_BUILTIN_LEVEL + 1u);
}

int TSymbolTable::nextUniqueIdValue()
{
    ASSERT(mUniqueIdCounter < std::numeric_limits<int>::max());
    return ++mUniqueIdCounter;
}

}  // namespace sh
