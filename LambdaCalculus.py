# coding=utf-8

'''
Created on Apr 6, 2012

@author: William
'''

import sys

class LambdaFunc():
    
    def __init__(self, var):
        self.var = var
    
    def __expr__(self):
        return '(λ%s.%s)' % (self.var, \
                    self.func if self._is_func else self.expr)
    
    def __str__(self):
        return '(λ%s.%s)' % (self.var, \
                    self.func if self._is_func else self.expr)
    
    def set_var(self, var):
        self.var = var
    
    def set_func(self, func):
        self.func = func
        self._is_func = True
    
    def set_expr(self, expr):
        self.expr = expr
        self._is_func = False
    
    def is_func(self):
        return self._is_func
    
    def get_var(self):
        return self.var
    
    def get_func(self):
        return self.func
    
    def get_expr(self):
        return self.expr
    
    def get_inner(self):
        if self._is_func:
            return self.func
        return self.expr
    
    def apply(self, argv):
#        print '=== Applying...', func, 'to', argv
        if argv is None:
            raise ValueError('*** Application: argv should not be None.')
        # remove unnecessary parentheses
        argv = remove_par(argv) if len(remove_par(argv)) == 1 else argv
        
        inner_func = self
        while inner_func.is_func():
            inner_func = inner_func.get_func()
            if inner_func.get_var() == self.var:
                return self.get_func() if self.is_func() else parse(self.get_expr())
        
#        print '=== Application [before]:', self.get_inner()
        # remove parentheses before application and add them back if necessary
        # this will avoid redundant parentheses during application
        applied = add_par(
                          remove_par(inner_func.get_expr()) \
                            .replace(self.var, argv)
                        )
#        print '=== Application [cascade]:', applied
        applied = parse(applied)
        
        try:
            func = parse_func(remove_par(applied))
        except:
            inner_func.set_expr(applied)
        else:
            inner_func.set_func(func)
#        print '=== Application [after]:', self.get_inner()
        return self.get_inner()

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
    
    if term[3] != '.':
        raise ValueError('*** Parse Function: Invalid token at position 3 in %s. "." is expected.' % term)
    if len(term) < 5:
        raise ValueError('*** Parse Function: No lambda term found.')
    
    func = LambdaFunc(term[2])
    
    if term[4:].startswith('λ'):
        inner_func = parse_func(term[4:])
        func.set_func(inner_func)
    else:
        expr = add_par(term[4:])
        func.set_expr(expr)

    return func

def parse(term):
    '''
    Parameter "term" comes in with outer parentheses.
    '''
    
    term = term.replace(' ', '')
    if len(term) < 2 or term.find('λ') == -1:
        # no need to further parse it
        return remove_par(term) if len(remove_par(term)) == 1 else term
    
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
        
        # DEFECT: should not always apply prior function to
        # following terms but unless they are in parentheses
        
        # process next_token
#        print 'Before parsing...', next_token
        if isinstance(func, LambdaFunc):
#            print 'After applying...', func
            func = func.apply(next_token)
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
                if func is not None:
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
        return parsed
    
    next_parsed = parse(parsed)
    while next_parsed != parsed:
        parsed = next_parsed
        next_parsed = parse(parsed)
    return parsed

#def parse2(term):
#    '''
#    Parameter "term" comes in with outer parentheses.
#    '''
#    
#    term = term.replace(' ', '')
#    if len(term) < 2 or term.find('λ') == -1:
#        # no need to further parse it
#        # TODO: return remove_par(term)
#        return term
#    
#    # parse term containing lambda function(s), which must be enclosed
#    # by parentheses
#    buf = []
#    pos = 0
#    func = None
#    term = remove_par(term)
#    while True:
#        next_token, pos = read_token(term, pos)
#        if next_token is None:
#            break
#        
#        # NOTE: should not parse it before trying to convert it to
#        # lambda function; it would otherwise muddle the sequence of
#        # computation.
##        next_token = parse(next_token)
#        
#        # process next_token
##        print 'Before parsing...', next_token
#        if isinstance(func, LambdaFunc):
#            func = app(func, next_token)
##            print 'After applying...', func
#        elif next_token.startswith('(λ'):
#            if func is not None:
#                buf.append(func)
#            
#            # parse lambda function
#            try:
#                func = parse_func(remove_par(next_token))
##                print 'Parsed function...', func
#            except:
#                sys.exit(sys.exc_info()[1])
#        else:
#            # NOTE: parse(next_token) might result in a lambda function;
#            # therefore, updated to new version
#            buf.append(parse(next_token))
#
#    if func is not None:
#        buf.append(func)
#    
#    return add_par(''.join(map(str, buf)))

#def parse3(term):
#    '''
#    Parameter "term" comes in with outer parentheses.
#    '''
#    
#    term = term.replace(' ', '')
#    if len(term) < 2 or term.find('(λ') == -1:
#        # no need to further parse it
#        # TODO: return remove_par(term)
#        return term
#    
#    # parse term containing lambda function(s), which must be enclosed
#    # by parentheses
#    buf = []
#    term = remove_par(term)
#    last_token, pos = read_token(term)  # last_token must not be None
##    last_token = parse(last_token)
#    while True:
#        next_token, pos = read_token(term, pos)
#        
#        if next_token is None:
#            buf.append(last_token)
#            break
#        
#        next_token = parse3(next_token)
#        
#        # process last_token
##        print 'Before parsing...', last_token
#        if isinstance(last_token, LambdaFunc) or \
#                last_token.startswith('(λ'):
#            # parse lambda function
#            if not isinstance(last_token, LambdaFunc):
#                last_token = remove_par(last_token)
#            try:
#                func = parse_func(last_token)
##                print 'Parsed function...', func
#            except:
#                sys.exit(sys.exc_info()[1])
#                
#            last_token = app(func, next_token)
##            print 'After applying...', last_token
#        else:
#            buf.append(last_token)
#            last_token = next_token
#    
#    return add_par(''.join(map(str, buf)))

if __name__ == '__main__':
    
    # Tests
#    print has_par('(()()((()())()))')
    
#    func = parse_func('λx.λf.ax(b)yc')
#    outer_func = LambdaFunc('y')
#    outer_func.set_func(func)
#    ret = app(app(outer_func, 'H'), 'HH')
#    print ret
#    
#    outer_func = parse_func('λy.λx.λf.ax(b)yc')
#    ret = app(app(outer_func, 'H'), 'HH')
#    print ret
    
#    term = '(λy.λx.λf.ax(b)yc)abc'
#    token, pos = read_token(term)
#    print token, pos
#    print read_token(term, pos)
    
    print parse('λa.λb.λc.abc')
    print parse('(λy.λx.λf.ax(b)yc)ABC')
    print parse('(λy.λx.λf.ax(b)yc)A(BC)')
    print parse('((λf.λx.(fx))f)x')
    print parse('(λx.(y(λx.(zx))))(a)')
    
    print parse('(λn. λf. λx. (f (n f) x)) (λf. λx. (f x))')
    print parse('(λn. λf. λx. (f (n f) x)) ((λn. λf. λx. (f (n f) x)) (λf. λx. (f x)))')
    
    print 'PLUS 1 2 = 3:\t',
    print parse('(λm.λn.λf.λx.m f (n f x)) (λf.λx.f x) (λf.λx.f (f x))')
    print 'MULT 2 2 = 4:\t',
    print parse('(λm.λn.λf.m (n f)) (λf.λx.f (f x)) (λf.λx.f (f x))')
    print 'POW 2 3 = 8:\t',
    print parse('(λb.λe.e b) (λf.λx.f (f x)) (λg.λf.g (g (g f)))')
    print 'PRED 2 = 1:\t',
    print parse('(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λx.f (f x))')
    print 'PRED 0 = 0:\t',
    print parse('(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) (λf.λx.x)')
    
    print 'NOT TRUE:\t',
    print parse('(λp.λa.λb.p b a) (λx.λy.x)')
    print 'OR TURE FALSE:\t',
    print parse('(λp.λq.p p q) (λx.λy.x) (λx.λy.y)')
    print 'IF-THEN-ELSE TRUE M N:\t',
    print parse('(λp.λa.λb.p a b) (λx.λy.x) M N')
    print 'IF-THEN-ELSE FALSE M N:\t',
    print parse('(λp.λa.λb.p a b) (λx.λy.y) M N')
    
    print 'SUB 3 2 = 1:\t',
    print parse('(λi.λj.j (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) i) (λf.λy.f (f (f y))) (λf.λz.f (f z))')
    
#    print parse('((λa.λb.λc.abc) (λx.λy.x) (λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)) N) ((λa.λb.λc.abc) (λx.λy.y) M (λf.λx.x))')
    
#    print parse(sys.argv[1])











