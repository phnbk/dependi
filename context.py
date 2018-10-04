from collections import namedtuple
from functools import partial
from rule_store import RuleStore, Rule, Match, DerivedFacts
from unification import Unification

### TODO: `name' of impl is should be declared and reused and not an adhoc name.

class Type(namedtuple('Type', 'id')):
  def Next(self):
      return Type(self.id + 1)
    
TypeVar = namedtuple('TypeVar', 'id')
Implementation = namedtuple('Implementation', 'name type_args impl')

def ImplPattern(name, type_args):
    return Implementation(name, type_args, None)

def CheckIsValidType(x):
    if not isinstance(x, Type):
        raise ValueError('Not a Type: %s' % x)
    if not isinstance(x.id, int):
        raise ValueError('Not a Type: %s' % x)
        
def CheckIsImplementation(x):
    if not isinstance(x, Implementation):
        raise ValueError('Not a Implementation: %s' % (x,))
    
    if not isinstance(x.name, str):
        raise ValueError('Not a valid name: %s' % (x.name,))
        
    if not isinstance(x.type_args, tuple):
        raise ValueError('Not a list of type args: %s' % (x.type_args,))
        
    for a in x.type_args:
        if isinstance(a, TypeVar):
            if not isinstance(a.id, int):
                raise ValueError('Not a valid TypeVar id: %s' % (a.id,))
        else:
            CheckIsValidType(a)
        
def CheckIsGroundImplementation(x):
    CheckIsImplementation(x)
    for a in x.type_args:
        CheckIsValidType(a)

class ImplUnification(Unification):
    def IsVar(self, term):
        if isinstance(term, TypeVar):
            return term.id
        else:
            return None
            
    def IsPred(self, term):
        if isinstance(term, Type):
            return term, []
        elif isinstance(term, Implementation):
            return term.name, term.type_args
        else:
            return None
            
    def ReplaceArgs(self, pred, args):
        if not args:
            return pred
        if isinstance(pred, Implementation):
            return Implementation(pred.name, args, pred.impl)
        else:
            raise RuntimeError('Bad substition of non-implementation object: %s' % pred)

class Types(object):
    last_type = Type(-1)
    
    @classmethod
    def NewType(self):
        self.last_type = self.last_type.Next()
        return self.last_type

class Context(object):
    Generic = namedtuple('Generic', 'name impl_f kw_to_pos')
    
    def __init__(self):
        self.store = RuleStore(ImplUnification())
    
    def Copy(self):
        return Context()
        
    def Add(self, impl):
        CheckIsGroundImplementation(impl)
        self.store.AddFact(impl)
    
    def AddGeneric(self, name, impl_f, **required_impls):
        """`name` is a free form name for debugging."""
        
        kw_to_pos, required_items_positional = self._KeywordPatternsToPosition(required_impls)
        g = self.Generic(name, impl_f, kw_to_pos)
        rule = Rule(required_items_positional, partial(self._InstantiateGeneric, g))
        self.store.AddRule(rule)
    
    def Query(self, **queried_impls):
        for impl in queried_impls.values():
            CheckIsImplementation(impl)
            
        kw_to_pos, impls_positional = self._KeywordPatternsToPosition(queried_impls)
        matches = self.store.MatchingFacts(impls_positional)
        result = []
        for match in matches:
            kw_to_impl = {}
            types = tuple(map(lambda s: s[1], sorted(match.substitutions, key=lambda s: s[0])))
            result.append((types, kw_to_impl))
            for kw, pos in kw_to_pos.items():
               kw_to_impl[kw] = match.facts[pos].impl
        return result
    
    def _InstantiateGeneric(self, generic, match):
        required_impls = {}
        for kw, pos in generic.kw_to_pos.items():
           required_impls[kw] = match.facts[pos].impl
        
        types = tuple(map(lambda s: s[1], sorted(match.substitutions, key=lambda s: s[0])))
        new_impls = generic.impl_f(types=types, **required_impls)
        for impl in new_impls:
            CheckIsGroundImplementation(impl)
        return new_impls
    
    @staticmethod
    def _KeywordPatternsToPosition(required_impls):
        kw_to_pos = {}
        required_items_positional = []
        for required_name, required_impl in required_impls.items():
            CheckIsImplementation(required_impl)
            kw_to_pos[required_name] = len(required_items_positional)
            required_items_positional.append(required_impl)
        return kw_to_pos, required_items_positional
        