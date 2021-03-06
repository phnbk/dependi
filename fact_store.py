from print_scope import PrintScope, Print
from collections import namedtuple

class FactStore(object):
    def __init__(self):
        # Maps from symbol to set of ground predicates.
        self.facts = {}
        
        # Maps from symbol to list of listeners. On addition of a fact with
        # symbol S, listeners for that symbol will be called with S and the fact.
        self.listeners = {}
        
    def ListenFor(self, symbol, listener):
        self.listeners.setdefault(symbol, set()).add(listener)

    def ListenForAnyOf(self, symbols, listener):
        for s in symbols:
            self.ListenFor(s, listener)
            
    def ListenForAllOf(self, symbols, callback):
        missing_symbols = set(symbols)
        
        def listener(symbol, fact):
            missing_symbols.discard(symbol)
            if not missing_symbols:
                callback()
                
        for s in missing_symbols:
            self.ListenFor(s, listener)

    def Add(self, symbol, term):
        """Adds (symbol, term), triggers listeners and returns their results."""
        facts_for_symbol = self.facts.setdefault(symbol, set())
        if term in facts_for_symbol:
            return []
        facts_for_symbol.add(term)
        result = []
        for listener in self.listeners.pop(symbol, []):
            result.append(listener(symbol, term))
        return result
    
    def GetFacts(self, symbol):
        return self.facts.get(symbol, set())
    
    def GetMissingSymbols(self, symbols):
        return set(symbols) - self.facts.keys()

Match = namedtuple('Match', 'facts substitutions')

class DerivedFacts(object):
    def __init__(self, facts, unifier, terms):
        self.facts = facts
        self.unifier = unifier
        self.terms = terms

    def ExtendMatches(self, prefix_matches, term):
        """Extends elements of `prefix_matches` (list of `Match`) that match terms."""
        result = []
        for prefix in prefix_matches:
            query_term = self.unifier.Apply(prefix.substitutions, term)
            symbol, _ = self.unifier.IsPred(term)
            for fact in self.facts.GetFacts(symbol):
                try:
                    new_substitions = self.unifier.UnifyOne(fact, query_term)
                except ValueError:
                    continue
                
                result.append(Match(prefix.facts + [fact], prefix.substitutions + new_substitions))
        
        return result
        
    def MatchingFacts(self, must_match=None):
        matches = [Match(facts=[], substitutions=[])]
        for term in self.terms:
            matches = self.ExtendMatches(matches, term)
        if not must_match:
            return matches
        return [m for m in matches if must_match in m.facts]
