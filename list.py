from collections import namedtuple
from functools import partial
from context import Context, Implementation, ImplPattern, TypeVar, Type, Types, global_context

_ = global_context

###### INTERFACES #######

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
    #def Empty()
    #def Append(ls, x)

class IotaLists(object):
    pass
    #def Create(num_elements)

class Main(object):
    pass
    #def Main()

###### CONCRETE IMPLEMENTATIONS #######

Iota = namedtuple('Iota', 'num_elements')
IotaT = Types.NewType()

class IotaListsImpl(IotaLists):
    @staticmethod
    def Create(num_elements):
        return Iota(num_elements)
        
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

_.Add(Implementation('IotaLists', (IotaT,), IotaListsImpl))
_.Add(Implementation('FiniteList', (IotaT,), IotaIsFinite))
_.Add(Implementation('RandomAccess', (IotaT,), IotaRandomAccess))


###### GENERIC IMPLEMENTATIONS #######

def GenPrintList(finite, raccess, types, _):
    L, = types
    class PrintRAccessList(PrintList):
        @staticmethod
        def Print(ls):
            strs = [str(i) for i in range(0, finite.Size(ls))]
            print("[%s]" % (", ".join(strs)))
    return [Implementation('PrintList', (L,), PrintRAccessList)]

_.AddGeneric('GenPrintList', GenPrintList, finite=ImplPattern('FiniteList', (TypeVar(0),)), raccess=ImplPattern('RandomAccess', (TypeVar(0),)))

def GenMain(iotas, printls, types, _):
    class MainImpl(Main):
        @staticmethod
        def Main():
            iota = iotas.Create(3)
            printls.Print(iota)
    return [Implementation('Main', (), MainImpl)]
_.AddGeneric('GenMain', GenMain, iotas=ImplPattern('IotaLists', (TypeVar(0),)), printls=ImplPattern('PrintList', (TypeVar(0),)))

    
###### QUERY A 'MAIN' #######

_.Query(main=ImplPattern('Main', ()))[0][1]['main'].Main()