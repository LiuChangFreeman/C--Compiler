"""Define names for all type symbols known in the standard interpreter.

Types that are part of optional modules (e.g. array) are not listed.
"""
import sys

# Iterators in Python aren't a matter of type but of protocol.  A large
# and changing number of builtin types implement *some* flavor of
# iterator.  Don't check the type!  Use hasattr to check for both
# "__iter__" and "next" attributes instead.

NoneType = type(None)
TypeType = type
ObjectType = object

IntType = int
FloatType = float
BooleanType = bool
try:
    ComplexType = complex
except NameError:
    pass

StringType = str

try:               # Python 2
    BufferType = buffer
    FileType = file
    LongType = long
    StringTypes = basestring
    UnicodeType = unicode
    XRangeType = xrange
except NameError:  # Python 3
    from io import IOBase
    BufferType = memoryview
    FileType = IOBase
    LongType = int
    StringTypes = (StringType,)
    UnicodeType = str
    XRangeType = range

TupleType = tuple
ListType = list
DictType = DictionaryType = dict

def _f(): pass
FunctionType = type(_f)
LambdaType = type(lambda: None)         # Same as FunctionType
CodeType = type(_f.func_code)

def _g():
    yield 1
GeneratorType = type(_g())

class _C:
    def _m(self): pass
ClassType = type(_C)
UnboundMethodType = type(_C._m)         # Same as MethodType
_x = _C()
InstanceType = type(_x)
MethodType = type(_x._m)

BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)     # Same as BuiltinFunctionType

ModuleType = type(sys)

try:
    raise TypeError
except TypeError:
    tb = sys.exc_info()[2]
    TracebackType = type(tb)
    FrameType = type(tb.tb_frame)
    del tb

SliceType = slice
EllipsisType = type(Ellipsis)

DictProxyType = type(TypeType.__dict__)
NotImplementedType = type(NotImplemented)

# For Jython, the following two types are identical
GetSetDescriptorType = type(FunctionType.func_code)
MemberDescriptorType = type(FunctionType.func_globals)

del sys, _f, _g, _C, _x                           # Not for export
