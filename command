# RNN command sample

https://github.com/magenta/magenta/tree/main/magenta/models/melody_rnn

melody_rnn_generate \
--config=basic \
--bundle_file=/data/ckpt/basic_rnn.mag \
--output_dir=/data/output \
--num_outputs=1 \
--num_steps=128 \
--primer_melody="[60]"

https://github.com/magenta/magenta/tree/main/magenta/models/drums_rnn

drums_rnn_generate \
--config=one_drum \
--bundle_file=/data/mags/drum_kit_rnn.mag \
--output_dir=/data/output \
--num_outputs=1 \
--num_steps=128 \
--qpm=120.0 \
--primer_drums=“[(36,)]”

# VAE command(sample/)

https://github.com/magenta/magenta/tree/main/magenta/models/music_vae

music_vae_generate \
--config=hierdec-trio_16bar \
--checkpoint_file=/data/ckpt/hierdec-trio_16bar.tar \
--mode=sample \
--num_outputs=5 \
--output_dir=/data/output

music_vae_generate \
--config=hierdec-trio_16bar \
--checkpoint_file=/data/ckpt/hierdec-trio_16bar.tar \
--mode=interpolate \
--input_midi_1=/data/input/001.mid \
--input_midi_2=/data/input/002.mid \
--num_outputs=5 \
--output_dir=/data/output

# improv_rnn

improv_rnn_generate \
--config=chord-pitches_improv \
--bundle_file=/data/ckpt/chord_pitches_improv.mag \
--output_dir=/data/output \
--num_outputs=1 \
--qpm=120 \
--primer_melody="[60]" \
--backing_chords="C G Am F C G Am F" \
--render_chords

improv_rnn_generate \
--config=chord_pitches_improv \
--bundle_file=/data/ckpt/chord_pitches_improv.mag \
--output_dir=/data/output \
--num_outputs=5 \
--primer_midi=/data/input/primer.mid \
--backing_chords="C G Am F C G Am F" \
--render_chords

## その他

polyphony_rnn_generate \
--bundle_file=/data/ckpt/polyphony_rnn.mag \
--output_dir=/data/output \
--num_outputs=3 \
--num_steps=128 \
--primer_pitches="[67,64,60]" \
--condition_on_primer=true \
--inject_primer_during_generation=false

pianoroll_rnn_nade_generate \
--bundle_file=/data/ckpt/pianoroll_rnn_nade-bach.mag \
--output_dir=/data/output \
--num_outputs=3 \
--num_steps=128 \
--primer_pitches="[67,64,60]"

performance_rnn_generate \
--config=pitch_conditioned_performance_with_dynamics \
--bundle_file=/data/ckpt/pitch_conditioned_performance_with_dynamics.mag \
--output_dir=/data/output \
--num_outputs=3 \
--num_steps=9000 \
--notes_per_second=16 \
--pitch_class_histogram="[5,0,1,1,4,0,1,3,0,2,1,1]"
