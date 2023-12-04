simplify_map = {
  "Pli Tv Bu Vb Pj": "Bu Pj",
  "Pli Tv Bu Vb Ss": "Bu Ss",
  "Pli Tv Bu Vb Ay": "Bu Ay",
  "Pli Tv Bu Vb NP": "Bu NP",
  "Pli Tv Bu Vb Pc": "Bu Pc",
  "Pli Tv Bu Vb Pd": "Bu Pd",
  "Pli Tv Bu Vb Sk": "Bu Sk",
  "Pli Tv Bu Vb As": "Bu As",
  "Pli Tv Bi Vb Pj": "Bi Pj",
  "Pli Tv Bi Vb Ss": "Bi Ss",
  "Pli Tv Bi Vb Ay": "Bi Ay",
  "Pli Tv Bi Vb NP": "Bi NP",
  "Pli Tv Bi Vb Pc": "Bi Pc",
  "Pli Tv Bi Vb Pd": "Bi Pd",
  "Pli Tv Bi Vb Sk": "Bi Sk",
  "Pli Tv Bi Vb As": "Bi As",
  "Pli Tv Kd": "Kd",
  "Pli Tv Pvr": "Pvr",
}

def simplify_label(label):
    for key in simplify_map.keys():
        if key in label:
            label = label.replace(key, simplify_map[key])
    return label
