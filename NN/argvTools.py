#!/usr/bin/python3

import getopt
import sys


def parse_argv(argv, defaults):
    """Parse command-line options for nnRun_Chars and return runtime settings."""
    settings = dict(defaults)

    print(argv[1:])
    try:
        opts, args = getopt.getopt(
            argv[1:],
            'hbt:i:n:k:m:d:s:',
            ['help', 'batch', 'tag=', 'iters=', 'nimgs=', 'klayers=', 'mlayers=', 'datapath=', 'batchsize='],
        )

        print('Got options:')
        print(opts)
        print(args)
    except getopt.GetoptError:
        print('Parsing...')
        print('Command line argument error!')
        print('{:} [ -h -b --batch -tTag --tag="MyCoolTag"]]'.format(argv[0]))
        sys.exit(2)

    print('Opts:')
    print(opts)
    for opt, arg in opts:
        print('Processing command line option {} {}'.format(opt, arg))
        if opt in ('-h', '--help'):
            print(
                'Usage: {:} [ -h -b --batch -t/--tag="MyCoolTag  -i/--iters=[] -n/--nimgs=[] -k/--klayers=[] -,/--mlayers=[] "]'.format(
                    argv[0]
                )
            )
            sys.exit()
        elif opt in ('-b', '--batch'):
            settings['gBatch'] = True
        elif opt in ('-t', '--tag'):
            settings['gTag'] = arg
            print('OK, using user-defined histograms tag for output pngs {:}'.format(settings['gTag']))
        elif opt in ('-i', '--iters'):
            settings['nIters'] = int(arg)
            print(f"OK, using user-defined number of iterations {settings['nIters']}")
        elif opt in ('-n', '--nimgs'):
            settings['ntested'] = int(arg)
            print(f"OK, using user-defined number of images to train on as {settings['ntested']}")
        elif opt in ('-k', '--klayers'):
            settings['inputn1'] = int(arg)
            print(f"OK, using user-defined numbers in 1st hidden layer {settings['inputn1']}")
        elif opt in ('-m', '--mlayers'):
            settings['inputn2'] = int(arg)
            print(f"OK, using user-defined numbers in 1st hidden layer {settings['inputn2']}")
        elif opt in ('-d', '--datapath'):
            settings['dataPath'] = arg
            print(f"OK, using user-defined dataset path {settings['dataPath']}")
        elif opt in ('-s', '--batchsize'):
            settings['batch_size'] = int(arg)
            print(f"OK, using user-defined mini-batch size {settings['batch_size']}")

    return settings
