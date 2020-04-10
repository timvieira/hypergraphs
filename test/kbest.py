from hypergraphs.apps.parse import parse_forest
from hypergraphs.semirings.lazysort import post_process, post_process2

def test_kbest():
    # XXX: add an automated test.

    if 0:
        from hypergraphs.apps.parse import papa
        H = papa.hypergraph
    else:
        from hypergraphs.apps.parse import abc
        H = abc.hypergraph


    Z = H.Z()
    for x in H.sorted():
#        t = post_process(lambda e: e.head[2], x.data)
#        print(float(x.score/Z), t)
        t = post_process2(lambda e: e.head[2], x.data)
        print(float(x.score/Z), t)

    S = H._sorted()
    B = S.inside()
    A = S.outside(B)

    print('=============================================')
#    item = (1,7,'VP',1)
#    item = (0,1,'Papa',0)

    for item in [*H.nodes
#            (0, 1, 'a', 0),
#            (1, 2, 'b', 0),
#            (2, 3, 'c', 0),
    ]:
#    H.show()
        print('\nitem:', item)

        # XXX: the usual multiplication operation is AC, but ours is not.  To get
        # around this we have to use a function to punch a hole in the product.
    #    for x in B[item] * A[item]:
        for x in A[item]:
#        for x in B[item]:

            t = post_process2(lambda e: e.head[2], x.data)
            print(t)



if __name__ == '__main__':
    test_kbest()
