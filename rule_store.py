from functools import partial
from collections import namedtuple
from fact_store import DerivedFacts, FactStore, Match
from copy import deepcopy

# conclusion: a function from Match to a list of facts to add to the store.
Rule = namedtuple('Rule', 'premise conclusion')

class RuleStore(object):
    def __init__(self, unifier):
        self.uni = unifier
        self._facts = FactStore()
        self._rules = []
        self._facts_to_add = []
    
    def Copy(self):
        if self._facts_to_add:
            raise RuntimeError('Cannot copy with pending facts to add.')
        copy = RuleStore(self.uni)
        copy._facts = self._facts.Copy()
        copy._rules = self._rules.copy()
    
    def AddFact(self, term):
        self._facts_to_add.append(term)
        self._FinishPendingFacts()
        
    def AddRule(self, rule):
        self._rules.append(rule)
        
        premise_symbols = map(self._GetSymbol, rule.premise)
        missing_premises = self._facts.GetMissingSymbols(premise_symbols)
        if missing_premises:
            self._facts.ListenForAllOf(missing_premises, partial(self._ApplyRule, rule, register_listener=True))
        else:
            self._ApplyRule(rule, register_listener=True)
        self._FinishPendingFacts()
    
    def MatchingFacts(self, terms):
        return DerivedFacts(self._facts, self.uni, terms).MatchingFacts()
    
    def _FinishPendingFacts(self):
        while self._facts_to_add:
            term = self._facts_to_add.pop()
            symbol, _ = self.uni.IsPred(term)
            self._facts.Add(symbol, term)
            
    def _GetSymbol(self, pred):
        symbol, _ = self.uni.IsPred(pred)
        return symbol
        
    def _OnNewFact(self, rule, symbol, fact):
        # Reregister the handler for `symbol`.
        self._facts.ListenFor(symbol, partial(self._OnNewFact, rule))
        self._ApplyRule(rule, register_listener=False, must_match=fact)
    
    def _ApplyRule(self, rule, register_listener, must_match=None):
        """Assumes that there are no missing premise symbols in `_facts`."""
        matches = DerivedFacts(self._facts, self.uni, rule.premise).MatchingFacts(must_match)
        if matches:
            print("Trigger rule %s, %s matches:\n  %s" % (rule, len(matches), matches))
            for match in matches:
                for f in rule.conclusion(match):
                    self._facts_to_add.append(f)
        
        premise_symbols = map(self._GetSymbol, rule.premise)
        if register_listener:
            self._facts.ListenForAnyOf(premise_symbols, partial(self._OnNewFact, rule))
    
