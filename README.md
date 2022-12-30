# simple magenta-docker

python with magenta without cpu

# introduce

docker-compose build --no-cache
docker-compose up -d

# VAE command

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
