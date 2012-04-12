# coding=utf-8

'''
Created on Apr 7, 2012

@author: William

Support for combination of terms as the lambda function body.
'''

import sys

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
    
    def apply(self, argv, var=None):
        if var is None:
            var = self.var
        if argv is None:
            raise ValueError('*** Application: argv should not be None.')
        # remove unnecessary parentheses
        argv = remove_par(argv) if len(remove_par(argv)) == 1 else argv
#        print '=== Applying... [%s := %s] to %s' % (var, argv, self)
        
#        print '=== Application [domain - before]:', self.get_domain()
        for i in range(len(self.domain)):
            term = self.domain[i]
            
#            print '=== Application [term - before]:', term
            if not isinstance(term, LambdaFunc):
                self.domain.remove(term)
                # remove parentheses before application and add them back if necessary
                # this will avoid redundant parentheses during application
                applied = remove_par(term).replace(var, argv)
                applied = applied if len(applied) == 1 else add_par(applied)
                self.domain.insert(i, applied)
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

def parse_func(term):
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
        if sub.startswith('('):   # inner function with parentheses
            sub, offset = read_token(sub)
            # since they are in parentheses, they are meant to be evaluated as long as possible
            sub = remove_par(parse(sub))
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

def parse(term, out_type=str):
    '''
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
    buf = []
    pos = 0
    func = None
    term = remove_par(term)
    while True:
        next_token, pos = read_token(term, pos)
        if next_token is None:
            break
        
#        print 'Before parsing...', next_token
        # process next_token
        if isinstance(func, LambdaFunc):
#            print 'Before applying...', func
            func = func.apply(next_token)
#            print 'After applying...', func
        else:
            if not next_token.startswith('(λ'):
                # Parse token only if it cannot be converted
                # to lambda function. For example:
                # ((λx.λy.x (λe.e)) (λf.λx.f x)).
                # Otherwise, it will muddle the sequence of
                # computation. For example:
                # (λx.λy.x (λe.e)) (λf.λx.f x).
                next_token = parse(next_token)
                
            if next_token.startswith('(λ'):
                if func is not None:    # but it isn't function either
                    buf.append(func)
                
                # parse lambda function
                try:
                    func = parse_func(remove_par(next_token))
#                    print 'Parsed function...', func
                except:
                    sys.exit(sys.exc_info()[1])
            else:
                # cannot parse it to lambda function
                buf.append(next_token)

    if func is not None:
        buf.append(func)
    
    parsed = add_par(''.join(map(str, buf)))
    if parsed == add_par(term):
        if out_type == list:
            return parsed, buf
        return parsed

    next_parsed, next_buf = parse(parsed, list)
    while next_parsed != parsed:
        parsed, buf = next_parsed, next_buf
        next_parsed, next_buf = parse(parsed, list)
    if out_type == list:
        return parsed, buf
    return parsed

if __name__ == '__main__':
    
    # Tests
#    print has_par('(()()((()())()))')
    
#    term = '(λy.λx.λf.ax(b)yc)abc'
#    token, pos = read_token(term)
#    print token, pos
#    print read_token(term, pos)

#    print parse_func('λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)')
    
#    func = parse_func('λp.λq.p p q')
#    print func
#    func = func.apply('(λx.λy.x)')
#    print func
#    func = func.apply('(λx.λy.y)')
#    print func

#    func = parse_func('λx.λf.ax(b)yc')
#    outer_func = LambdaFunc('y')
#    outer_func.add_term(func)
#    print outer_func
#    ret = outer_func.apply('H').apply('HH')
#    print ret
    
#    print parse('λa.λb.λc.abc')
#    print parse('(λy.λx.λf.ax(b)yc)ABC')
#    print parse('(λy.λx.λf.ax(b)yc)A(BC)')
#    print parse('((λf.λx.(fx))f)x')
#    print parse('(λx.(y(λx.(zx))))(a)')
    
#    print parse('(λn. λf. λx. (f (n f) x)) (λf. λx. (f x))')
#    print parse('(λn. λf. λx. (f (n f) x)) ((λn. λf. λx. (f (n f) x)) (λf. λx. (f x)))')
    
#    print 'PLUS 1 2 = 3:',
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
    
#    print 'NOT TRUE:\t',
#    print parse('(λp.λa.λb.p b a) (λx.λy.x)')
#    print 'OR TURE FALSE:\t',
#    print parse('(λp.λq.p p q) (λx.λy.x) (λx.λy.y)')
#    print 'IF-THEN-ELSE TRUE M N:\t',
#    print parse('(λp.λa.λb.p a b) (λx.λy.x) M N')
#    print 'IF-THEN-ELSE FALSE M N:\t',
#    print parse('(λp.λa.λb.p a b) (λx.λy.y) M N')
    
    print parse('(λf.λy.f y) (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λz.f z)')

#    print 'SUB 3 2 = 1:\t',
#    print parse('(λi.λj.j (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) i) (λf.λy.f (f (f y))) (λf.λz.f (f z))')
#    print parse('j (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λy.f (f (f y)))')
#    print parse('(λj.(j(λf.(λx.(f(fx)))))) (λf.λz.f (f z))')
#    print
#    print parse('(λf.λz.f (f z)) (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u))')
#    print parse('(λf.λz.f (f z)) (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λy.f (f (f y)))')
#    print
#    print parse('(λf.λz.f (f z)) (PRED)')
#    print parse('(λi.λj.j (PRED) i) (λf.λy.f (f (f y))) (λf.λz.f (f z))')
#    print parse('(λf.λz.f (f z)) (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u))')
#    print parse('(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u))(λf.(λy.(f(f(fy)))))')
#    print parse('(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λx.z (λg.λh.h (g f)) (λu.x) (λu.u))')
#    print parse('(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u))')
    

#    print parse('(λf.λz.f (f z))      (λf.λx.(f(fx)))')
#    print 'IF-THEN-ELSE TRUE (PRED (IF-THEN-ELSE FALSE M 2)) N = IF-THEN-ELSE TRUE (PRED 2) N = 1:\t',
#    print parse('(λa.λb.λc.abc) (λx.λy.x) ((λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) ((λa.λb.λc.abc) (λx.λy.y) M (λf.λx.f (f x)))) N ')
    
#    print parse('(λp.dλa.λb.p a b) (λx.λy.y) M N')
#    print parse('(λp.p (λx.λy.y)) M N')
    
#    print parse(sys.argv[1])











