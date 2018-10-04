from collections import namedtuple
from functools import partial
from context import Context, Implementation, ImplPattern, TypeVar, Type, Types

class AttributeView(object):
    def __init__(self, d):
        self.d = d
    def __getattr__(self, attr):
        return self.d.get(attr)


_ = Context()

class List(object):
    pass

class FiniteList(List):
    pass
    #def Size(ls)
    
class RandomAccess(List):
    pass
    #def At(ls, i)

class PrintList(List):
    pass
    #def Print(ls)

class Lists(object):
    pass
    #def Empty(self)
    #def Append(self, ls, x)

Iota = namedtuple('Iota', 'num_elements')

class IotaIsFinite(FiniteList):
    @staticmethod
    def Size(iota):
        return iota.num_elements
    
class IotaRandomAccess(RandomAccess):
    @staticmethod
    def At(iota, i):
        if i < 0 or i >= iota.num_elements:
            raise ValueError("%s out of bounds [0, %s)." %(i, iota.num_elements))
        return i

def MakeIota(num_elements):
    iota = Iota(num_elements)
    
    I = Types.NewType()
        
    _.Add(Implementation('FiniteList', (I,), IotaIsFinite))
    _.Add(Implementation('RandomAccess', (I,), IotaRandomAccess))
            
    return (iota, I)

def GenPrintList(finite, raccess, types):
    L, = types
    class PrintRAccessList(PrintList):
        @staticmethod
        def Print(ls):
            strs = [str(i) for i in range(0, finite.Size(ls))]
            print("[%s]" % (", ".join(strs)))
    return [Implementation('PrintList', (L,), PrintRAccessList)]

_.AddGeneric('GenPrintList', GenPrintList, finite=ImplPattern('FiniteList', (TypeVar(0),)), raccess=ImplPattern('RandomAccess', (TypeVar(0),)))

iota, I = MakeIota(3)
I_ = AttributeView(_.Query(print=ImplPattern('PrintList', (I,)))[0][1])
I_.print.Print(iota)