# simple magenta-docker

python with magenta without cpu

# introduce

docker-compose build --no-cache
docker-compose up -d

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

# VAE command()

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
