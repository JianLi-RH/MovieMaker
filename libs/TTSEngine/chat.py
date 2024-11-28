"""
https://chattts.com/***REMOVED***Features
https://blog.csdn.net/u010522887/article/details/139719895
"""

import ChatTTS
import csv
***REMOVED***
import torch
import torchaudio
from IPython.display import Audio



def get_speaker(speaker='男'):
    
    all_***REMOVED***
        '男': '3.281,2.916,2.316,2.280,-0.884,0.723,-10.224,-0.266,2.000,4.442,1.427,-1.075,-3.027,0.438,1.224,1.043,-0.423,-3.808,0.740,-4.704,10.824,-0.362,-0.291,10.761,1.843,6.068,-4.458,5.142,4.183,4.333,-4.859,-1.444,0.901,3.424,-0.992,-1.645,0.230,0.818,-2.294,1.417,2.839,-0.533,-2.302,-1.379,-3.898,0.998,-0.196,14.249,1.641,-6.927,-1.283,6.005,-0.125,1.531,3.420,8.003,-0.202,-2.823,4.435,2.378,5.186,4.951,1.945,-2.100,1.644,1.921,-1.138,6.229,-5.203,3.610,-0.919,-5.326,2.130,-4.196,21.073,-0.012,11.642,-4.142,-0.581,-0.138,0.882,-1.235,2.377,6.930,3.499,-0.239,4.493,0.411,-2.122,-7.575,0.809,0.885,0.008,0.900,9.930,-3.983,-0.462,-0.699,-4.674,5.071,-3.361,-2.448,0.742,-3.553,-6.620,-0.570,2.859,-3.424,8.462,2.013,-0.204,6.866,-1.946,0.946,-0.440,-4.125,1.194,-2.351,5.368,-5.819,0.049,-0.918,-1.812,-2.288,4.262,12.440,2.084,-0.156,-5.392,0.106,3.279,4.475,0.139,1.006,5.619,0.716,-5.918,-0.774,-5.805,-7.207,-0.402,0.228,-1.422,4.098,1.244,-1.481,-0.672,-3.778,1.220,-0.947,0.807,-1.658,5.977,7.529,-1.070,-2.112,-2.946,-1.739,-2.284,-1.045,-0.442,-1.813,1.269,-2.797,0.321,0.155,-0.379,-2.554,-1.409,2.421,0.318,4.154,0.647,0.610,-3.516,4.489,3.286,3.552,-0.358,1.132,-2.382,-0.612,-5.613,-0.168,-0.680,1.723,-20.408,-2.504,5.870,1.631,4.703,-0.359,0.367,-1.661,-2.172,-9.155,-3.521,-1.058,4.984,-4.086,-3.736,8.959,-1.759,-1.117,17.161,1.497,1.160,2.355,2.584,-2.312,-2.436,0.787,-4.522,5.730,-2.144,1.276,-5.419,-5.749,8.496,5.873,-0.472,-1.497,1.162,8.649,0.326,-0.714,4.123,-3.431,-1.579,0.016,-4.171,-15.907,0.607,1.909,-3.616,-0.803,-0.046,1.836,5.704,-0.730,3.511,7.312,-0.066,0.972,0.199,1.777,-3.750,0.089,18.306,1.156,-2.320,1.280,-2.491,-2.765,-19.535,-1.302,-8.004,-1.833,0.941,-3.547,-0.741,-1.860,-1.626,-2.555,-0.086,0.221,7.494,8.971,-2.007,-2.635,-2.494,-1.794,-5.080,4.963,-1.599,-1.862,-0.225,0.518,2.853,1.657,-0.257,-1.165,-7.366,2.681,5.232,0.592,-2.189,1.606,-1.407,-2.102,-2.945,2.853,8.901,0.029,-5.533,2.786,-0.961,2.544,1.200,-1.171,1.578,-1.681,-0.955,-2.784,2.281,-3.195,2.811,-1.718,0.810,-0.603,-1.736,-1.373,-0.891,-5.330,-1.381,9.614,4.155,0.047,-1.053,3.823,1.010,0.042,-2.849,1.482,0.798,19.538,-12.677,3.608,-1.660,4.493,2.087,-0.906,1.919,1.318,-1.815,-1.287,9.502,0.361,-4.073,-0.589,-1.339,5.567,1.668,0.479,0.333,-26.911,-3.391,-1.020,-4.389,-4.838,2.512,1.478,-3.802,-1.676,-0.469,0.898,3.632,-1.620,0.432,-1.906,-1.674,-7.568,0.361,1.675,-1.164,-13.232,-1.971,-3.983,-2.921,8.597,-0.231,-0.449,0.392,4.953,-5.841,0.047,4.419,-5.355,-4.528,-1.681,-8.136,0.295,3.060,-7.177,-1.483,1.266,2.680,2.265,-8.495,-2.133,1.485,-1.022,-3.286,-1.811,-1.127,-4.633,0.473,6.305,-4.399,-0.452,1.234,-0.245,4.392,2.415,-2.063,3.707,-4.495,3.831,29.219,-11.790,-0.259,1.078,-7.773,1.709,-1.397,-0.067,0.768,2.663,-1.454,-3.022,-1.810,5.015,1.889,1.119,-1.413,-3.240,4.198,14.864,-2.950,1.651,-3.228,-1.095,-2.941,1.231,-8.138,-1.936,-2.160,5.722,-5.481,0.544,-0.786,-1.140,-1.677,2.252,0.031,-2.385,-1.336,3.705,-3.270,-0.495,2.222,1.482,-6.423,-0.509,-1.519,5.775,0.420,-2.140,-3.850,2.567,8.821,-6.976,-6.974,-1.999,-3.226,-1.778,-6.607,9.911,-9.480,1.611,-0.308,-9.211,-1.476,1.751,-0.466,-2.363,-2.358,-4.866,-1.147,-3.444,-6.753,-0.507,-1.245,-2.413,-1.962,2.347,-0.094,-0.745,0.668,2.071,-0.755,-2.450,6.657,7.899,-6.277,2.189,-2.127,2.291,6.095,0.927,-0.250,-1.662,4.031,6.098,-17.201,-9.840,-0.729,1.427,3.222,-0.208,2.380,1.103,1.147,4.051,2.980,0.371,4.143,-1.133,0.486,-0.588,-0.392,-1.507,-0.803,-6.217,-0.947,-5.456,-9.972,-1.221,-1.677,0.376,-0.066,-0.987,-1.144,2.161,-0.282,1.924,1.364,10.975,-6.569,-5.145,-1.047,-1.040,-6.781,-0.387,-21.836,0.683,3.180,-0.757,-0.025,3.418,0.626,1.140,-4.496,-2.867,-2.973,10.865,2.019,-6.465,9.939,-0.107,-2.146,4.367,0.148,-1.867,1.160,-13.273,7.023,0.068,-1.266,-4.770,-1.669,-0.643,1.833,-0.005,-3.790,3.982,-4.962,-0.175,2.481,-0.260,-1.224,1.529,1.225,5.921,5.203,2.303,-2.092,-0.826,5.299,-0.106,0.513,-3.272,1.970,-2.140,-0.033,-3.860,2.144,2.398,-1.478,4.514,1.553,0.901,-2.297,4.627,-0.360,-0.540,0.280,4.952,-2.520,-3.369,19.334,-0.363,0.924,-0.099,-1.544,1.592,-0.163,6.088,-2.863,2.072,-0.336,-1.897,4.755,-3.300,-6.699,-3.852,0.276,-5.298,-0.012,-6.344,3.159,9.078,-2.398,-1.005,-5.604,1.775,4.505,1.172,-3.949,-1.302,5.698,-0.228,-8.495,-4.654,2.533,-4.065,0.098,0.392,2.624,0.928,-0.316,-0.798,-1.814,-3.183,-3.962,-2.339,-2.051,3.898,-1.971,-2.940,8.407,0.673,2.367,7.541,3.822,-6.822,-2.951,-2.204,10.548,-0.255,-1.850,1.263,1.779,1.912,0.608,-1.325,2.220,2.637,1.699,-8.412,-1.397,-0.422,-4.485,3.247,0.382,7.712,-2.262,-1.700,-0.506,7.307,7.266,-0.498,-6.427,-5.879,14.950,0.991,3.057,10.976,-3.662,-0.781,-0.486,7.302,1.052,-3.824,-9.337,-0.783,3.696,-1.935,1.468,-2.889,-1.950,-1.511,2.164,2.791,0.533,-0.986,0.150,1.650,0.909,1.949,-4.902,1.626,0.463,2.622,-1.272,2.164,2.691,-4.966,-0.418,-0.016,-8.490,-3.339,5.198,-3.525,2.392,0.445,1.293,3.217,6.489,1.553,2.088,-1.272,-1.077,3.093,-7.780,4.537,0.824,-1.956,1.215,0.527,2.576,-3.828,2.519,3.089,-4.081,-2.068,-0.241,0.574,-0.245,-1.646,-0.643,3.113,0.861,9.045,-4.593,5.160,3.660,-1.495',
        '女': '-4.741,0.419,-3.355,3.652,-1.682,-1.254,9.719,1.436,0.871,12.334,-0.175,-2.653,-3.132,0.525,1.573,-0.351,0.030,-3.154,0.935,-0.111,-6.306,-1.840,-0.818,9.773,-1.842,-3.433,-6.200,-4.311,1.162,1.023,11.552,2.769,-2.408,-1.494,-1.143,12.412,0.832,-1.203,5.425,-1.481,0.737,-1.487,6.381,5.821,0.599,6.186,5.379,-2.141,0.697,5.005,-4.944,0.840,-4.974,0.531,-0.679,2.237,4.360,0.438,2.029,1.647,-2.247,-1.716,6.338,1.922,0.731,-2.077,0.707,4.959,-1.969,5.641,2.392,-0.953,0.574,1.061,-9.335,0.658,-0.466,4.813,1.383,-0.907,5.417,-7.383,-3.272,-1.727,2.056,1.996,2.313,-0.492,3.373,0.844,-8.175,-0.558,0.735,-0.921,8.387,-7.800,0.775,1.629,-6.029,0.709,-2.767,-0.534,2.035,2.396,2.278,2.584,3.040,-6.845,7.649,-2.812,-1.958,8.794,2.551,3.977,0.076,-2.073,-4.160,0.806,3.798,-1.968,-4.690,5.702,-4.376,-2.396,1.368,-0.707,4.930,6.926,1.655,4.423,-1.482,-3.670,2.988,-3.296,0.767,3.306,1.623,-3.604,-2.182,-1.480,-2.661,-1.515,-2.546,3.455,-3.500,-3.163,-1.376,-12.772,1.931,4.422,6.434,-0.386,-0.704,-2.720,2.177,-0.666,12.417,4.228,0.823,-1.740,1.285,-2.173,-4.285,-6.220,2.479,3.135,-2.790,1.395,0.946,-0.052,9.148,-2.802,-5.604,-1.884,1.796,-0.391,-1.499,0.661,-2.691,0.680,0.848,3.765,0.092,7.978,3.023,2.450,-15.073,5.077,3.269,2.715,-0.862,2.187,13.048,-7.028,-1.602,-6.784,-3.143,-1.703,1.001,-2.883,0.818,-4.012,4.455,-1.545,-14.483,-1.008,-3.995,2.366,3.961,1.254,-0.458,-1.175,2.027,1.830,2.682,0.131,-1.839,-28.123,-1.482,16.475,2.328,-13.377,-0.980,9.557,0.870,-3.266,-3.214,3.577,2.059,1.676,-0.621,-6.370,-2.842,0.054,-0.059,-3.179,3.182,3.411,4.419,-1.688,-0.663,-5.189,-5.542,-1.146,2.676,2.224,-5.519,6.069,24.349,2.509,4.799,0.024,-2.849,-1.192,-16.989,1.845,6.337,-1.936,-0.585,1.691,-3.564,0.931,0.223,4.314,-2.609,0.544,-1.931,3.604,1.248,-0.852,2.991,-1.499,-3.836,1.774,-0.744,0.824,7.597,-1.538,-0.009,0.494,-2.253,-1.293,-0.475,-3.816,8.165,0.285,-3.348,3.599,-4.959,-1.498,-1.492,-0.867,0.421,-2.191,-1.627,6.027,3.667,-21.459,2.594,-2.997,5.076,0.197,-3.305,3.998,1.642,-6.221,3.177,-3.344,5.457,0.671,-2.765,-0.447,1.080,2.504,1.809,1.144,2.752,0.081,-3.700,0.215,-2.199,3.647,1.977,1.326,3.086,34.789,-1.017,-14.257,-3.121,-0.568,-0.316,11.455,0.625,-6.517,-0.244,-8.490,9.220,0.068,-2.253,-1.485,3.372,2.002,-3.357,3.394,1.879,16.467,-2.271,1.377,-0.611,-5.875,1.004,12.487,2.204,0.115,-4.908,-6.992,-1.821,0.211,0.540,1.239,-2.488,-0.411,2.132,2.130,0.984,-10.669,-7.456,0.624,-0.357,7.948,2.150,-2.052,3.772,-4.367,-11.910,-2.094,3.987,-1.565,0.618,1.152,1.308,-0.807,1.212,-4.476,0.024,-6.449,-0.236,5.085,1.265,-0.586,-2.313,3.642,-0.766,3.626,6.524,-1.686,-2.524,-0.985,-6.501,-2.558,0.487,-0.662,-1.734,0.275,-9.230,-3.785,3.031,1.264,15.340,2.094,1.997,0.408,9.130,0.578,-2.239,-1.493,11.034,2.201,6.757,3.432,-4.133,-3.668,2.099,-6.798,-0.102,2.348,6.910,17.910,-0.779,4.389,1.432,-0.649,5.115,-1.064,3.580,4.129,-4.289,-2.387,-0.327,-1.975,-0.892,5.327,-3.908,3.639,-8.247,-1.876,-10.866,2.139,-3.932,-0.031,-1.444,0.567,-5.543,-2.906,1.399,-0.107,-3.044,-4.660,-1.235,-1.011,9.577,2.294,6.615,-1.279,-2.159,-3.050,-6.493,-7.282,-8.546,5.393,2.050,10.068,3.494,8.810,2.820,3.063,0.603,1.965,2.896,-3.049,7.106,-0.224,-1.016,2.531,-0.902,1.436,-1.843,1.129,6.746,-2.184,0.801,-0.965,-7.555,-18.409,6.176,-3.706,2.261,4.158,-0.928,2.164,-3.248,-4.892,-0.008,-0.521,7.931,-10.693,4.320,-0.841,4.446,-1.591,-0.702,4.075,3.323,-3.406,-1.198,-5.518,-0.036,-2.247,-2.638,2.160,-9.644,-3.858,2.402,-2.640,1.683,-0.961,-3.076,0.226,5.106,0.712,0.669,2.539,-4.340,-0.892,0.732,0.775,-2.757,4.365,-2.368,5.368,0.342,-0.655,0.240,0.775,3.686,-4.008,16.296,4.973,1.851,4.747,0.652,-2.117,6.470,2.189,-8.467,3.236,3.745,-1.332,3.583,-2.504,5.596,-2.440,0.995,-2.267,-3.322,3.490,1.156,1.716,0.669,-3.640,-1.709,5.055,6.265,-3.963,2.863,14.129,5.180,-3.590,0.393,0.234,-3.978,6.946,-0.521,1.925,-1.497,-0.283,0.895,-3.969,5.338,-1.808,-3.578,2.699,2.728,-0.895,-2.175,-2.717,2.574,4.571,1.131,2.187,3.620,-0.388,-3.685,0.979,2.731,-2.164,1.628,-1.006,-7.766,-11.033,-10.985,-2.413,-1.967,0.790,0.826,-1.623,-1.783,3.021,1.598,-0.931,-0.605,-1.684,1.408,-2.771,-2.354,5.564,-2.296,-4.774,-2.830,-5.149,2.731,-3.314,-1.002,3.522,3.235,-1.598,1.923,-2.755,-3.900,-3.519,-1.673,-2.049,-10.404,6.773,1.071,0.247,1.120,-0.794,2.187,-0.189,-5.591,4.361,1.772,1.067,1.895,-5.649,0.946,-2.834,-0.082,3.295,-7.659,-0.128,2.077,-1.638,0.301,-0.974,4.331,11.711,4.199,1.545,-3.236,-4.404,-1.333,0.623,1.414,-0.240,-0.816,-0.808,-1.382,0.632,-5.238,0.120,10.634,-2.026,1.702,-0.469,1.252,1.173,3.015,-8.798,1.633,-5.323,2.149,-6.481,11.635,3.072,5.642,5.252,4.702,-3.523,-0.594,4.150,1.392,0.554,-4.377,3.646,-0.884,1.468,0.779,2.372,-0.101,-5.702,0.539,-0.440,5.149,-0.011,-1.899,-1.349,-0.355,0.076,-0.100,-0.004,5.346,6.276,0.966,-3.138,-2.633,-3.124,3.606,-3.793,-3.332,2.359,-0.739,-3.301,-2.775,-0.491,3.283,-1.394,-1.883,1.203,1.097,2.233,2.170,-2.980,-15.800,-6.791,-0.175,-4.600,-3.840,-4.179,6.568,5.935,-0.431,4.623,4.601,-1.726,0.410,2.591,4.016,8.169,1.763,-3.058,-1.340,6.276,4.682,-0.089,1.301,-4.817'
***REMOVED***
    
    if not speaker:
        speaker = '男'
    if isinstance(speaker, str):
        spk = all_speaker.get(speaker)
        return torch.tensor([float(x) for x in spk.split(",")])
    if isinstance(speaker, int):
        ***REMOVED*** https://www.ttslist.com/
        ***REMOVED*** 男： 14 17 19 400 4200 8800
        ***REMOVED*** 中： 18
        ***REMOVED*** 女： 16 200 300 4100 9600
        
        csv_file = os.path.join("libs/TTSEngine/speaker", f"{speaker***REMOVED***.csv")
        spk = []
        with open(csv_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                spk.append(float(row[0]))
        return torch.tensor(spk)
        

def covert_text_to_sound(text, output, speaker=None):
    
    chat = ChatTTS.Chat()
    chat.load(compile=True)
    
    rand_speaker = get_speaker(speaker)
    params_infer_code = ChatTTS.Chat.InferCodeParams(
        spk_emb = rand_speaker, ***REMOVED*** add sampled speaker 
        temperature = .4,   ***REMOVED*** using custom temperature
        top_P = 0.7,        ***REMOVED*** top P decode
        top_K = 20,         ***REMOVED*** top K decode
        prompt="[speed_4]"   ***REMOVED*** 语速 0 ~ 9
    )

    texts = [text,]
    wavs = chat.infer(texts, 
                      params_infer_code=params_infer_code,
                      skip_refine_text=True,
                      refine_text_only=False    ***REMOVED*** 禁止自动停顿
                      )

    try:
        torchaudio.save(output, torch.from_numpy(wavs[0]).unsqueeze(0), 24000)
    except:
        torchaudio.save(output, torch.from_numpy(wavs[0]), 24000)
        
        
***REMOVED***
    ***REMOVED*** get_speaker()
    covert_text_to_sound("难道想去高俅那里举报洒家", "output/难道想去高俅那里举报洒家.mp3", None)