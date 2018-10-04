
# Algorithm from https://www.cs.cornell.edu/courses/cs3110/2011sp/Lectures/lec26-type-inference/type-inference.htm#4

class Unification(object):
    
    def IsVar(self, term):
        """If `term` is a variable returns its id."""
        raise ValueError('not implemented')

    def IsPred(self, term):
        """If `term` is a predicate returns a symbol and list of arguments."""
        raise ValueError('not implemented')
    
    def ReplaceArgs(self, pred, args):
        raise ValueError('not implemented')
    
    def Occurs(self, v_id, term):
        term_var = self.IsVar(term)
        if term_var is not None:
            return v_id == term_var
        else:
            _, args = self.IsPred(term)
            return any(self.Occurs(v_id, arg) for arg in args)
            
    def Substitute(self, s, v_id, t):
        t_var = self.IsVar(t)
        if t_var is not None:
            if t_var == v_id:
                return s
            else:
                return t
        else:
            _, args = self.IsPred(t)
            new_args = [self.Substitute(s, v_id, arg) for arg in args]
            return self.ReplaceArgs(t, new_args)
    
    def Apply(self, substitutions, term):
        for v_id, s in substitutions:
            term = self.Substitute(s, v_id, term)
        return term
    
    def UnifyOne(self, a, b):
        a_var = self.IsVar(a)
        b_var = self.IsVar(b)
        if a_var is not None and b_var is not None:
            if a_var == b_var:
                return []
            else:
                return [(a_var, b)]
        if a_var is None and b_var is None:
            a_sym, a_args = self.IsPred(a)
            b_sym, b_args = self.IsPred(b)
            if a_sym != b_sym:
                raise ValueError('Cannot unify: conflicting symbols %s and %s' % (a_sym, b_sym))
            if len(a_args) != len(b_args):
                raise ValueError('Cannot unify: conflicting arities %s and %s for %s' % (len(a_args), len(b_args), a_sym))
            return self.Unify(list(zip(a_args, b_args)))
        
        if a_var is None:
            # a is predicate and b is variable.
            if self.Occurs(b_var, a):
                raise ValueError('Cannot unify: circularity %s = %s' % (a, b_var))
            return [(b_var, a)]

        # a is variable and b is predicate.
        if self.Occurs(a_var, b):
            raise ValueError('Cannot unify: circularity %s = %s' % (a_var, b))
        return [(a_var, b)]
    
    def Unify(self, equations):
        result = []
        for (a, b) in equations:
            subst = self.UnifyOne(self.Apply(result, a), self.Apply(result, b))
            result += subst
        return result
    