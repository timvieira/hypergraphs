from sympy import Symbol, simplify
from hypergraphs.semirings import base

class Symbolic(base.Semiring):
    @staticmethod
    def lift(w, i):
        return Symbol(i)
    zero = 0
    one = 1
    @staticmethod
    def symbol(i):
        return Symbol(i)
