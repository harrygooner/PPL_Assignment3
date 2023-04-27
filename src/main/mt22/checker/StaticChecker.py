from Visitor import Visitor
from AST import *
from StaticError import *

class Symbol(Decl):
    def __init__(self, name:str, typ:str, inherit:bool = False, out: bool = False):
        self.name = name
        self.typ = typ
        self.inherit = inherit
        self.out = out

class FuncType(Type):
    def __init__(self, return_typ: Type, params_list:List[Type]):
        self.return_typ = return_typ
        self.params_list = params_list

class Utils:
    def inferClass(o, name, typInfer):
        for env in o:
            for symbol in env:
                if symbol.name == name:
                    if type(symbol.typ) is FuncType :
                        symbol.typ.return_typ = typInfer
                    else:
                        symbol.typ = typInfer
                    break

class getEnv(Visitor):
    def __init__(self):
        pass
    def visitProgram(self, ast, param):
        
        param.append(Symbol('readInteger', FuncType(IntegerType(), [])))
        param.append(Symbol('readFloat', FuncType(FloatType(), [])))
        param.append(Symbol('readBoolean', FuncType(BooleanType(), [])))
        param.append(Symbol('readString', FuncType(StringType(), [])))
        param.append(Symbol('printInteger', FuncType(VoidType(), [ParamDecl('a', IntegerType())])))
        param.append(Symbol('printBoolean', FuncType(VoidType(), [ParamDecl('a', BooleanType())])))
        param.append(Symbol('printString', FuncType(VoidType(), [ParamDecl('a', StringType())])))
        param.append(Symbol('writeFloat', FuncType(VoidType(), [ParamDecl('a', FloatType())])))

        for decl in ast.decls:
            self.visit(decl, param)
        return param
    def visitVardecl(self, ast, param):
        pass
    def visitFuncDecl(self, ast, param):
        lst_params=[]
        for para in ast.params:
            self.visit(para, lst_params)
        param.append(Symbol(ast.name, FuncType(ast.return_type, lst_params), ast.inherit))
    def visitParamDecl(self, ast, param):
        param.append(ast)


class StaticChecker(Visitor):
    inLoop = False
    funcList = []
    inheritFuncname = None

    def __init__(self, asttree):
        self.ast = asttree
    def check(self):
        return self.visitProgram(self.ast,[[]])
    def visitIntegerType(self, ast, param): pass
    def visitFloatType(self, ast, param): pass
    def visitBooleanType(self, ast, param): pass
    def visitStringType(self, ast, param): pass
    def visitArrayType(self, ast, param): pass
    def visitAutoType(self, ast, param): pass
    def visitVoidType(self, ast, param): pass

    def visitBinExpr(self, ast, param): 
        e1t = self.visit(ast.left,param)
        e2t = self.visit(ast.right,param)
        if type(e1t) is FuncType:
            e1t = e1t.return_typ
        if type(e2t) is FuncType:
            e2t = e2t.return_typ
        # + , - , *, / accept their operands in int/float type and return int/float type
        if ast.op in ['+','-','*','/']:
            if (type(e1t) is not FloatType and type(e1t) is not IntegerType and type(e1t) is not AutoType):
                raise TypeMismatchInExpression(ast)
            if (type(e2t) is not FloatType and type(e2t) is not IntegerType and type(e2t) is not AutoType):
                raise TypeMismatchInExpression(ast)
            if(type(e1t) is AutoType and type(e1t) is AutoType):
                raise TypeMismatchInExpression(ast)
            if type(e1t) is AutoType:
                Utils.inferClass(param, ast.left.name, e2t)
            elif type(e2t) is AutoType:
                Utils.inferClass(param, ast.right.name, e1t)
            if type(e1t) is FloatType or type(e2t) is FloatType:
                return FloatType()            
            return IntegerType()

        #% accept their operands in IntegerType and return in IntegerType
        elif ast.op == '%':
            if type(e1t) is not IntegerType and type(e1t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if type(e2t) is not IntegerType and type(e2t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if(type(e1t) is AutoType and type(e1t) is AutoType):
                raise TypeMismatchInExpression(ast)
            if type(e1t) is AutoType:
                Utils.inferClass(o, ast.left.name, IntegerType())
            elif type(e2t) is AutoType:
                Utils.inferClass(o, ast.right.name, IntegerType())
            return IntegerType()

        # !, &&, || accept their operands in bool type and return bool type
        elif ast.op in ['&&', '||']:
            if type(e1t) is not BooleanType and type(e1t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if type(e2t) is not BooleanType and type(e2t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if(type(e1t) is AutoType and type(e1t) is AutoType):
                raise TypeMismatchInExpression(ast)
            if type(e1t) is AutoType:
                Utils.inferClass(o, ast.left.name, BooleanType())
            elif type(e2t) is AutoType:
                Utils.inferClass(o, ast.right.name, BooleanType())
            return BooleanType()

        #:: accept their operands in StringType and return StringType
        elif ast.op == '::':
            if type(e1t) is not StringType and type(e1t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if type(e2t) is not StringType and type(e2t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if(type(e1t) is AutoType and type(e1t) is AutoType):
                raise TypeMismatchInExpression(ast)
            if type(e1t) is AutoType:
                Utils.inferClass(o, ast.left.name, StringType())
            elif type(e2t) is AutoType:
                Utils.inferClass(o, ast.right.name, StringType())
            return StringType()

        # !=, == accept their operands in IntegerType/BooleanType and return BooleanType
        elif ast.op in ['==','!=']:
            if type(e1t) is not BooleanType and type(e1t) is not IntegerType and type(e1t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if type(e2t) is not BooleanType and type(e2t) is not IntegerType and type(e2t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if(type(e1t) is AutoType and type(e1t) is AutoType):
                raise TypeMismatchInExpression(ast)
            if type(e1t) is AutoType:
                Utils.inferClass(o, ast.left.name, e2t)
            elif type(e2t) is AutoType:
                Utils.inferClass(o, ast.right.name, e1t)
            return BooleanType()

        #['>', '<', '==', '!='] accept their operands in IntegerType/FloatType and return BooleanType
        elif ast.op in ['>', '<', '==', '!=']:
            if type(e1t) is not FloatType and type(e1t) is not IntegerType and type(e1t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if type(e2t) is not FloatType and type(e2t) is not IntegerType and type(e2t) is not AutoType:
                raise TypeMismatchInExpression(ast)
            if(type(e1t) is AutoType and type(e1t) is AutoType):
                raise TypeMismatchInExpression(ast)
            if type(e1t) is AutoType:
                Utils.inferClass(o, ast.left.name, e2t)
            elif type(e2t) is AutoType:
                Utils.inferClass(o, ast.right.name, e1t)
            return BooleanType()

    def visitUnExpr(self, ast, param): 
        operandTyp = self.visit(ast.val, param)
        if type(operandTyp) is FuncType:
            operandTyp = operandTyp.return_typ
        if ast.op == '-':
            if type(operandTyp) is not FloatType and type(operandTyp) is not IntegerType:
                raise TypeMismatchInExpression(ast)
            return operandTyp
        elif ast.op == '!':
            if type(operandTyp) is not BooleanType:
                raise TypeMismatchInExpression(ast)
            return BooleanType()

    def visitId(self, ast, param): 
        a = {}
        for env in param:
            for symbol in env:
                if symbol.name == ast.name:
                    if type(symbol.typ) is FuncType:
                         raise TypeMismatchInExpression(ast)
                    return symbol.typ
        raise Undeclared(Identifier(), ast.name)

    def visitArrayCell(self, ast, param): 
        arrayTyp = None
        for env in param:
            for symbol in env:
                if symbol.name == ast.name:
                    arrayTyp = symbol.typ


        if(arrayTyp is None): 
            raise Undeclared(Identifier(), ast.name)
        
        if type(arrayTyp) is not ArrayType:
            raise TypeMismatchInExpression(ast)

        for i in ast.cell:
            posTyp = self.visit(i, param)
            if(type(posTyp) is not IntegerType):
                raise TypeMismatchInExpression(ast)
        
        # print(arrayTyp)
        dim = arrayTyp.dimensions
        dimen = dim
        # print(ast.cell)
        if(len(dim) < len(ast.cell)):
            raise TypeMismatchInExpression(ast)
        for i in range(len(ast.cell)):
            # if(dim[i] > ast.cell[i].val):
            dimen = dimen[1:]
            # else:
                # raise TypeMismatchInExpression(ast)
        
        if(dimen == []):  
            return arrayTyp.typ
        else: return ArrayType(dimen, arrayTyp.typ)
        
    def visitIntegerLit(self, ast, param): return IntegerType()
    
    def visitFloatLit(self, ast, param): return FloatType()
    
    def visitStringLit(self, ast, param): return StringType()
    
    def visitBooleanLit(self, ast, param): return BooleanType()

    def visitArrayLit(self, ast, param): 
        dim = []
        prevEleTyp = None
        typInfer = None
        numberOfEle = 0
        for ele in ast.explist:
            numberOfEle += 1
            # print(ele)
            eleTyp = self.visit(ele,param)
            # print(type(eleTyp), type(self.visit(ele,param)))
            if numberOfEle >1:
                if type(eleTyp) is ArrayType:
                    if(eleTyp.dimensions != prevEleTyp.dimensions):
                        # print(ele,eleTyp.dimensions, prevEleTyp.dimensions)
                        raise IllegalArrayLiteral(ast)
                    if type(eleTyp.typ) is not type(prevEleTyp.typ):
                        # if type(eleTyp.typ) is IntegerType and type(prevEleTyp.typ) is FloatType:
                        #     typInfer = prevEleTyp
                        # elif type(eleTyp.typ) is FloatType and type(prevEleTyp.typ) is IntegerType:
                        #     typInfer = eleTyp 
                        # else:    
                            # print(eleTyp, prevEleTyp)
                        raise IllegalArrayLiteral(ast)
                else:
                    if type(eleTyp) is not type(prevEleTyp):
                    #     if type(eleTyp) is IntegerType and type(prevEleTyp) is FloatType:
                    #         typInfer = FloatType()
                    #     elif type(eleTyp) is FloatType and type(prevEleTyp) is IntegerType:
                    #         typInfer = FloatType()    
                    #     else:
                        raise IllegalArrayLiteral(ast)
            prevEleTyp = eleTyp
            if(typInfer is None): typInfer = eleTyp
        if(type(typInfer) is ArrayType):
            dim.append(numberOfEle)
            for i in typInfer.dimensions:
                dim.append(i)
            # for i in eleTyp.dimensions:
            #     dim.append(i)
            return ArrayType(dim, typInfer.typ)
        return ArrayType([numberOfEle], typInfer)
                
    def visitFuncCall(self, ast, param): 
        params_list = None
        return_typ = None
        for func in StaticChecker.funcList:
            if(func.name == ast.name):
                params_list = func.typ.params_list
                return_typ = func.typ.return_typ
                break
        if(params_list == None): 
            raise Undeclared(Function(), ast.name)

        if(len(ast.args)!=len(params_list)):
            raise TypeMismatchInExpression(ast)

        for i in range(len(ast.args)):
            argu_typ = self.visit(ast.args[i],param)
            param_typ = params_list[i].typ
            if(type(argu_typ) is not type(param_typ)):
                if type(param_typ) is AutoType:
                    for func in StaticChecker.funcList:
                        if(func.name == ast.name):
                            func.typ.params_list[i].typ = argu_typ
                elif type(argu_typ) is FloatType and type(param_typ) is IntegerType:
                    continue
                elif type(argu_typ) is IntegerType and type(param_typ) is FloatType:
                    continue
                else:
                    raise TypeMismatchInExpression(ast)
        
        if type(return_typ) is VoidType:
            raise TypeMismatchInExpression(ast)

        return FuncType(return_typ, params_list)
        
    def visitAssignStmt(self, ast, param): 

        lhs_typ = self.visit(ast.lhs, param)
        rhs_typ = self.visit(ast.rhs, param)
        # print(lhs_typ, rhs_typ)
        if type(lhs_typ) is ArrayType or type(lhs_typ) is VoidType:
            raise TypeMismatchInStatement(ast)
        elif type(lhs_typ) is AutoType:
            if type(rhs_typ) is VoidType or type(rhs_typ) is AutoType:
                raise TypeMismatchInStatement(ast)
            else:
                if type(rhs_typ) is FuncType:
                    typInfer = rhs_typ.return_typ
                Utils.inferClass(param, ast.lhs.name, typInfer)
        else:
            if type(rhs_typ) is FuncType:
                # print(type(rhs_typ.return_typ))
                if type(rhs_typ.return_typ) is AutoType:
                    typInfer = lhs_typ
                    Utils.inferClass(param, ast.rhs.name, typInfer)
                elif type(rhs_typ.return_typ) is not type(lhs_typ):
                    if type(rhs_typ.return_typ) is not IntegerType or type(lhs_typ) is not FloatType:
                        raise TypeMismatchInStatement(ast)
            else:
                if type(rhs_typ) is not type(lhs_typ):
                    if type(rhs_typ) is not IntegerType or type(lhs_typ) is not FloatType:
                        raise TypeMismatchInStatement(ast)


    def visitBlockStmt(self, ast, param):
        StaticChecker.return_lst.append(False)
        if(ast.body == []):
            if(StaticChecker.inheritFuncname is not None):
                funcname = StaticChecker.inheritFuncname
                StaticChecker.inheritFuncname = None
                raise InvalidStatementInFunction(funcname)
        for element in ast.body:
            self.visit(element, param)
            if(StaticChecker.inheritFuncname is not None):
                funcname = StaticChecker.inheritFuncname
                StaticChecker.inheritFuncname = None
                raise InvalidStatementInFunction(funcname)
        StaticChecker.return_lst.pop()        
         
    def visitIfStmt(self, ast, param): 

        cond_stmt = self.visit(ast.cond, param)
        
        if type(cond_stmt) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        newEnv = [[]] + param
        StaticChecker.return_lst.append(False)
        self.visit(ast.tstmt, newEnv)
        StaticChecker.return_lst.pop()
        
        if(ast.fstmt is not None):
            StaticChecker.return_lst.append(False)
            self.visit(ast.fstmt, newEnv)
            StaticChecker.return_lst.pop()
    
    def visitForStmt(self, ast, param): 
        self.visit(ast.init, param)
        svTyp = self.visit(ast.init.lhs, param)
        
        if type(svTyp) is not IntegerType:
            raise TypeMismatchInStatement(ast)
        cond_stmt = self.visit(ast.cond, param)
        
        if type(cond_stmt) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        upd = self.visit(ast.upd, param)
        
        if type(upd) is not IntegerType:
            raise TypeMismatchInStatement(ast)
        StaticChecker.inLoop = True
        newEnv = [[]] + param
        StaticChecker.return_lst.append(False)
        self.visit(ast.stmt, newEnv)
        StaticChecker.return_lst.pop()
        StaticChecker.inLoop = False
    
    def visitWhileStmt(self, ast, param): 
        cond_stmt = self.visit(ast.cond, param)
        if type(cond_stmt) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        StaticChecker.inLoop = True
        newEnv = [[]] + param
        StaticChecker.return_lst.append(False)
        self.visit(ast.stmt, newEnv)
        StaticChecker.return_lst.pop()
        StaticChecker.inLoop = False

    def visitDoWhileStmt(self, ast, param): 
        StaticChecker.inLoop = True
        newEnv = [[]] + param
        self.visit(ast.stmt, newEnv)
        StaticChecker.inLoop = False
        cond_stmt = self.visit(ast.cond, param)
        
        if type(cond_stmt) is not BooleanType:
            raise TypeMismatchInStatement(ast)

    def visitBreakStmt(self, ast, param): 
        if(StaticChecker.inLoop == False):
            raise MustInLoop(ast)
        StaticChecker.inLoop = False
    
    def visitContinueStmt(self, ast, param): 
        if(StaticChecker.inLoop == False):
            raise MustInLoop(ast)
        StaticChecker.inLoop = True

    def visitReturnStmt(self, ast, param): 
        if(StaticChecker.return_lst[-1]==False):
            return_typ = self.visit(ast.expr, param)
            for func in StaticChecker.funcList:
                if(func.name == StaticChecker.cur_func):
                    if type(func.typ.return_typ) is AutoType:
                        func.typ.return_typ = return_typ
                        StaticChecker.return_lst[-1] = True
                    elif type(return_typ) is not type(func.typ.return_typ):
                        raise TypeMismatchInStatement(ast)
                    else:
                        StaticChecker.return_lst[-1] = True
                    break


    def visitCallStmt(self, ast, param): 
        params_list = None
        return_typ = None
        flag = False
        funcName = ast.name
        if(ast.name in ['readInteger', 'readFloat', 'readBoolean', 'readString']):
            for func in StaticChecker.funcList:
                return_typ = func.typ.return_typ
                flag = True
        elif (ast.name == 'super'):
            superFunc = None
            for func in StaticChecker.funcList:
                if(func.name == StaticChecker.inheritFuncname):
                    superFunc = func.inherit
            for func in StaticChecker.funcList:
                if(func.name == superFunc):
                    params_list = func.typ.params_list
                    # print(superFunc)
                    return_typ = func.typ.return_typ
                    funcName = StaticChecker.inheritFuncname
                    StaticChecker.inheritFuncname = None
                    break
        elif(ast.name == 'preventDefault'):
            
            if(ast.args != []):
                StaticChecker.inheritFuncname = None
                raise TypeMismatchInStatement(ast.name)
            else:
                
                if(StaticChecker.inheritFuncname is not None):

                    StaticChecker.inheritFuncname = None
                    flag = True
        else:
            for func in StaticChecker.funcList:
                if(func.name == ast.name):
                    params_list = func.typ.params_list
                    return_typ = func.typ.return_typ
                    break
        if(flag == False):
            if(params_list == None): 
                raise Undeclared(Function(), ast.name)
            
            if(len(ast.args)!=len(params_list)):
                raise TypeMismatchInStatement(ast)

            for i in range(len(ast.args)):
                args_typ = self.visit(ast.args[i],param)
                if(type(args_typ) is not type(params_list[i].typ)):
                    if type (params_list[i].typ) is AutoType:
                        for func in StaticChecker.funcList:
                            if(func.name == funcName):
                                func.typ.params_list[i].typ = args_typ
                    elif type(args_typ) is FloatType and type(params_list[i].typ) is IntegerType:
                        continue
                    elif type(args_typ) is IntegerType and type(params_list[i].typ) is FloatType:
                        continue
                    else:
                        raise TypeMismatchInStatement(ast)

            if type(return_typ) is AutoType:
                Utils.inferClass(param, ast.name, VoidType())


    def visitVarDecl(self, ast, param): 
        for symbol in param[0]:
            if symbol.name == ast.name:
                raise Redeclared(Variable(),ast.name)        
        if ast.init is None:
            if type(ast.typ) is AutoType:
                raise Invalid(Variable(),ast.name)
            if type(ast.typ) is ArrayType:
                if type(ast.typ.typ) is AutoType:
                    raise Invalid(Variable(),ast.name)
        else:
            initTyp = self.visit(ast.init, param)    
            if type(ast.typ) is FloatType:
                if type(initTyp) is FuncType:
                    initTyp = initTyp.return_typ
                if type(initTyp) is not IntegerType and type(initTyp) is not FloatType:
                    raise TypeMismatchInVarDecl(ast)
            elif type(ast.typ) is ArrayType:
                # print(initTyp)
                if type(initTyp) is FuncType:
                    initTyp = initTyp.return_typ
                if initTyp.dimensions != ast.typ.dimensions:
                    # print(initTyp.dimensions, ast.typ.dimensions)
                    raise TypeMismatchInVarDecl(ast)
                if type(initTyp.typ) is not type(ast.typ.typ):
                    if type(ast.typ.typ) is AutoType:
                        ast.typ = initTyp
                    else:
                        raise TypeMismatchInVarDecl(ast)
            elif type(ast.typ) is AutoType:
                if type(initTyp) is FuncType:
                    initTyp = initTyp.return_typ
                ast.typ = initTyp
            elif type(ast.typ) is not type(initTyp): 
                if type(initTyp) is FuncType:
                    initTyp = initTyp.return_typ
                if type(ast.typ) is not type(initTyp):
                    if type(initTyp) is AutoType:
                        Utils.inferClass(param, ast.init.name, ast.typ)
                    elif type(initTyp) is VoidType:
                        raise TypeMismatchInExpression(ast.init)
                    elif type(initTyp) is AutoType:
                        Utils.inferClass(param, ast.init.name, ast.typ)
                    else:
                        raise TypeMismatchInVarDecl(ast)
        param[0].append(Symbol(ast.name, ast.typ))

    def visitParamDecl(self, ast, param):
        for symbol in param[0]:
            if symbol.name == ast.name:
                # print(symbol.inherit)
                if(symbol.inherit == True):
                    raise Invalid(Parameter(),symbol.name)
                else:
                    raise Redeclared(Parameter(),ast.name)
        param[0].append(Symbol(ast.name, ast.typ))

    def visitFuncDecl(self, ast, param): 
        StaticChecker.inheritFuncname = None
        if ast.name in ['readInteger', 'readFloat', 'readBoolean', 'readString', 'printInteger', 'printBoolean', 'printString', 'writeFloat', 'preventDefault', 'super']:
            raise Redeclared(Function(),ast.name)
        for symbol in param[0]:
            if symbol.name == ast.name:
                raise Redeclared(Function(),ast.name)
        newEnv = [[]] + param
        if(ast.inherit is not None):
            for func in StaticChecker.funcList:
                if func.name == ast.inherit:
                    StaticChecker.inheritFuncname = ast.name
                    for par in func.typ.params_list:
                        if(par.inherit == True):
                            newEnv[0].append(Symbol(par.name, par.typ, par.inherit))
                    break
            # print(StaticChecker.inheritFuncname)
            if StaticChecker.inheritFuncname is None:
                raise Undeclared(Function, ast.inherit)
        for para in ast.params:
            self.visit(para, newEnv)
        StaticChecker.cur_func = ast.name
        StaticChecker.return_lst = []
        self.visit(ast.body, newEnv)
        for func in StaticChecker.funcList:
            if func.name == ast.name:
                param[0].append(func)
        

        # lst_params = []
        # for para in ast.params:
        #     for symbol in newEnv[0]:
        #         if para.name == symbol.name:
        #             lst_params.append(symbol.typ)
        # param[0].append(Symbol(ast.name, FuncType(ast.return_type, lst_params), ast.inherit))

        # typTemp = [ast.return_type, lst_params, ast.inherit]
        # param[0][ast.name] = typTemp

    
    def visitProgram(self, ast, param): 
        StaticChecker.inLoop = False
        flag = False
        funcCheck = getEnv()
        StaticChecker.funcList = funcCheck.visit(ast, [])
        for decl in ast.decls:
            self.visit(decl, param)
        for par in StaticChecker.funcList:
            if(par.name == 'main') and par.typ.params_list == []:
                flag = True
        if(flag == False):
            raise NoEntryPoint()
        return ''