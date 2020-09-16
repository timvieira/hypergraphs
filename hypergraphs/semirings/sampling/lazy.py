import numpy as np


class Sample:

    def __init__(self, w, d):
        self.w = w
        self.d = d

    def __iter__(self):
        while True:
            X = -np.log(np.random.uniform(0,1)) / self.w
            yield (X, self.d)

    def __add__(self, other):
        if other is zero: return self
        if self is zero: return other
        return Sum(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if other is zero: return zero
        if self is zero: return zero
        return Prod(self, other)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.w}, {self.d})'

    @classmethod
    def zero(cls):
        return zero

    @classmethod
    def one(cls):
        return one


class Sum(Sample):
    def __init__(self, x, y):
        self.x = x; self.y = y
        super().__init__(x.w + y.w, d=[x,y])
    def __iter__(self):
        while True:
            for x,y in zip(self.x, self.y):
                yield min(x, y)


class Prod(Sample):
    def __init__(self, x, y):
        self.x = x; self.y = y
        super().__init__(x.w * y.w, d=[x,y])
    def __iter__(self):
        while True:
            for x,y in zip(self.x, self.y):
                xs,xd = x
                _,yd = y

                # We have to random variates
                #  X = -log(Ux)/Wx ~ Expon(Wx)
                #  Y = -log(Uy)/Wy ~ Expon(Wy)
                # We want to construct a new one using existing randomness
                #  Z = -log(U)/(Wx*Wy)

                # A simple manipulation shows that dividing by Wy works!
                #   X/Wy = (-log(Ux)/Wx)/Wy ~ Z

                Z = xs / self.y.w

                # We could, instead, generate a fresh random variate
                #Z = -np.log(np.random.uniform(0,1)) / (self.x.w * self.y.w)

                yield [Z, [xd, yd]]


zero = Sample(0.0, None)
one = Sample(1.0, ())
