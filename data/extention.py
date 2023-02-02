import random

def postprocess_to_diatonic_melody(note):
    key = note.pitch % 12
    if key in {0, 2, 4, 5, 7, 9, 11}: # Cキーとした時のダイアトニックに該当する場合
        return note.pitch
    else: # それ以外の場合は，最近傍のpitchに修正
        if random.random() < 0.5:
            nearest_pitch = note.pitch - 1
        else:
            nearest_pitch = note.pitch + 1
        return nearest_pitch