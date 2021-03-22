#coding:utf-8
from __future__ import print_function
from prettytable import PrettyTable
class Node(object):
    def __init__(self, value):
        self.childs = []
        self.parent = None
        self.value = value
    def addchild(self,value):
        self.childs.append(value)
    def setparent(self,value):
        self.parent=value
    def getdic(self):
        return self.value
    def traves(self):
        dic={}
        key=self.value.values()[0]
        dic[key]=[]
        for child in self.childs:
            dic[key].append(child.traves())
        return dic
def GenerateGramerTupleGroup(file):
    GrammerTupleGroup=[]
    lines=file.split('\n')
    for line in lines:
        AfterEffect=line.strip(' ').strip('\t').replace(' ','').replace('\r','')
        NonterminalSymbol=AfterEffect.split('->')[0]
        RightExpression=AfterEffect.split('->')[1]
        Individals=RightExpression.split('|')
        RightExpressionGroup=[]
        for individal in Individals:
            RightExpressionGroup.append(individal)
        GrammerTuple=[NonterminalSymbol,RightExpressionGroup]
        GrammerTupleGroup.append(GrammerTuple)
    return GrammerTupleGroup
def GenerateTerminalSymbolGroup(file):
    TerminalSymbolGroup=[]
    lines=file.split('\n')
    for line in lines:
        line.strip(' ').strip('\t')
        list=line.split(' ')
        for item in list:
            TerminalSymbolGroup.append(item)
    return TerminalSymbolGroup
def GenerateVTs():
    for NonTerminal in NonterminalSymbolGroup:
        FirstDic={}
        LastDic={}
        FirstDic['item']=NonTerminal
        FirstDic['type']=[]
        LastDic['item']=NonTerminal
        LastDic['type']=[]
        for item in ProductionGroup:
            if(item[0]==NonTerminal):
                RightExpressionGroup=item[1]
                for RightExpression in RightExpressionGroup:#每一句单独分析
                    SplitResult=SplitRightExpression(RightExpression)
                    cnt=len(SplitResult)
                    #终结符在句首或者句尾
                    if (SplitResult[0].keys()[0] == "Terminal" and SplitResult[0].values()[0] not in FirstDic['type']):
                        FirstDic['type'].append(SplitResult[0].values()[0])
                    if (SplitResult[cnt-1].keys()[0] == "Terminal" and SplitResult[cnt-1].values()[0] not in LastDic['type']):
                        LastDic['type'].append(SplitResult[cnt-1].values()[0])
                    # 非终结符在句首或者句尾
                    if (SplitResult[0].keys()[0] == "Nonterminal"):
                        if(SplitResult[0].values()[0] not in FirstDic['type']):
                            FirstDic['type'].append(SplitResult[0].values()[0])#后续添加该非终结符的FIRSTVT
                        if(cnt>1 and SplitResult[1].keys()[0] == "Terminal"and SplitResult[1].values()[0] not in FirstDic['type']):
                            FirstDic['type'].append(SplitResult[1].values()[0])#添加第二个终结符到FIRSTVT
                    if (SplitResult[cnt-1].keys()[0] == "Nonterminal"):
                        if(SplitResult[cnt-1].values()[0] not in LastDic['type']):
                            LastDic['type'].append(SplitResult[cnt-1].values()[0])#后续添加该非终结符的LASTVT
                        if(cnt>1 and SplitResult[cnt-2].keys()[0] == "Terminal" and SplitResult[cnt-2].values()[0] not in LastDic['type']):
                            LastDic['type'].append(SplitResult[cnt - 2].values()[0])#添加倒数第二个终结符到LASTVT
        FIRSTVT.append(FirstDic)
        LASTVT.append(LastDic)
    for FirstDic in FIRSTVT:
        MakeUpFIRSTVT(FirstDic)
    for LastDic in LASTVT:
        MakeUpLASTVT(LastDic)
    return
def MakeUpFIRSTVT(FirstDic):
    TempDic=FirstDic
    for item in FirstDic['type']:
        if item in NonterminalSymbolGroup:
            TempDic['type'].remove(item)
            for tuple in FIRSTVT:
                if(tuple['item']==item):
                    temp=MakeUpFIRSTVT(tuple)
                    for terminal in temp['type']:
                        if(terminal not in FirstDic['type']):
                            TempDic['type'].append(terminal)
        else:
            continue
    return TempDic
def MakeUpLASTVT(LastDic):
    TempDic=LastDic
    for item in LastDic['type']:
        if item in NonterminalSymbolGroup:
            TempDic['type'].remove(item)
            for tuple in LASTVT:
                if(tuple['item']==item):
                    temp=MakeUpLASTVT(tuple)
                    for terminal in temp['type']:
                        if(terminal not in LastDic['type']):
                            TempDic['type'].append(terminal)
        else:
            continue
    return TempDic
def Judge():
    for item in ProductionGroup:
        NonterminalSymbolGroup.append(item[0])
        for things in item[1]:
            RightExpressionGroup.append(things)
    IsOpPre=True
    for individal in RightExpressionGroup:
        items=SplitRightExpression(individal)
        for i in range(len(items)):
            if(items[i] in NonterminalSymbolGroup and items[i+1] in NonterminalSymbolGroup and i<len(items)-1):
                IsOpPre=False
                break
    if(IsOpPre):
        print("输入符合算符文法")
    else:
        print("输入不符合算符文法")
def GenerateSymbolIndexTable():
    for i in range(len(TerminalSymbolGroup)):
        SymbolIndexTable[i]=TerminalSymbolGroup[i]
        SymbolIndexTableReverse[TerminalSymbolGroup[i]]=i
    return SymbolIndexTable
def SplitRightExpression(RightExpression):
    result=[]
    while(len(RightExpression)>0):
        for Terminal in TerminalSymbolGroup:
            index=RightExpression.find(Terminal)
            if(index==0):
                ItemDic = {}
                ItemDic['Terminal']=Terminal
                result.append(ItemDic)
                RightExpression=RightExpression[index +len(Terminal):]
                break
        for Nonterminal in NonterminalSymbolGroup:
            index=RightExpression.find(Nonterminal)
            if(index==0):
                ItemDic = {}
                ItemDic['Nonterminal']=Nonterminal
                result.append(ItemDic)
                RightExpression = RightExpression[index +len(Nonterminal):]
                break
    return result
def GeneratePrecedenceRelationTable():
    IsOpPre=True
    for GramerTuple in ProductionGroup:
        RightExpressionGroup = GramerTuple[1]
        for RightExpression in RightExpressionGroup:
            SplitGroup=SplitRightExpression(RightExpression)
            n=len(SplitGroup)
            for i in range(0,n-1):
                if(SplitGroup[i].keys()[0] == "Terminal" and SplitGroup[i+1].keys()[0] == "Terminal"):
                    x=SymbolIndexTableReverse[SplitGroup[i].values()[0]]
                    y=SymbolIndexTableReverse[SplitGroup[i+1].values()[0]]
                    if(PrecedenceRelationTable[x][y]!=""):
                        IsOpPre=False
                    PrecedenceRelationTable[x][y]="="
                if(i+2<=n-1 and SplitGroup[i].keys()[0] == "Terminal" and SplitGroup[i+1].keys()[0] == "Nonterminal" and SplitGroup[i+2].keys()[0] == "Terminal"):
                    x=SymbolIndexTableReverse[SplitGroup[i].values()[0]]
                    y=SymbolIndexTableReverse[SplitGroup[i+2].values()[0]]
                    if(PrecedenceRelationTable[x][y]!=""):
                        IsOpPre=False
                    PrecedenceRelationTable[x][y]="="
                if(SplitGroup[i].keys()[0] == "Terminal" and SplitGroup[i+1].keys()[0] == "Nonterminal"):
                    Collection=[]
                    for FirstDic in FIRSTVT:
                        if(FirstDic['item']==SplitGroup[i+1].values()[0]):
                            Collection=FirstDic['type']
                            break
                    x=SymbolIndexTableReverse[SplitGroup[i].values()[0]]
                    for item in Collection:
                        y=SymbolIndexTableReverse[item]
                        if (PrecedenceRelationTable[x][y] != ""):
                            IsOpPre = False
                        PrecedenceRelationTable[x][y]="<"
                if(SplitGroup[i].keys()[0] == "Nonterminal" and SplitGroup[i+1].keys()[0] == "Terminal"):
                    Collection=[]
                    for LastDic in LASTVT:
                        if(LastDic['item']==SplitGroup[i].values()[0]):
                            Collection=LastDic['type']
                            break
                    y=SymbolIndexTableReverse[SplitGroup[i+1].values()[0]]
                    for item in Collection:
                        x=SymbolIndexTableReverse[item]
                        if (PrecedenceRelationTable[x][y] != ""):
                            IsOpPre = False
                        PrecedenceRelationTable[x][y]=">"
    return IsOpPre
def PrintPrecedenceRelationTable():
    title=[" "]
    for i in range(len(TerminalSymbolGroup)):
        title.append(SymbolIndexTable[i])
    x = PrettyTable(title)
    for i in range(len(TerminalSymbolGroup)):
        row=[SymbolIndexTable[i]]
        for j in range(len(TerminalSymbolGroup)):
            row.append(PrecedenceRelationTable[i][j])
        x.add_row(row)
    print(x)
    return
def MakeSyntacticAnalyse(code):
    def UpdateT(T):
        while (stack[T] in NonterminalSymbolGroup):
            T = T - 1
        return T
    source=[]
    stack=[]
    splitcode=SplitRightExpression(code)
    NonterminalSymbolGroup.append('N')
    for char in splitcode:
        source.append(char.values()[0])
    stack.append('#')
    AnalysisRows.append(['0','#',code,'','移进'])
    count=1
    while(1):
        LastT=len(stack)-1
        LastT=UpdateT(LastT)
        FirstT = LastT
        while(1):
            LastT = len(stack) - 1
            LastT = UpdateT(LastT)
            FirstT= LastT
            x = SymbolIndexTableReverse[stack[LastT]]
            while(1):
                PostT=FirstT
                FirstT = UpdateT(FirstT- 1)
                m=SymbolIndexTableReverse[stack[FirstT]]
                n=SymbolIndexTableReverse[stack[PostT]]
                if(PrecedenceRelationTable[m][n]=='<'or FirstT<0):
                    break
                if(PrecedenceRelationTable[m][n]=='='):
                    continue
            if(len(source)==0):
                break
            y=SymbolIndexTableReverse[source[0]]
            if(PrecedenceRelationTable[x][y]=='>'):
                break
            else:
                stack.append(source.pop(0))
                result = ''
                for item in stack:
                    result = result + item
                remain = ''
                for item in source:
                    remain = remain + item
                row=[str(count), result, remain,'','移进']
                AnalysisRows.append(row)
                count = count + 1
        Expression=''
        for i in range(FirstT+1,len(stack)):
            Expression=Expression+stack[i]
        action=''
        if(Expression!=''):
            for GrammerTuple in ProductionGroup:
                Nonterminal=GrammerTuple[0]
                RightExpression=GrammerTuple[1]
                for individal in RightExpression:
                    Backup=Expression
                    BackupIndividal=individal
                    ReplaceGroup=SplitRightExpression(Expression)
                    Expression=''
                    ReplaceIndividalGroup = SplitRightExpression(individal)
                    individal=''
                    for dic in ReplaceGroup:
                        if(dic.keys()[0]=='Nonterminal'):
                            dic['Nonterminal']='N'
                        Expression+=dic.values()[0]
                    for dic in ReplaceIndividalGroup:
                        if(dic.keys()[0]=='Nonterminal'):
                            dic['Nonterminal'] = 'N'
                        individal+=dic.values()[0]
                    if(individal==Expression):
                        action= Nonterminal+'->'+BackupIndividal
                        temp=SplitRightExpression(''.join(stack).replace(Backup,'N'))
                        stack=[]
                        for item in temp:
                            stack.append(item.values()[0])
        result=''
        for item in stack:
            result=result+item
        remain=''
        for item in source:
            remain=remain+item
        row=[str(count),result,remain,action,'规约']
        AnalysisRows.append(row)
        count=count+1
        if(result in NonterminalSymbolGroup):
            break
    return
def GenerateReduceProcedureRows():
    for i in range(len(AnalysisRows)-1):
        AnalysisRows[i][3]=AnalysisRows[i+1][3]
        AnalysisRows[i][4]=AnalysisRows[i+1][4]
    AnalysisRows[len(AnalysisRows)-1][3] = ''
    AnalysisRows[len(AnalysisRows)-1][4] = '成功'
    tempresult=[]
    for row in AnalysisRows:
        num=int(row[0])
        stack=row[1]
        source=row[2]
        grammer=row[3]
        action=row[4]
        if(action=='规约'):
            temprow=[stack+source,grammer]
            tempresult.append(temprow)
    return  list(reversed(tempresult))
def MakeUpReduceProcedure(ReduceProcedureRows):
    title=["当前序列","推导文法"]
    table = PrettyTable(title)
    table.add_row(['S',''])
    AST=Node({'Nonterminal':'S'})
    previous=[AST]
    for row in ReduceProcedureRows:
        now=SplitRightExpression(row[0])
        original=''
        grammer=row[1]
        RightExpressionGroup=SplitRightExpression(grammer.split('->')[1])
        Nonterminal=grammer.split('->')[0]
        targetseria=''
        index=0
        for i in range(len(now)):
            if (now[i].keys()[0] == 'Nonterminal'):
                targetseria += 'N'
            elif (now[i].keys()[0] == 'Terminal'):
                targetseria += 'T'
        for i in range(len(previous)):
            if(previous[i].value.keys()[0]=='Nonterminal'):
                seria = ''
                for j in range(len(previous)):
                    if (j == i):
                        for k in range(len(RightExpressionGroup)):
                            if (RightExpressionGroup[k].keys()[0] == 'Nonterminal'):
                                seria += 'N'
                            elif (RightExpressionGroup[k].keys()[0] == 'Terminal'):
                                seria += 'T'
                    else:
                        if(previous[j].value.keys()[0]=='Nonterminal'):
                            seria+='N'
                        elif(previous[j].value.keys()[0]=='Terminal'):
                            seria+='T'
                if(seria==targetseria):
                    index=i
                    break
        if(previous[index].value.values()[0]!=Nonterminal):
            TempNode=Node({'Nonterminal':Nonterminal})
            previous[index].addchild(TempNode)
            TempNode.parent=previous[index]
            before=previous[index].value.values()[0]
            del previous[index]
            previous.insert(index,TempNode)
            makeup=''
            for i in range(len(previous)):
                makeup = makeup + previous[i].value.values()[0]
            row=[makeup,before+'->'+Nonterminal]
            table.add_row(row)
        tuples = SplitRightExpression(grammer.split('->')[1])
        ReplaceGroup=[]
        for tuple in tuples:
            TempNode = Node(tuple)
            TempNode.parent = previous[index]
            previous[index].addchild(TempNode)
            ReplaceGroup.append(TempNode)
        del previous[index]
        for i in range(len(ReplaceGroup)):
            previous.insert(index+i,ReplaceGroup[i])
        for i in range(len(previous)):
            original=original+previous[i].value.values()[0]
        row=[original,grammer]
        table.add_row(row)
    print(table)
    dic=AST.traves()
    #PrintTree(dic,0)
    return
def PrintTree(node, depth):
    for i in range(depth):
        print(' | '),
    print('->', end=node.keys()[0])
    if(len(node.values()[0])==1 and len(node.values()[0][0].values()[0])==0):
        print('->', end=node.values()[0][0].keys()[0])
    else:
        print('')
        for child in node.values()[0]:
           PrintTree(child , depth + 1)
FIRSTVT = []
LASTVT = []
TerminalSymbolGroup=[]
NonterminalSymbolGroup=[]
ProductionGroup=[]
SymbolIndexTable={}
SymbolIndexTableReverse={}
PrecedenceRelationTable=[]
AnalysisRows=[]
if __name__=='__main__':
    #code = 'num+num*num+(real/num)*num-real#'
    code='(((a,a),^,(a)),a)#'
    code='id+(((id*id)+id)*id+id)#'
    print(code)
    TerminalSymbolFile=open('terminalsymbol.txt','rb')
    GrammerFile=open('grammer.txt','rb')
    TerminalSymbolGroup=GenerateTerminalSymbolGroup(TerminalSymbolFile.read())
    PrecedenceRelationTable = [["" for x in range(len(TerminalSymbolGroup))] for y in range(len(TerminalSymbolGroup))]
    ProductionGroup=GenerateGramerTupleGroup(GrammerFile.read())
    RightExpressionGroup=[]
    Judge()
    GenerateVTs()
    GenerateSymbolIndexTable()
    IsOpPre=GeneratePrecedenceRelationTable()
    if(IsOpPre):
        print("输入符合算符优先文法")
    else:
        print("输入符合算符优先文法")
    PrintPrecedenceRelationTable()
    MakeSyntacticAnalyse(code)
    ReduceProcedureRows=GenerateReduceProcedureRows()
    title=["序号","符号栈","剩余队列","使用文法","动作"]
    Table = PrettyTable(title)
    for row in AnalysisRows:
        Table.add_row(row)
    print(Table)
    MakeUpReduceProcedure(ReduceProcedureRows)






