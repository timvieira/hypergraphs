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
