import librosa as lb
import numpy as np
import matplotlib.pyplot as plt
import librosa.display
import sys


print("----------",sys.argv[1])

filename = sys.argv[1].replace(".wav","")

n_fft = 800
hop_length = 128
n_mels = 128

audio, sampling_rate = lb.load(sys.argv[1], sr=16000, mono=True)
#mel_spectro = lb.feature.melspectrogram(audio, sampling_rate, n_fft=512, hop_length=64, n_mels = 256)
mel_spectro = lb.feature.melspectrogram(audio, sampling_rate, n_fft=n_fft, hop_length=hop_length, n_mels = n_mels)
mel_spectro_dB = lb.power_to_db(mel_spectro, ref=np.max)

librosa.display.specshow(mel_spectro_dB, x_axis='time',  y_axis='mel', sr=sampling_rate)
plt.savefig(filename+'-n_fft_'+str(n_fft)+'-hop_length_'+str(hop_length)+'-n_mels_'+str(n_mels)+'.png', format='png', dpi=1200, transparent=True)
