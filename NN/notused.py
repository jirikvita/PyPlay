  
    #Define variables:
    x = T.matrix('x')
    w = theano.shared(np.array([random(),random()]))
    b = theano.shared(1.)
    learning_rate = 0.01

    #Define mathematical expression:
    z = T.dot(x,w)+b
    a = 1/(1+T.exp(-z))

    a_hat = T.vector('a_hat') #Actual output
    cost = -(a_hat*T.log(a) + (1-a_hat)*T.log(1-a)).sum()
  

    dw,db = T.grad(cost,[w,b])

    train = function(
        inputs = [x,a_hat],
        outputs = [a,cost],
        updates = [
            [w, w-learning_rate*dw],
            [b, b-learning_rate*db]
        ]
    )



    #Define inputs and weights
    inputs = [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1]
    ]
    outputs = [0,0,0,1]

    #Iterate through all inputs and find outputs:
    cost = []
    for iteration in range(30000):
        pred, cost_iter = train(inputs, outputs)
        cost.append(cost_iter)

    #Print the outputs:
    print('The outputs of the NN are:')
    for i in range(len(inputs)):
        print('The output for x1=%d | x2=%d is %.2f' % (inputs[i][0],inputs[i][1],pred[i]) )

    #Plot the flow of cost:
    print('\nThe flow of cost during model run is as following:')
    
    # matplotlib inline
    plt.plot(cost)


