# Compiler
-------
基于 Python 的词法和LR(1)文法分析器

## 总体说明
* 编程语言:Python 2.7.11
* 编程平台:Ubuntu16.04
* 编程环境:sublime
* 完成的内容:实现了 3型文法的词法分析器和2 型文法的LR(1)语法分析器。
* 测试文法:一个类C语言的文法
* 测试程序:一个类C语言的程序。

## 文件说明
本程序共涉及7个文件, 现将其说明如下:

lexical_analyze.py    词法分析程序

syntax_analyze.py     语法分析程序

nfa_and_dfa.py        定义了 nfa 和 dfa 类以及其节点

lex_grammar.txt       词法文法文件

syn_grammar.txt       语法文法文件

source.cc             待分析的类C程序

token_table.data      词法分析输出的token表

## 词法文法说明
我构造了一个3型文法作为程序读入的词法的文法，为了简化读入操作，我将课本上的 ->(推出符)换成了 ‘:’, ‘:’的左侧是产生式的左部, 右侧是产生式的右部, 并且将空产生式的右部的埃普西隆用 $ 来代替。
我将token的类型大体分成了 identifier、limiter、operator、number、string 等五类, 并每一类设计了表达式和推导过程。

## 语法文法说明
直到开始写文法我才直到这个课设最难的是文法的构造, 自己YY了很久也没能设计出一个让自己满意且可用的文法, 所以中从 http://www.nongnu.org/hcb/ 这里参考了一下，最后写出来了一个2型文法。
跟词法的文法, 这里用 ‘:’ 来代替课本上的 –> 并且用 ‘$’ 来代替埃普西隆空产生式右部。

## 词法分析器说明
词法分析器接受一个3型文法, 接受3型文法后会分析其终结符和非终结符, 分析方法是: 对于非终结符, 很明显, 所有在产生式左部的符号都是非终结符, 那么终结符就是所有的符号集合与非终结符集合的差集.分析完终结符和非终结符之后根据课本算法构造 NFA， 然后根据课本的算法构造 DFA，至此文法的处理工作结束。
接下来分析待分析的程序, 对于读入的程序, 将每个字符一次输入到 DFA 里面，当 DFA 不能接受某个字符的时候判断当前状态是否是一个终结状态, 如果是则token分析成功, 否则词法分析失败。

## 语法分析器说明
语法分析器首先读入要分析的2型文法, 然后求出文法的终结符和非终结符, 求法与上面相同, 之后要求出每个文法符号的 first集，终结符的first 集是他本身，非终结符的 first 集的求解过程是一个记忆化搜索的过程。 然后为文法添加拓展的 S’->S,# 在此基础上进行拓展形成项目集 I0, 然后对项目集I0 进行推广, 同时构建 LR(1) 分析表。
有了 LR(1) 分析表后接下来的过程我们只需要一个一个的将词法分析生成的token读入到程序里面放在分析表中寻找移进或者归约操作即可, 如果最后的状态是 acc 则文法符合要求, 如果最后无法得到 acc，或者在分析表中找不到相应的操作, 则语法错误。

## 代码说明
### 工具类(nfa_and_dfa.py)
```python
class NFANode(object)                               # NFA的节点结构
    def __init__(self, name, _type)                 # 类的构造函数, 传入名称和类型
    def add_edge(self, alpha, target)               # 为节点添加边

class NFA(object)                                   # NFA 的结构
    def __init__(self)                              # 类的构造函数
    def get_target(self, cur_status, alpha)         # 从当前状态,输入一个字符返回下一个状态

class DFANode(object)                               # DFA 的节点结构
    def __init__(self, name, _type)                 # 类的构造函数, 传入名称和类型
    def add_edge(self, alpha, target)               # 为节点添加边

class LRDFANode(object)                             # LR(1)DFA的节点结构
    def __init__(self, set_id)                      # 类的构造函数, 传入节点的编号
    def add_object_set(self, id, left, right, index, tail)   # 为项目集添加产生式
    def add_object_set_by_set(self, object_set)              # 以一个集合的方式向项目集中添加产生式

class DFA(object)                                   # DFA 的结构类
    def __init__(self)                              # 构造函数
    def get_target(self, cur_status, alpha)         # 从当前状态,输入一个字符返回下一个状态
```
### 词法分析器(lexical_analyze.py)
```python
class LexicaAnalyze(object)                         # 与词法分析有关的操作
    def read_lex_grammar(self, file_name)           # 读取词法的文法, 参数为文法文件路径
    def create_nfa(self)                            # 根据输入的文法创建 nfa
    def get_create_nfa_node(name, _type)            # 创建新的节点或者返回一个已存在的节点
    def nfa_to_dfa(self)                            # 由 nfa 转向 dfa
    def get_create_dfaNode(name, _type) 		    # 创建新的节点或者返回一个已存在的节点
    def run_on_dfa(self, line,pos)					# 给定一行语句, 让其在dfa上跑生成 token
    def read_and_analyze(self, file_name)			# 读取待分析的句子并生成token_table
def main()											# 主函数调用, 创建 LexicaAnalyze 对象, 并完成词法分析操作
```
### 语法分析器(syntax_analyze.py)
```python
class SyntaxAnalyze(object)                         # 与语法分析相关的操作的类
    def __init__(self)                              # 构造函数
    def read_syntax_grammar(self, file_name)        # 读取语法分析需要的文法, 传入文件名
    def get_terminate_noterminate(self)             # 得到文法的非终结符和终结符
    def __get_first_set(self, cur_status, all_elem) # 递归得到一个非终结符的first 集
    def init_first_set(self)                        # 初始化所有符号的first集
    def create_lr_dfa(self)                         # 创建项目集 DFA, 同时构造分析表
    def create_get_lr_dfa_node(set_id)              # 创建新的节点或者得到一个已有的节点
    def expand_production(self, production,set)     # 通过一个产生式得到与其项目集
    def run_on_lr_dfa(self, tokens)                 # 分析 token_table 并返回结果
    def read_and_analyze(self, file_name)           # 读取token_table
def main()                                          # 主函数，创建 SyntaxAnalyze 对象并进行所有操作输出结果
```
### 运行
```shell
python lexical_analyze.py                           # 生成 token_table
python syntax_analyze.py                            # 输出语法分析结果
```
