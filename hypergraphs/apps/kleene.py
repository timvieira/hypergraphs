def kleene(A, Weight):
    # initialization
    [N,_] = A.shape
    R = A.copy(); S = A.copy()
    for j in range(N):
        R,S = S,R
        R[:,:] = Weight.zero
        for i in range(N):
            for k in range(N):
                # i ➙ j ⇝ j ➙ k
                R[i,k] = S[i,k] + S[i,j] * Weight.star(S[j,j]) * S[j,k]
    # post processing fix-up: add the identity matrix
    for i in range(N): R[i,i] += Weight.one
    return R
