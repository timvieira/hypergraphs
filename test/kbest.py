from hypergraphs.apps.parse import parse_forest
from hypergraphs.semirings.lazysort import post_process

def test_kbest():
    # XXX: add an automated test.
    from hypergraphs.apps.parse import papa_grammar

    H = parse_forest('Papa ate the caviar with the spoon .'.split(), papa_grammar)
    Z = H.Z()
    for x in H.sorted():
        t = post_process(lambda e: e.head[2], x.data)
        print(float(x.score/Z), t)


if __name__ == '__main__':
    test_kbest()
