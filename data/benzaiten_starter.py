import music21
import numpy as np
import matplotlib.pyplot as plt
import mido
import csv
import IPython.display as ipd
import midi2audio
import glob
import pretty_midi # TODO: midoで代替できそうだったら代替する
from collections import OrderedDict
import subprocess
import IPython
import glob

from extention import postprocess_to_diatonic_melody

# 各種定数、パスの設定
TOTAL_MEASURES = 240        # 学習用MusicXMLを読み込む際の小節数の上限
UNIT_MEASURES = 4           # 1回の生成で扱う旋律の長さ
BEAT_RESO = 4               # 1拍を何個に分割するか（4の場合は16分音符単位）
N_BEATS = 4                 # 1小節の拍数（今回は4/4なので常に4）
NOTENUM_FROM = 36           # 扱う音域の下限（この値を含む）
NOTENUM_THRU = 84           # 扱う音域の上限（この値を含まない）
INTRO_BLANK_MEASURES = 4    # ブランクおよび伴奏の小節数の合計
MELODY_LENGTH = 8           # 生成するメロディの長さ（小節数）
 
KEY_ROOT = "C"              # 生成するメロディの調のルート（"C" or "A"）
KEY_MODE = "major"          # 生成するメロディの調のモード（"major" or "minor"）

basedir = "/data/" # 作業フォルダ
backing_file = "input/sample1_backing.mid"       # 適宜変更すること
chord_file = "input/sample1_chord.csv"           # 適宜変更すること
output_file = "output.mid"                # 自分のエントリーネームに変更すること
bundle_file_path = basedir+"ckpt/chord_pitches_improv.mag"
output_dir = basedir+"output/"


# 指定された仕様のcsvファイルを読み込んで
# ChordSymbol列を返す
def read_chord_file(file):
  chord_seq = [None] * (MELODY_LENGTH * N_BEATS)
  with open(file) as f:
    reader = csv.reader(f)
    for row in reader:
      m = int(row[0]) # 小節番号（0始まり）
      if m < MELODY_LENGTH:
        b = int(row[1]) # 拍番号（0始まり、今回は0または2）
        chord_seq[m*4+b] = music21.harmony.ChordSymbol(root=row[2], 
                                                       kind=row[3], 
                                                       bass=row[4])
  for i in range(len(chord_seq)):
    if chord_seq[i] != None:
      chord = chord_seq[i]
    else:
      chord_seq[i] = chord
  return chord_seq

# コード進行からChordSymbol列を生成
# divisionは1小節に何個コードを入れるか
def make_chord_seq(chord_prog, division):
  T = int(N_BEATS * BEAT_RESO / division)
  seq = [None] * (T * len(chord_prog))
  for i in range(len(chord_prog)):
    for t in range(T):
      if isinstance(chord_prog[i], music21.harmony.ChordSymbol):
        seq[i * T + t] = chord_prog[i]
      else:
        seq[i * T + t] = music21.harmony.ChordSymbol(chord_prog[i])
  return seq

# ChordSymbol列をmany-hot (chroma) vector列に変換
def chord_seq_to_chroma(chord_seq):
  N = len(chord_seq)
  matrix = np.zeros((N, 12))
  for i in range(N):
    if chord_seq[i] != None:
      for note in chord_seq[i]._notes:
        matrix[i, note.pitch.midi % 12] = 1
  return matrix

# 空（全要素がゼロ）のピアノロールを生成
def make_empty_pianoroll(length):
  return np.zeros((length, NOTENUM_THRU - NOTENUM_FROM + 1))


# ピアノロールを描画し、MIDIファイルを再生
def show_and_play_midi(pianoroll, transpose, src_filename, dst_filename):
  # ピアノロール（one-hot vector列）をノートナンバー列に変換
  def calc_notenums_from_pianoroll(pianoroll):
    notenums = []
    for i in range(pianoroll.shape[0]):
      n = np.argmax(pianoroll[i, :])
      nn = -1 if n == pianoroll.shape[1] - 1 else n + NOTENUM_FROM
      notenums.append(nn)
    return notenums

  # 連続するノートナンバーを統合して (notenums, durations) に変換
  def calc_durations(notenums):
    N = len(notenums)
    duration = [1] * N
    for i in range(N):
      k = 1
      while i + k < N:
        if notenums[i] > 0 and notenums[i] == notenums[i + k]:
          notenums[i + k] = 0
          duration[i] += 1
        else:
          break
        k += 1
    return notenums, duration

  # MIDIファイルを生成
  def make_midi(notenums, durations, transpose, src_filename, dst_filename):
    midi = mido.MidiFile(src_filename)
    MIDI_DIVISION = midi.ticks_per_beat
    track = mido.MidiTrack()
    midi.tracks.append(track)
    init_tick = INTRO_BLANK_MEASURES * N_BEATS * MIDI_DIVISION
    prev_tick = 0
    for i in range(len(notenums)):
      if notenums[i] > 0:
        curr_tick = int(i * MIDI_DIVISION / BEAT_RESO) + init_tick
        track.append(mido.Message('note_on', note=notenums[i]+transpose, 
                                  velocity=100, time=curr_tick - prev_tick))
        prev_tick = curr_tick
        curr_tick = int((i + durations[i]) * MIDI_DIVISION / BEAT_RESO) + init_tick
        track.append(mido.Message('note_off', note=notenums[i]+transpose, 
                                  velocity=100, time=curr_tick - prev_tick))
        prev_tick = curr_tick
    midi.save(dst_filename)

  plt.matshow(np.transpose(pianoroll))
  plt.show()
  notenums = calc_notenums_from_pianoroll(pianoroll)
  notenums, durations = calc_durations(notenums)
  make_midi(notenums, durations, transpose, src_filename, dst_filename)
  fs = midi2audio.FluidSynth(sound_font="/usr/share/sounds/sf2/FluidR3_GM.sf2")
  fs.midi_to_audio(dst_filename, "output.wav")
  ipd.display(ipd.Audio("output.wav"))



def parse_chord_for_magenta(filepath:str) -> str:
    # magenta向けにコード進行列のstringを加工
    # TODO: chord記法の変換パターンの網羅
    dict_modify_chords = OrderedDict({
        'dominant-seventh': '7 dom',
        'augmented-seventh': '+maj7',
        'seventh': '7',
        # '-seventh': '7',
        'major': 'M',
        'minor': 'm',
        '-': '',
        'augmented': '+',
        'diminished': 'o',
        '-': 'b'
    })
    chords_str = '"'
    with open(filepath, 'r') as f:
        chords_all = f.readlines()
    for i,chords_cur in enumerate(chords_all):
        chords_cur_list = chords_cur.split(',')[0:4]
        if int(chords_cur_list[0]) >= MELODY_LENGTH: break # 8小節を超えたらループを抜ける
        if chords_cur_list[1] != '0': continue # 小節頭のコード進行のみ採用（その他は捨象する）
        for elem in dict_modify_chords:
            chords_cur_list[3] = chords_cur_list[3].replace(elem, dict_modify_chords[elem])
        chords_str += chords_cur_list[2] + chords_cur_list[3] + ' '
    chords_str += '"'
    return chords_str




def run():
    chord_prog = read_chord_file(basedir + chord_file)
    chroma_vec = chord_seq_to_chroma(make_chord_seq(chord_prog, N_BEATS))
    pianoroll = make_empty_pianoroll(chroma_vec.shape[0])
    chord_prog_magenta = parse_chord_for_magenta(basedir + chord_file)
    
    print(bundle_file_path)
    print(output_dir)

    
    command = 'improv_rnn_generate --config="attention_improv" --bundle_file='+bundle_file_path+' --output_dir='+output_dir+' --num_outputs=1 --primer_melody="[60]" --backing_chords='+chord_prog_magenta

    # 拡張パック 乱数で決める
    # initial_notes = [random.randint(60, 75) for _ in range(3)]
    # command = 'improv_rnn_generate --config="attention_improv" --bundle_file='+bundle_file_path+' --output_dir='+output_dir+f' --num_outputs=10 --primer_melody="{initial_notes}" --backing_chords='+chord_prog_magenta

    # 拡張パック Chord Pitches Improv or (basic_improv)
    # command = 'improv_rnn_generate --config="chord_pitches_improv" --bundle_file='+bundle_file_path+' --output_dir='+output_dir+' --num_outputs=10 --primer_melody="[60]" --backing_chords='+chord_prog_magenta
    print(command)
    subprocess.run(command, shell=True)

    # 最新の生成ファイルを指定（どれを選ぶかは自由。例：人間の耳で確認して良いものを指定する）
    melody_filepaths = glob.glob(basedir + '/output/*.mid' ) # 全ての出力メロディのリストを取得
    melody_filepaths.sort(reverse=True)
    melody_filepath = melody_filepaths[0]
    midi_data = pretty_midi.PrettyMIDI(melody_filepath)

    #　ノーマル
    for instrument in midi_data.instruments:
      for note in instrument.notes:
          start, end = int(note.start * MELODY_LENGTH), int(note.end * MELODY_LENGTH) # ループ内で見ているnoteの開始点と終了点を算出
          pianoroll[start:end, :] = np.zeros(NOTENUM_THRU - NOTENUM_FROM + 1,)
          while note.pitch - NOTENUM_FROM > pianoroll.shape[1]: # 高い音を出しすぎた場合はオク下げ
              note.pitch -= 12
          pianoroll[start:end, note.pitch-NOTENUM_FROM] = 1 # note.pitchのところのみ1とするone-hotベクトルを書き込む

    # 拡張パック　ダイアトニック音階への修正
    # for instrument in midi_data.instruments:
    # # TODO: ここでメロディパートなのか伴奏パートなのかを区別する必要がある
    #   for note in instrument.notes:
    #       start, end = int(note.start * MELODY_LENGTH), int(note.end * MELODY_LENGTH) # ループ内で見ているnoteの開始点と終了点を算出
    #       modified_pitch = postprocess_to_diatonic_melody(note)
    #       pianoroll[start:end, :] = np.zeros(NOTENUM_THRU - NOTENUM_FROM + 1,)
    #       while modified_pitch - NOTENUM_FROM > pianoroll.shape[1]: # 高い音を出しすぎた場合はオク下げ
    #           modified_pitch -= 12
    #       pianoroll[start:end, modified_pitch-NOTENUM_FROM] = 1
    
    show_and_play_midi(pianoroll, 12, basedir + "/" + backing_file, 
                   basedir + output_file)

if __name__ == "__main__":
    run()
