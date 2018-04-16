__author__ = 'Lanxue Dang'

NetworkType = ["Small World",
               "PrefAttach",
               "ForestFire",
               "Random",
               "Circle",
               "Full"]
NetworkTypeParams = [
    ["Nodes(int)", "OutDeg(int)", "RewireProb(float)", "Rnd"],
    ["Nodes(int)", "OutDeg(int)", "Rnd"],
    ["Nodes(int)", "FwdProb(float)", "BckProb(float)"],
    ["Nodes(int)", "Edges(int)", "Rnd"],
    ["Nodes(int)", "OutDegree(int)"],
    ["Nodes(int)"]
]

RuleforSelectConnectNode = ["Degree", "Betweenness", "Closeness", "Eigenvector", "Random"]
CanvasMargin = [10, 10, 10, 10]  # left, top, right, bottom
NodeSize = 8  # for graph node
SeedNodeSize = 10
OpinionLeaderSize = 10
ActiveNodeSize = 10
NodeColor = "green"  # for all nodes in a graph
NodeBrushColor = "green"
LineColor = "green"

ActivingNodeBrushColor = "Yellow"
ActivedNodeBrushColor = "red"
SeedNodeBrushColor = "blue"
OpinionLeaderColor = "purple"
PredictNodeBrushColor = "Yellow"
NumbertoConnected = 5

AlgrotihmsforSeedNodes = ["Degree Centrality",
                          "Betweenness Centrality",
                          "Closeness Centrality",
                          "Eigenvector Centrality",
                          "Random Algorithm"]

Infinite = 999999999
EarthRadius = 6378.137
KiloToMile = 0.621371192
MileToKilo = 1.609344

RegressionCoefficients = [-3.038e-08, 1.377e-05, -0.00187, 0.2828]
TimeRegressionCoefficients = [-1.421e-10, + 4.741e-07, -0.0004823, 0.165]
RegressionArea = 0
RegressiontotalT = 0

COLOR_LIST = ["LightPink", "Crimson", "PaleVioletRed", "HotPink", "DeepPink", "MediumVioletRed", "Fuchsia",
              "DarkMagenta", "Purple", "MediumOrchid", "DarkViolet", "DarkOrchid", "Indigo", "BlueViolet",
              "MediumPurple", "MediumSlateBlue", "SlateBlue", "DarkSlateBlue", "Blue", "DarkBlue",
              "RoyalBlue", "CornflowerBlue", "LightSteelBlue", "LightSlateGray", "SlateGray", "DodgerBlue",
              "SteelBlue", "LightSkyBlue", "SkyBlue", "DeepSkyBlue", "LightBlue", "PowderBlue", "CadetBlue",
              "PaleTurquoise", "Cyan", "Aqua", "DarkTurquoise", "DarkSlateGray", "DarkCyan", "Teal",
              "MediumTurquoise", "LightSeaGreen", "Turquoise", "Aquamarine", "MediumAquamarine",
              "MediumSpringGreen", "SpringGreen", "MediumSeaGreen", "SeaGreen", "LightGreen", "PaleGreen",
              "DarkSeaGreen", "LimeGreen", "Lime", "ForestGreen", "Green", "DarkGreen", "Chartreuse",
              "LawnGreen", "GreenYellow", "DarkOliveGreen", "YellowGreen", "OliveDrab",
              "LightGoldenrodYellow", "Yellow", "Olive", "DarkKhaki", "LemonChiffon", "PaleGoldenrod",
              "Khaki", "Gold", "Goldenrod", "DarkGoldenrod", "OldLace", "Wheat", "Moccasin", "Orange",
              "PapayaWhip", "BlanchedAlmond", "NavajoWhite", "AntiqueWhite", "Tan", "BurlyWood", "Bisque",
              "DarkOrange", "Linen", "Peru", "PeachPuff", "SandyBrown", "Chocolate", "SaddleBrown", "Sienna",
              "LightSalmon", "Coral", "OrangeRed", "DarkSalmon", "Tomato", "MistyRose", "Salmon",
              "LightCoral", "RosyBrown", "IndianRed", "Red", "Brown", "Maroon", "Gray", "Black", "White"]
