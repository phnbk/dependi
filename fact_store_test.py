import unittest
from unification_test import TupleUnification
from fact_store import FactStore, DerivedFacts

class TestDerivedFacts(unittest.TestCase):
    def setUp(self):
        self.uni = TupleUnification()
        self.facts = FactStore()
    
    def AddFact(self, term):
        symbol, _ = self.uni.IsPred(term)
        self.facts.Add(symbol, term)
    
    def Matches(self, terms):
        matches = DerivedFacts(self.facts, self.uni, terms).MatchingFacts()
        result = []
        for (facts, substitions) in matches:
            result.append((facts, sorted(substitions)))
        return sorted(result)
        
    def test_ListenAndAdd(self):
        called_with = []
        def Listener(symbol, fact):
            called_with.append(symbol)
        
        n1 = ('1')
        n2 = ('2')
        a1 = ('a', n1, n2)
        a2 = ('a', n2, n1)
        
        self.AddFact(n1)
        self.facts.ListenFor('a', Listener)
        # Adding the same listener multiple times doesn't change anything.
        self.facts.ListenFor('a', Listener)
        self.assertEqual(called_with, [])
        
        self.AddFact(n2)
        self.assertEqual(called_with, [])
        
        self.AddFact(a1)
        self.assertEqual(called_with, ['a'])
        called_with = []
        
        self.AddFact(a2)
        self.assertEqual(called_with, [])
        
    def test_ListenForAllOfAndAdd(self):
        called = [0]
        def Listener():
            called[0] += 1
        
        n1 = ('1')
        n2 = ('2')
        n3 = ('3')
        a1 = ('a', n1, n2)
        a2 = ('a', n2, n1)
        b1 = ('b', n1)
        b3 = ('b', n3)
        
        self.AddFact(n1)
        self.facts.ListenForAllOf(['a', 'b'], Listener)
        self.AddFact(n2)
        self.AddFact(n3)
        self.AddFact(a1)
        self.AddFact(a2)
        self.assertEqual(called, [0])
        
        self.AddFact(b3)
        # Only the terms' symbols count and not their arguments.
        self.assertEqual(called, [1])
        called[0] = 0
        
        self.AddFact(b1)
        self.assertEqual(called, [0])
        
    def test_MatchingFacts(self):
        n1 = ('1',)
        n2 = ('2',)
        n3 = ('3',)
        
        a1 = ('a', n1, n2)
        a2 = ('a', n2, n3)
        a3 = ('a', n3, n2)
        b1 = ('b', n1)
        b2 = ('b', n2)
        c1 = ('c', n1, n1, n1)
        d = ('d')
        
        qa1 = ('a', 1, 2)
        qa2 = ('a', 2, 1)
        qb = ('b', 1)
        
        qd = ('d')
        
        
        self.assertEqual(self.Matches([qd]), [])
        
        for t in [a1, b1]:
          self.AddFact(t)
          
        self.assertEqual(self.Matches([qd]), [])
        
        self.assertEqual(self.Matches([qa1]), [
                          ([a1], [(1, n1), (2, n2)])
                         ])
        
        self.assertEqual(self.Matches([qa1, qa2]), [])
          
        for t in [a2, a3, b2, c1, d]:
          self.AddFact(t)
          
        self.assertEqual(self.Matches([qd]), [([qd], [])])
        
        self.assertEqual(self.Matches([qa1]), [
                          ([a1], [(1, n1), (2, n2)]),
                          ([a2], [(1, n2), (2, n3)]),
                          ([a3], [(1, n3), (2, n2)])
                         ])
                         
        self.assertEqual(self.Matches([qa1, qb]), [
                          ([a1, b1], [(1, n1), (2, n2)]),
                          ([a2, b2], [(1, n2), (2, n3)])
                         ])
                         
        self.assertEqual(self.Matches([qa1, qa2]), [
                           ([a2, a3], [(1, n2), (2, n3)]),
                           ([a3, a2], [(1, n3), (2, n2)])
                         ])

if __name__ == '__main__':
    unittest.main()