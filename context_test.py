import unittest
from context import Context, Implementation, ImplPattern, TypeVar, Type

class TestContext(unittest.TestCase):
    def test_TriggerGeneric(self):
        ctx = Context()
        
        def g1(a, types):
            print('g1: %s %s' % (a, types))
            return [Implementation('Concat', (types[0],), "FakeConcat(%s)" % a)]
            
        ctx.AddGeneric('g1', g1, a=ImplPattern('Append', (TypeVar(0),)))
        
        ctx.Add(Implementation('Append', (Type(0),), "FakeAppend"))
        
        self.assertEqual(ctx.Query(a=ImplPattern('Append', (TypeVar(0),)),c=ImplPattern('Concat', (TypeVar(0),))),
            [((Type(0),), {
                'a': 'FakeAppend',
                'c': 'FakeConcat(FakeAppend)'}
            )])
        
if __name__ == '__main__':
    unittest.main()