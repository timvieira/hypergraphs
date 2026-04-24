from semirings import LogVal

LogVal.to_real = LogVal.__float__
LogVal.lower = LogVal.__float__

from hypergraphs.semirings.vector import make_vector
LogValVector = make_vector(LogVal)
