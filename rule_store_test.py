import unittest
from unification_test import TupleUnification
from rule_store import RuleStore, Rule, Match, DerivedFacts

class TestRuleStore(unittest.TestCase):
    def setUp(self):
        self.rules = RuleStore(TupleUnification())
        
    def _test_TriggerRules(self):
        n1 = ('1',)
        n2 = ('2',)
        n3 = ('3',)
        
        a1 = ('a', n1, n2)
        a2 = ('a', n2, n3)
        a3 = ('a', n3, n2)
        a4 = ('a', n1, n3)
        b1 = ('b', n1)
        b2 = ('b', n2)
        c1 = ('c', n1, n1, n1)
        d = ('d',)
        
        qa1 = ('a', 1, 2)
        qa2 = ('a', 2, 1)
        qb = ('b', 1)
        
        r1_called_with = []
        def r1_callback(m):
            r1_called_with.append(m)
        r1 = Rule([qa1, qa2], r1_callback)
        self.rules.AddRule(r1)
        self.assertEqual(r1_called_with, [])
        
        for t in [a1, b1]:
          self.rules.AddFact(t)
        self.assertEqual(r1_called_with, [])
          
        for t in [a2, a3, b2, c1, d]:
          self.rules.AddFact(t)
        self.assertEqual(sorted(r1_called_with), [Match([a2, a3], [(1, n2), (2, n3)]), Match([a3, a2], [(1, n3), (2, n2)])])
          
        r2_called_with = []
        def r2_callback(m):
            r2_called_with.append(m)   
        r2 = Rule([qb], r2_callback)
        self.rules.AddRule(r2)
        
        self.assertEqual(sorted(r2_called_with), [Match([b1], [(1, n1)]), Match([b2], [(1, n2)])])
        
        self.rules.AddFact(a4)
        self.assertEqual(len(r1_called_with), 2)
          
    def test_Chain(self):
        hans = ('hans',)
        jenny = ('jenny',)
        markus = ('markus',)
        
        susan = ('susan',)
        anna = ('anna',)
        john = ('john',)
        
        english = ('english',)
        german = ('german',)
        
        f1 = ('childOf', hans, jenny)
        f2 = ('childOf', susan, anna)
        
        f3 = ('married', jenny, markus)
        f4 = ('married', john, anna)
        
        f5 = ('speaks', jenny, english)
        f6 = ('speaks', markus, german)
        
        f7 = ('speaks', anna, german)
        f8 = ('speaks', anna, english)
        f9 = ('speaks', john, english)
        
        r1 = Rule([('married', 1, 2)], lambda m: [self.rules.uni.Apply(m.substitutions, ('married', 2, 1))])
        r2 = Rule([('childOf', 1, 2), ('married', 2, 3)], lambda m: [self.rules.uni.Apply(m.substitutions, ('childOf', 1, 3))])
        
        def on_r3(m): 
            s = sorted(m.substitutions)
            if s[1][1] == s[2][1]:
                return []
            return [self.rules.uni.Apply(m.substitutions, ('speaks', 1, 4))]
        r3 = Rule([('childOf', 1, 2), ('childOf', 1, 3), ('speaks', 2, 4), ('speaks', 3, 4)], on_r3)
        
        for r in [r1, r2, r3]:
            self.rules.AddRule(r)
        for f in [f1, f2, f3, f4, f5, f6, f7, f8, f9]:
            self.rules.AddFact(f)
        
        matches = self.rules.MatchingFacts([('speaks', 1, 2)])
        facts = [m.facts[0] for m in matches]
        facts = set(facts) - set([f5, f6, f7, f8, f9])
        print('new matches:  ', facts)
        self.assertTrue(('speaks', susan, english) in facts)
        self.assertFalse(('speaks', hans, english) in facts)
        self.assertFalse(('speaks', hans, german) in facts)
        self.assertEqual(len(matches), 6)

if __name__ == '__main__':
    unittest.main()