

def find_and_assign(name, type_val, o):
    for scope in o:
        if name in scope:
            scope[name] = type_val
            break

from functools import reduce
class StaticCheck(Visitor):

    # class Program: #decl:List[VarDecl],stmts:List[stmt]
    def visitProgram(self,ctx:Program,o):
        o = [{}]
        [self.visit(i,o) for i in ctx.decl]
        [self.visit(i,o) for i in ctx.stmts]

    # class VarDecl: #name:str
    def visitVarDecl(self,ctx:VarDecl,o):
        if ctx.name in o[0]:
            raise Redeclared(ctx)

        o[0][ctx.name] = None
        return o

    # class FuncDecl(Decl): 
    # name:str,     
    # param:List[VarDecl],    
    # local:List[Decl],
    # stmts:List[Stmt]    
    def visitFuncDecl(self,ctx:FuncDecl,o):
        if ctx.name in o[0]:
            raise Redeclared(ctx)

        o[0][ctx.name] = []
        temp = [{}] + o
        [self.visit(i,temp) for i in ctx.param]
        [self.visit(i,temp) for i in ctx.local]
        [self.visit(i,temp) for i in ctx.stmts]
        o[0][ctx.name] = [temp[0][param.name] for param in ctx.param]
        return o

    # class Assign(Stmt): #lhs:Id,rhs:Exp
    def visitAssign(self,ctx:Assign,o):
        rhs = self.visit(ctx.rhs, o)
        lhs = self.visit(ctx.lhs, o)

        if lhs is None:
            if rhs is None:
                raise TypeCannotBeInferred(ctx)
            else:
                find_and_assign(ctx.lhs.name, rhs, o)
        elif rhs is None:
            find_and_assign(ctx.rhs.name, lhs, o)
        elif lhs != rhs:
            raise TypeMismatchInStatement(ctx)
        return o

    # class CallStmt(Stmt): #name:str,args:List[Exp]
    def visitCallStmt(self,ctx:CallStmt,o):
        param_list = None
        for scope in o:
            if ctx.name in scope and type(scope[ctx.name]) is list:
                param_list = scope[ctx.name]
                break
        if param_list is None:
            raise UndeclaredIdentifier(ctx.name)

        args_list = [self.visit(arg, o) for arg in ctx.args]
        num_param = len(param_list)
        if len(args_list) != num_param:
            raise TypeMismatchInStatement(ctx)

        for i in range(num_param):
            if param_list[i] is None:
                if args_list[i] is None: 
                    raise TypeCannotBeInferred(ctx)
                else:
                    param_list[i] = args_list[i]
            elif args_list[i] is None:
                find_and_assign(ctx.args[i].name, param_list[i], o)
            elif args_list[i] != param_list[i]:
                raise TypeMismatchInStatement(ctx)
        return o
  



    def visitIntLit(self,ctx:IntLit,o):
        return int
    def visitFloatLit(self,ctx,o):
        return float

    def visitBoolLit(self,ctx,o):
        return bool

    # class Id(Exp): #name:str
    def visitId(self,ctx,o):
        for scope in o:
            if ctx.name in scope:
                return scope[ctx.name]
        raise UndeclaredIdentifier(ctx.name)