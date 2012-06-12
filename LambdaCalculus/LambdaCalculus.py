# coding=UTF-8

'''
Created on Apr 11, 2012

@author: William

V4. Support for combination of terms as the lambda function body.
V5. Support for factorial.

ISSUE: (λm.λn.mn) n l --> (λn.nn) l --> ll
'''

import sys

Y = '(λg.(λx.g (x x)) (λx.g (x x)))'
G = '(λF.λN.(λp.λa.λb.p a b) ((λn.n (λx.λi.λj.j) (λi.λj.i)) N) (λf.λx.f x) ((λm.λn.λf.m (n f)) N (F ((λi.λj.j (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) i) N (λf.λz.f z)))))'

# Setting f --> F and n --> N does matter; the following will not work:
#G = '(λF.λn.(λp.λa.λb.p a b) ((λn.n (λx.λi.λj.j) (λi.λj.i)) n) (λf.λx.f x) ((λm.λn.λf.m (n f)) n (F ((λi.λj.j (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) i) n (λf.λz.f z)))))'
#print parse('(λN.(λp.λa.λb.p a b) ((λn.n (λx.λi.λj.j) (λi.λj.i)) N) (λf.λx.f x) ((λm.λn.λf.m (n f)) N (F ((λi.λj.j (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) i) N (λf.λz.f z))))) (λf.(λz.f z))')

def has_par(s):
    if not s.startswith('('):
        return False
    
    left, right = s.find('(', 1), s.find(')', 1)
    while left != -1 and right != -1 and left < right:
        left = s.find('(', left + 1)
        right = s.find(')', right + 1)
    if left == -1 and right == -1:
        raise ValueError('*** Read Token: Unexpected pairs of parentheses in %s!' % s)
    
    if right == len(s) - 1:
        return True
    else:
        return False

def add_par(s):
    if not has_par(s):
        return '(' + s + ')'
    return s

def remove_par(s):
    while has_par(s):
        s = s[1:-1]
    return s

class LambdaFunc():
    
    def __init__(self, var):
        self.var = var
    
    def __expr__(self):
        return '(λ%s.%s)' % (self.var, self.get_domain())
    
    def __str__(self):
        return '(λ%s.%s)' % (self.var, self.get_domain())
    
    def set_var(self, var):
        self.var = var
    
    def set_domain(self, domain):
        self.domain = domain
    
    def add_term(self, term):
        if 'domain' not in dir(self):
            self.domain = []
        self.domain.append(term)
    
    def get_var(self):
        return self.var
    
    def get_domain(self):
        _domain = ''.join(map(str, self.domain))
        return _domain if len(_domain) == 1 else add_par(_domain)
    
    def deeper_apply(self, var, argv, term):
        # 1. remove parentheses before application and add them back if necessary
        # this will avoid redundant parentheses during application
        # 2. parse it before applying since the term may containing combination of
        # variables and functions
        # 3. keep domain as one dimension array
        
        parsed, terms = parse(term, list)
        
        for i in range(len(terms)):
            term = terms[i]
            
            if not isinstance(term, LambdaFunc):
                terms.remove(term)
                if len(parse(term, list)[1]) == 1: # simple term
                    applied = remove_par(term).replace(var, argv)
                else:   # need further decompose
                    applied = self.deeper_apply(var, argv, term)
                # this cost me two days on complex sub!!!
                applied = applied if len(applied) == 1 else add_par(applied)
                terms.insert(i, applied)
            elif term.get_var() != var:
                # lambda function
                # apply beta reduction only if they are bound to different variables
                term.apply(argv, var)
                term = parse_func(remove_par(str(term)))
        return ''.join(map(str, terms))
    
    def apply(self, argv, var=None):
        
        if var is None:
            var = self.var
        if argv is None:
            raise ValueError('*** Application: argv should not be None.')
        # remove unnecessary parentheses
        argv = remove_par(argv) if len(remove_par(argv)) == 1 else argv
#        print '*** Applying... [%s := %s] to %s' % (var, argv, self)
        
#        print '=== Application [domain - before]:', self.get_domain()
        for i in range(len(self.domain)):
            term = self.domain[i]
            
#            print '=== Application [term - before]:', term
            if not isinstance(term, LambdaFunc):
                self.domain.remove(term)
                applied = self.deeper_apply(var, argv, term)
                # after two days on complex sub, add this in case!!!
                applied = applied if len(applied) == 1 else add_par(applied)
                self.domain.insert(i, applied)
#                print '=== Application [term - after - string]:', applied
            else:
                # 1. do not apply it if sub-function has the same variable
                # 2. as sub-function, term should not be replaced by its domain after
                # application, but terms in its domain should be parsed cascade to
                # functions if possible
                if term.get_var() != var:
                    term.apply(argv, var)
                    term = parse_func(remove_par(str(term)))
#                print '=== Application [term - after - function]:', term
            
#        print '=== Application [domain - after]:', self.get_domain()
        
        # process inner domain after application
        parsed, terms = parse(self.get_domain(), list)
        try:
            func = parse_func(remove_par(parsed))
        except:
            self.domain = terms
        else:
            self.domain = [func]
#        print '=== Application [after]:', self.get_domain()
        return self.domain[0] if len(self.domain) == 1 else self.get_domain()

def read_token(s, pos=0):
    '''
    Reads one token from given s passed in without outer parentheses.
    
    Returns single character token (variable) or set of characters
    embraced by parentheses. "pos" will point at the position behind
    the character or ")" -- could be equal to len(s); -1 if invalid.
    '''
    
    if len(s) == 0 or pos >= len(s):
        return None, -1
    
    if not s[pos].startswith('('):
        return s[pos], pos + 1
    
    left, right = s.find('(', pos + 1), s.find(')', pos + 1)
    while left != -1 and right != -1 and left < right:
        left = s.find('(', left + 1)
        right = s.find(')', right + 1)
    if left == -1 and right == -1:
        raise ValueError('*** Read Token: Unexpected pairs of parentheses in %s!' % s)
    right += 1
    return s[pos : right], right

def parse_func(term, first=False):
    # for example, term = 'λx.λf.a(b)c', where a(b)c are all together
    # with or without enclosing parentheses; or term is an instance of LambdaFunc
    # NOTE: 'λ' takes up two bytes
    
    if isinstance(term, LambdaFunc):
        return term
    
    term = term.replace(' ', '')
    ptr = 3
    if term[ptr] != '.':
        raise ValueError('*** Parse Function: Invalid token at position 3 in %s. "." is expected.' % term)
    if len(term) < 5:
        raise ValueError('*** Parse Function: No lambda term found.')
    
    ptr = 2
    func = LambdaFunc(term[ptr])
    
    ptr = 4
    while ptr < len(term):
        sub = term[ptr:]
        offset = len(sub)
        if sub.startswith('('):
            # inner function with parentheses:
            # parse it only if the input argument term is the first one in one expresion;
            # otherwise keep it together and do not parse it right now (i.e. do not parse terms before applying)
            sub, offset = read_token(sub)
            # since they are in parentheses, they are meant to be evaluated as long as possible
            sub = remove_par(parse(sub) if first else sub)
        elif not sub.startswith('λ'):   # single-word term (starts with neither '(' nor 'λ')
            sub, offset = sub[0], 1
        
        if sub.startswith('λ'):  # parse inner function
            try:
                inner_func = parse_func(sub)
            except:
                raise ValueError('Unexpected lambda function format: %s.' % sub)
            func.add_term(inner_func)
        else:   # simple term(s)
            func.add_term(sub if offset == 1 else add_par(sub))
        
        ptr += offset

    return func

def parse(term, out_type=str, main=False):
    '''
    # TODO: remove this setting
    Parameter "term" comes in with outer parentheses.
    '''
    
    term = term.replace(' ', '')
    if len(term) < 2 or term.find('λ') == -1:
        # no need to further parse it
        term = remove_par(term) if len(remove_par(term)) == 1 else term
        if out_type == list:
            return term, [term]
        return term
    
    # parse term containing lambda function(s), which must be enclosed
    # by parentheses
    term = remove_par(term)
    # TODO: update this after removing parentheses setting
    if term.startswith('λ'):
        term = add_par(term)
    first_token, pos = read_token(term)
    if not first_token.startswith('(λ'):
        # e.g., ((λx.λy.x (λe.e)) (λf.λx.f x)) -- uncommon as first term
        first_token = parse(first_token)
    func = None
    if first_token.startswith('(λ'):
        try:
            func = parse_func(remove_par(first_token), True)
        except:
            sys.exit(sys.exc_info()[1])
        buf = []
    else:
        buf = [first_token]
    
    while True:
        # keep parentheses on next_token so it will be processed together
        next_token, pos = read_token(term, pos)
        if next_token is None:
            if func is not None:
                buf.append(func)
            break
        
        # if next_token is enclosed by parentheses, it should be parsed first
        if not next_token.startswith('(λ'):
            next_token = parse(next_token)
        
        if func is not None:
            func = func.apply(next_token)
            
            if not isinstance(func, LambdaFunc):
                # func is not a function any longer
                buf.append(func)
                func = None
        else:
            if next_token.startswith('(λ'):
                # parse lambda function
                try:
                    next_token = parse_func(remove_par(next_token))
                except:
                    sys.exit(sys.exc_info()[1])
                else:
                    buf.append(next_token)
            else:
                buf.append(next_token)

    global Y
    global G
    parsed = add_par(''.join(map(str, buf)))
    if main and parsed.find('(YG)') != -1:
        parsed = parsed.replace('(YG)', G + '(YG)', 1)
        # if it is not parsing the main input expression, do not expend (YG),
        # since the parent expression might still be able to be further parsed;
        # otherwise it may result in infinite loop
        parsed = parse(parsed, main=main)
    if out_type == list:
        return parsed, buf
    return parsed

if __name__ == '__main__':
    
####################################################### TEST #######################################################
#    
#    print parse('(λa.λb.λc.abc)')   # (λa.(λb.(λc.(abc))))
#    print parse('(λy.λx.λf.ax(b)yc)ABC')
#    print parse('(λy.λx.λf.ax(b)yc)A(BC)')  # (λf.(a(BC)bAc))
#    print parse('((λf.λx.(fx))f)x') # (fx)
#    
#    print parse('(λn. λf. λx. (f (n f x))) (λf. λx. (f x))')
#    print parse('(λn. λf. λx. (f (n f x))) ((λn. λf. λx. (f ((n f) x))) (λf. λx. (f x)))')
#    
#    print 'PLUS 1 2 = 3:'
#    print parse('(λm.λn.λf.λx.m f (n f x)) (λf.λx.f x) (λf.λx.f (f x))')
#    print parse('(λm.λn.m (λn.λf.λx.f (n f x)) n) (λf.λy.f y) (λf.λx.f (f x))')    # (λf.λx.f x) will make it wrong
#    print 'MULT 2 2 = 4:\t',
#    print parse('(λm.λn.λf.m (n f)) (λf.λx.f (f x)) (λf.λx.f (f x))')
#    print 'POW 2 3 = 8:\t',
#    print parse('(λb.λe.e b) (λf.λx.f (f x)) (λg.λf.g (g (g f)))')
#    print 'PRED 2 = 1:\t',
#    print parse('(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λx.f (f x))')
#    print 'PRED 0 = 0:\t',
#    print parse('(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λx.x)')
#    print 'SUB 3 2 = 1:\t',
#    print parse('(λi.λj.j (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) i) (λf.λy.f (f (f y))) (λf.λz.f (f z))')
#    
#    print 'NOT TRUE:\t',
#    print parse('(λp.λa.λb.p b a) (λx.λy.x)')
#    print 'OR TURE FALSE:\t',
#    print parse('(λp.λq.p p q) (λx.λy.x) (λx.λy.y)')
#    print 'IF-THEN-ELSE TRUE M N:\t',
#    print parse('(λp.λa.λb.p a b) (λx.λy.x) M N')
#    print 'IF-THEN-ELSE FALSE M N:\t',
#    print parse('(λp.λa.λb.p a b) (λx.λy.y) M N')
#    
#    print 'IF-THEN-ELSE TRUE (PRED (IF-THEN-ELSE FALSE M 2)) N = IF-THEN-ELSE TRUE (PRED 2) N = 1:\t',
#    print parse('(λa.λb.λc.abc) (λx.λy.x) ((λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) ((λa.λb.λc.abc) (λx.λy.y) M (λf.λx.f (f x)))) N')
#    
#    print 'Irregular:'
#    print parse('(λx.(y(λx.(zx))))(a)')
#    print parse('(λp.dλa.λb.p a b) (λx.λy.y) M N')
#    print parse('(λp.p (λx.λy.y)) M N')
#    
#    print 'FCTORIAL FOUR:\t',
#    print parse('(Y G) (λf.λx.(f (f (f (f x)))))', main=True)
#    
##############################################################################################################

    if len(sys.argv) > 1:
        try:
            parsed = parse(sys.argv[1], main=True)
            print 'Result is: %s.' % parsed
        except:
            print 'Failed to parse [%s]:\n\t%s' % (sys.argv[1], sys.exc_info()[1])
    else:
        print 'No argument was received.'
