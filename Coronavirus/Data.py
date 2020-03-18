#!/usr/bin/python

# data from https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports/
# date, total cases, deaths total
# global data
# cases here are laboratory testes, not clinically

Data = [ # world cases and deaths
         ['20.1.2020', 282, 6],
         ['21.1.2020', 314, 6],
         ['23.1.2020', 581, 17],
         ['24.1.2020', 846, 25],
         ['25.1.2020', 1320, 41],
         ['26.1.2020', 2014, 56],
         ['27.1.2020', 2798, 80],
         ['28.1.2020', 4593, 106],
         ['29.1.2020', 6065, 132],
         ['30.1.2020', 7818, 170],
         ['31.1.2020', 9826, 213],
         [ '1.2.2020', 11953, 259],
         [ '2.2.2020', 14557, 305],
         [ '3.2.2020', 17391, 362],
         [ '4.2.2020', 20630, 426],
         [ '5.2.2020', 24554, 494],
         [ '6.2.2020', 28276, 565],
         [ '7.2.2020', 31481, 638],
         [ '8.2.2020', 34886, 724],
         [ '9.2.2020', 37558, 813], 
         ['10.2.2020', 40554, 910],
         ['11.2.2020', 43103, 1018],
         ['12.2.2020', 45171, 1115],
         ['13.2.2020', 46997, 1369],
         ['14.2.2020', 49053, 1383],
         ['15.2.2020', 50580, 1526],
         ['16.2.2020', 51857, 1669],
         # now split:
         # China, nonChina
         ['17.2.2020', [70635, 794], [1772, 3]], # laboratory and clinically confirmed case from now on!
         ['18.2.2020', [72528, 804], [1870, 3]],
         ['19.2.2020', [74280, 924], [2006, 3]],
         ['20.2.2020', [74675, 1073], [2121, 8]],
         ['21.2.2020', [75569, 1200], [2239, 8]],
         ['22.2.2020', [76392, 1402], [2348, 11]], # again, back to the lab confirmed cases only!
         ['23.2.2020', [77042, 1769], [2445, 17]],
         ['24.2.2020', [77262, 2069], [2595, 23]],
    
         # added       China nonCh. Korea Japan Italy     Ger  CZ Fr Spain UK Iran USA; deaths: China, non-China
         ['25.2.2020', [77780, 2459,  977, 157, 229,      16,  0, 12,  2, 13, 61,  53], [2666, 34, ]],
         ['26.2.2020', [78191, 2918, 1261, 164, 322,      18,  0, 12,  2, 13, 95,  53], [2718, 43, ]],
         ['27.2.2020', [78630, 3664, 1766, 186, 400,      21,  0, 18, 12, 13, 141, 59], [2747, 57, ]],
         ['28.2.2020', [78961, 4691, 2337, 210, 659,      26,  0, 38, 25, 16, 245, 59], [2791, 67, ]],
         ['29.2.2020', [79394, 6009, 3150, 230, 888,      57,  0, 57, 32, 20, 388, 62], [2838, 86, ]],

         # added CZ data in addition:
    
         # Country:    China nonCh. Korea Japan  Italy     Ger CZ  Fr   Spain     UK   Iran  USA
         [ '1.3.2020', [79968, 7169,  3736, 239,  1128,    57,   3, 100,    45,   23,   593,   62],   [2873, 104]],
         [ '2.3.2020', [80174, 8774,  4212, 254,  1689,   129,   4, 100,    45,   36,   978,   62],   [2915, 128]],
         [ '3.3.2020', [80304, 10566, 4812, 268,  2036,   157,   5, 191,   114,   39,  1501,   64],   [2946, 166]],
         [ '4.3.2020', [80422, 12668, 5328, 284,  2502,   196,   8, 212,   151,   51,  2336,  108],   [2984, 214]],
         [ '5.3.2020', [80565, 14768, 5766, 317,  3089,   262,  12, 282,   198,   89,  2922,  129],   [3015, 267]],
         [ '6.3.2020', [80711, 17481, 6284, 349,  3858,   534,  19, 420,   257,  118,  3513,  148],   [3045, 335]],
         [ '7.3.2020', [80813, 21110, 6767, 408,  4636,   639,  26, 613,   374,  167,  4747,  213],   [3073, 413]],
         [ '8.3.2020', [80859, 24727, 7134, 455,  5883,   795,  32, 706,   430,  210,  5823,  213],   [3100, 484]],
         [ '9.3.2020', [80904, 28674, 7382, 488,  7375,  1112,  38, 1116,  589,  277,  6566,  213],   [3123, 686]],
         ['10.3.2020', [80924, 32778, 7513, 514,  9172,  1139,  63, 1402, 1024,  323,  7161,  472],   [3140, 872]],
         ['11.3.2020', [80955, 37371, 7755, 568, 10149,  1296,  94, 1774, 1639,  373,  8042,  696],   [3162, 1130]],
         ['12.3.2020', [80981, 44067, 7869, 620, 12462,  1567, 116, 2269, 2140,  460,  9000,  987],   [3173, 1440]],
         ['13.3.2020', [80991, 51767, 7979, 675, 15113,  2369, 141, 2868, 2965,  594, 10075, 1264], [3180, 1775, ]],
         ['14.3.2020', [81021, 61518, 8086, 716, 17660,  3062, 189, 3640, 4231,  802, 11364, 1678], [3194, 2199, ]],
         ['15.3.2020', [81048, 72469, 8162, 780, 21157,  3795, 298, 4469, 5753, 1144, 12729, 1678], [3204, 2531 ]],
         ['16.3.2020', [81077, 86434, 8236, 814, 24747,  4838, 383, 5380, 7753, 1395, 14991, 1678], [3218, 3388 ]],
  ['17.3.2020', [81116, 179112-81116, 8320, 829, 27980,  6012, 434, 6573, 9191, 1547, 14991, 3503], [3231, 7426-3231]],
        #['18.3.2020', [, , ], [,  ]],
        #['19.3.2020', [, , ], [,  ]],
        #['20.3.2020', [, , ], [,  ]],
        #['21.3.2020', [, , ], [,  ]],
        #['22.3.2020', [, , ], [,  ]],
        #['23.3.2020', [, , ], [,  ]],
        #['24.3.2020', [, , ], [,  ]],
        #['25.3.2020', [, , ], [,  ]],
        #['26.3.2020', [, , ], [,  ]],
        #['27.3.2020', [, , ], [,  ]],
        #['28.3.2020', [, , ], [,  ]],
        #['29.3.2020', [, , ], [,  ]],
        #['30.3.2020', [, , ], [,  ]],
        #['31.3.2020', [, , ], [,  ]],

]
