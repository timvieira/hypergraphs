from collections import defaultdict
class Semiring:
    @classmethod
    def chart(cls):
        return defaultdict(lambda: cls.zero)
    zero = None
    one = None
    def __add__(self, other):
        raise NotImplementedError
    def __mul__(self, other):
        raise NotImplementedError
    @classmethod
    def lift(cls, *args):
        return cls(*args)
    @classmethod
    def multiplicity(cls, v, m):
        raise NotImplementedError
    @classmethod
    def multiple(cls, m):
        return cls.multiplicity(cls.one, m)
    def star_approx(self, T):
        v = self.one
        for _ in range(T):
            v += self * v
        return v
    def star_fixpoint(self):
        prev = self.one
        while True:
            curr = prev + self * prev
            if prev == curr: return curr
            prev = curr
