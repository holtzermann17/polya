####################################################################################################
#
# tests.py
#
# Authors:
# Jeremy Avigad
# Rob Lewis
#
# Contains tests for Polya.
#
# TODO:
#
####################################################################################################


from __future__ import division
import polya.main.terms as terms
import polya.main.formulas as formulas
import polya.main.blackboard as blackboard
import polya.polyhedron.poly_add_module as poly_add_module
import polya.polyhedron.poly_mult_module as poly_mult_module
import polya.main.messages as messages
import polya.main.function_module as function_module
import timeit


def run(B):
    pa, pm = poly_add_module.PolyAdditionModule(), poly_mult_module.PolyMultiplicationModule()
    try:
        s, s2 = '', '1'
        while s != s2:
            s = s2
            #B.info_dump()
            pa.update_blackboard(B)
            #B.info_dump()
            pm.update_blackboard(B)
            s2 = str(B.get_equalities()) + str(B.get_disequalities()) + str(B.get_inequalities())
        #print 'No contradiction found.'
        #print
        return False
    except terms.Contradiction as e:
        #print e.msg
        #print
        messages.announce(e.msg, messages.ASSERTION)
        return True


def solve(*assertions):
    #print 'Beginning heuristic.\n'
    B = blackboard.Blackboard()
    B.assert_comparisons(*assertions)
    return run(B)


def test1():
    x, y, u, v, w, z, r = terms.Vars('x, y, u, v, w, z, r')

    B = blackboard.Blackboard()
    B.assert_comparison(0 < x)
    B.assert_comparison(x < 3*y)
    B.assert_comparison(u < v)
    B.assert_comparison(v < 0)
    B.assert_comparison(1 < v**2)
    B.assert_comparison(v**2 < x)
    B.assert_comparison(u*(3*y)**2 + 1 >= x**2 * v + x)

    # This example has a model if the last inequality is <. FM blows up here, poly doesn't
    # It does not have a model if the last inequality is >=. Contradiction is found.
    # "0<x<3*y", "u<v<0", "1<v^2<x", "u*(3*y)^2+1 >= x^2*v+x"

    run(B)


def test2():
    x, y, u, v, w, z, r = terms.Vars('x, y, u, v, w, z, r')

    messages.set_verbosity(messages.normal)
    B = blackboard.Blackboard()

    B.assert_comparison(0 < x)
    B.assert_comparison(x < y)
    B.assert_comparison(0 < u)
    B.assert_comparison(u < v)
    B.assert_comparison(0 < w + z)
    B.assert_comparison(w + z < r - 1)
    B.assert_comparison(u + (1+x)**2 * (2*w + 2*z + 3) >= 2*v + (1+y)**2 * (2*r + 1))
    #     print("  0 < x < y")
    # print("  0 < u < v")
    # print("  0 < w + z < r - 1")
    #"  u + (1 + x)^2 (2 w + 2 z + 3) < 2 v + (1 + y)^2 (2 r + 1)"
    # x y u v w z r
    # a b c d e f g
    run(B)

t = timeit.default_timer()


def test3():
    x, y, u, v, w, z, r = terms.Vars('x, y, u, v, w, z, r')

    messages.set_verbosity(messages.normal)
    B = blackboard.Blackboard()

    # "x+1/y<2", "y<0", "y/x>1", "-2<=x<=2", "-2<=y<=2", "x^2*y^(-1)>1-x"
    B.assert_comparisons(x+1/y<2, y<0, y/x>1, -2<=x, x<=2, -2<=y, y<=2, x**2*y**(-1)>1-x)
    run(B)


def test4():
    f = terms.Func('f')
    a, b, c = terms.Vars('a, b, c')
    #u, v, w = terms.UVar(1), terms.UVar(2), terms.UVar(3)

    B = blackboard.Blackboard()

    fm = function_module.FunctionModule(
        [formulas.ForAll([a, b], formulas.Implies(a<b, f(a)<f(b)))]
    )

    B.assert_comparison(a<b)
    B.assert_comparison(f(a) > f(b))
    try:
        fm.update_blackboard(B)
    except terms.Contradiction:
        print 'contradiction found by axiom module'


def test5():

    f = terms.Func('f')
    x, y, z, w, r, s = terms.Vars('x, y, z, w, r, s')
    #u, v = terms.UVar(1), terms.UVar(2)

    B = blackboard.Blackboard()

    fm = function_module.FunctionModule([formulas.ForAll([x, y], formulas.Implies(x<y, f(x)<f(y)))])
    #fm = function_module.FunctionModule([f(p)!=f(q)])

    B.assert_comparisons(0<r, s>1, 0<x, x<y, w>z, z+f(x)>w+f(s*(y+r)))
    try:
        fm.update_blackboard(B)
    except terms.Contradiction:
        print 'contradiction found by axiom module'
        return

    run(B)


def test6():
    f = terms.Func('f')
    x, y, z, w, r, s = terms.Vars('x, y, z, w, r, s')
    u, v = terms.UVar(1), terms.UVar(2)

    C = blackboard.Blackboard()

    fm = function_module.FunctionModule(
        [formulas.ForAll([x, y], (f(x)+f(y))/2 >= f((x+y)/2))]
    )

    C.assert_comparisons(f(x)+f(y)<z, f((x+y)/2)>4*z, z>0)
    fm.update_blackboard(C)

    run(C)


def arithmetical_tests():
    x, y, u, v, w, z, r = terms.Vars('x, y, u, v, w, z, r')
    a, b, c, d, e = terms.Vars('a, b, c, d, e')

    messages.set_verbosity(messages.quiet)

    problems = [
        [x+1/y<2, y<0, y/x>1, -2<=x, x<=2, -2<=y, y<=2, x**2*y**(-1)>1-x],

        [0<x, x<y, 0<u, u<v, 0<w+z, w+z < r-1,
          u + (1+x)**2 * (2*w + 2*z + 3) >= 2*v + (1+y)**2 * (2*r + 1)],

        [0<x, x<3*y, u<v, v<0, 1<v**2, v**2<x, u*(3*y)**2+1 >= x**2*v + x],

        [0<x, x<3*y, u<v, v<0, 1<v**2, v**2<x, u*(3*y)**2+1 < x**2*v + x],

        [1<x, 1<y, 1<z, 1>=x*(1+z*y)],

        [a>0, a<1, b>0, b<1, a+b<a*b],

        [x+y>=2, z+w>=2, u*x**2<u*x, u*y**2<u*y, u*w**2>u*w, u*z**2>u*z],

        [a<=b*x/2, 0<c, 0<d, d<1, (1+d/(3*(c+3)))*a>=b*x],

        [x<1, 1<y, x*y>1, u+x>=y+1, x**2*y<2-u*x*y],

        [x<1, 1<y, x*y>1, u+x>=y+1, x**2*y>=2-u*x*y],

        [x*(y+z)<=0, y+z>0, x>=0, x*w>0],

        [a**21>0, a**3<1, b**55>0, b<1, a+b<a*b],

        [0<x, x<1, 0<y, y<1, x**150*y**150>x**150+y**150]
    ]
    expected = [True, True, True, False, True, True, True, False, True, False, True, True, True]

    for i in range(len(problems)):
        val = solve(*problems[i])
        if val == expected[i]:
            print 'Test {} correct.'.format(i+1)
        else:
            print 'Test {} incorrect.'.format(i+1)


#arithmetical_tests()
messages.set_verbosity(messages.normal)

#######
# Bizarre bug here: test6() runs correctly if it is the only test run, but if either 4 or 5 are run
# first, it behaves badly. What could be causing this??
#######

test4()
print '###\n\n'
test5()
print '###\n\n'
test6()
#print solve(x<1, 1<y, x*y>1, u+x>=y+1, x**2*y<2-u*x*y)
#print solve(x*(y+z)<=0, y+z>0, x>=0, x*w>0)



print 'Ran in', round(timeit.default_timer()-t, 3), 'seconds'