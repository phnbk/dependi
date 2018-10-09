from collections import namedtuple
from functools import partial
from context import Context, Implementation, ImplPattern, TypeVar, Type, Types, global_context

_ = global_context

###### INTERFACES #######

class Interface(object):
    def __init__(self, type_args):
        self.type_args = type_args

class MInterface(type):
    def __new__(cls, name, bases, namespace):
        type_slots = namespace['type_slots']
        if bases:
            raise ValueError('expected no base classes but got: %s' %(bases,))
        bases = (Interface,)
        def __init__(self, **kwargs):
            if kwargs.keys() != set(type_slots):
                raise ValueError('wrong type arguments. got: %s  expected %s'
                        % (kwargs.keys(), self.type_slots))
            
            type_args = tuple(kwargs[slot] for slot in type_slots)
            Interface.__init__(self, type_args)
        namespace['__init__'] = __init__
        result = type.__new__(cls, name, bases, namespace)
        return result
        
class Order(metaclass=MInterface):
    type_slots = ['T']
    #def Lt(a, b)

class List(metaclass=MInterface):
    type_slots = ['L', 'E']

class FiniteList(metaclass=Minterface):
    type_slots = ['L']
    #def Size(ls)
    
class RandomAccess(metaclass=MInterface):
    type_slots = ['L']
    #def At(ls, i)

class PrintList(object):
    pass
    #def Print(ls)

class Sorted(object):
    pass
    #def IsSorted(ls)

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

def NewImpl(ctx):
    def Decorate(cls):
        for iface in cls.interfaces:
            ctx.Add(Implementation(type(iface).__name__, iface.type_args, cls))
    return Decorate
        
IntT = Types.NewType()

Iota = namedtuple('Iota', 'num_elements')
IotaT = Types.NewType()

@NewImpl(_)
class IotaIsList:
    interfaces = [List(L=IotaT, E=IntT)]
    
@NewImpl(_)
class IotaListsImpl:
    interfaces = [IotaLists(T=IotaT)]
    def Create(num_elements):
        return Iota(num_elements)
        
@NewImpl(_)
class IotaIsFinite:
    interfaces = [FiniteList(L=IotaT)]
    def Size(iota):
        return iota.num_elements
    
@NewImpl(_)
class IotaRandomAccess:
    interfaces = [RandomAccess(L=IotaT)]
    def At(iota, i):
        if i < 0 or i >= iota.num_elements:
            raise ValueError("%s out of bounds [0, %s)." %(i, iota.num_elements))
        return i

@NewImpl(_)
class IntOrder:
    interfaces = [Order(T=IntT)]
    def Lt(a, b):
        return a < b



###### GENERIC IMPLEMENTATIONS #######

def GenPrintList(finite, raccess, types, _):
    L, = types
    class PrintRAccessList(PrintList):
        @staticmethod
        def Print(ls):
            strs = [str(raccess.At(ls, i)) for i in range(0, finite.Size(ls))]
            print("[%s]" % (", ".join(strs)))
    return [Implementation('PrintList', (L,), PrintRAccessList)]

_.AddGeneric(GenPrintList, finite=ImplPattern('FiniteList', (TypeVar(0),)), raccess=ImplPattern('RandomAccess', (TypeVar(0),)))

def GenSorted(order, list, finite, raccess, types, _):
    L, E = types
    class SortedImpl(Sorted):
        @staticmethod
        def IsSorted(ls):
            if finite.Size(ls) < 2:
                return True
            for i in range(0, finite.Size(ls) - 1):
                if not order.Lt(raccess.At(ls, i), raccess.At(ls, i+1)):
                    return False
            return True
    return [Implementation('Sorted', (L,), SortedImpl)]

_.AddGeneric(GenSorted,
    order=ImplPattern('Order', (TypeVar(1),)),
    list=ImplPattern('List', (TypeVar(0), TypeVar(1),)),
    finite=ImplPattern('FiniteList', (TypeVar(0),)),
    raccess=ImplPattern('RandomAccess', (TypeVar(0),)))

def GenMain(iotas, printls, sorted, types, _):
    class MainImpl(Main):
        @staticmethod
        def Main():
            iota = iotas.Create(3)
            print('is sorted: %s' % sorted.IsSorted(iota))
            printls.Print(iota)
    return [Implementation('Main', (), MainImpl)]
_.AddGeneric(GenMain,
    iotas=ImplPattern('IotaLists', (TypeVar(0),)),
    printls=ImplPattern('PrintList', (TypeVar(0),)),
    sorted=ImplPattern('Sorted', (TypeVar(0),)))

    
###### QUERY A 'MAIN' #######

_.Query(main=ImplPattern('Main', ()))[0][1]['main'].Main()