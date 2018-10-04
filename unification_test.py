import unittest
from unification import Unification

class TupleUnification(Unification):
    def IsVar(self, term):
        if isinstance(term, int):
            return term
        else:
            return None
    
    def IsPred(self, term):
        if isinstance(term, int):
            return None
        else:
            return (term[0], term[1:])
    
    def ReplaceArgs(self, pred, args):
        return (pred[0],) + tuple(args)
            
class TestUnification(unittest.TestCase):
    def setUp(self):
        self.uni = TupleUnification()
        
    def test_Occurs(self):
        t = ('a', ('b', 1, ('c',)), ('a', 2))
        self.assertTrue(self.uni.Occurs(1, t))
        
    def test_Substitute(self):
        t = ('a', ('b', 1, ('c',)), ('a', 2, ('d', 2, 2)))
        s = ('e',)
        u = ('a', ('b', 1, ('c',)), ('a', ('e',), ('d', ('e',), ('e',))))
        self.assertEqual(self.uni.Substitute(s, 2, t), u)
        
    def test_Apply_Empty(self):
        t = ('a', 1)
        self.assertEqual(self.uni.Apply([], t), t)
        
    def test_UnifyOne1(self):
        a = ('a', ('a', 2), ('b', ('c',), 1))
        b = ('a', ('a', 1), ('b', 2    , 2))
        self.assertEqual(self.uni.UnifyOne(a, b),
           [(2, 1), (1, ('c',)) ])
           
    def test_UnifyOne2(self):
        a = ('a', 4, ('c', 4), 2       , 1       )
        b = ('a', 4, 3       , ('b', 3), ('a', 2))
        s = [(3, ('c', 4)), (2, ('b', ('c', 4))), (1, ('a', ('b', ('c', 4))))]
        ab = ('a', 4, ('c', 4), ('b', ('c', 4)), ('a', ('b', ('c', 4))))
        self.assertEqual(self.uni.UnifyOne(a, b), s)
        self.assertEqual(self.uni.Apply(s, a), ab)
        self.assertEqual(self.uni.Apply(s, b), ab)
        
    def test_UnifyOne3(self):
        a = ('a', 1       , 2       , ('c', 4), 4)
        b = ('a', ('a', 2), ('b', 3), 3       , 4)
        s = [(1, ('a', 2)), (2, ('b', 3)), (3, ('c', 4))]
        ab = ('a', ('a', ('b', ('c', 4))), ('b', ('c', 4)), ('c', 4), 4)
        self.assertEqual(self.uni.UnifyOne(a, b), s)
        self.assertEqual(self.uni.Apply(s, a), ab)
        self.assertEqual(self.uni.Apply(s, b), ab)
    
    def test_Unify_Empty(self):
        self.assertEqual(self.uni.Unify([]), [])

if __name__ == '__main__':
    unittest.main()