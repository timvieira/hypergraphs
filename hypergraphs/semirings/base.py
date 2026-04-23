class Semiring:
    @classmethod
    def chart(cls):
        return Chart(cls.zero)
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
    def __pow__(self, K):
        assert isinstance(K, int) and K >= 0
        x = self.one
        for k in range(K):
            x = x * self
        return x
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



class Chart(dict):
    def __init__(self, zero):
        self.zero = zero
        super(Chart, self).__init__()

    def __missing__(self, key):
        return self.zero

    def __add__(self, other):
        assert isinstance(other, Chart), other
        x = Chart(self.zero)
        for k,v in self.items():
            x[k] += v
        for k,v in other.items():
            x[k] += v
        return x

    def __sub__(self, other):
        assert isinstance(other, Chart), other
        x = Chart(self.zero)
        for k,v in self.items():
            x[k] += v
        for k,v in other.items():
            x[k] -= v
        return x

    def round(self, precision):
        x = Chart(self.zero)
        for k,v in self.items():
            x[k] += round(v, precision)
        return x
