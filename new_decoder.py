import numpy as np
from sklearn.cross_decomposition import CCA
from scipy import signal


# 在循环外部生成用来匹配的信号，减少开销
def generate_frequency_signals(fs, segment_samples, freq_list):
    y = np.zeros((6, segment_samples, len(freq_list)))
    for i, frequency in enumerate(freq_list):
        y[0, :, i] = np.sin(np.arange(0, segment_samples) / fs * np.pi * 2 * frequency)
        y[1, :, i] = np.cos(np.arange(0, segment_samples) / fs * np.pi * 2 * frequency)
        y[2, :, i] = np.sin(np.arange(0, segment_samples) / fs * np.pi * 2 * frequency * 2)
        y[3, :, i] = np.cos(np.arange(0, segment_samples) / fs * np.pi * 2 * frequency * 2)
        y[4, :, i] = np.sin(np.arange(0, segment_samples) / fs * np.pi * 2 * frequency * 3)
        y[5, :, i] = np.cos(np.arange(0, segment_samples) / fs * np.pi * 2 * frequency * 3)
    return y


def cca_match(chunk, fs, Freq, correlation_threshold):
    b, a = signal.butter(3, [4, 40], 'bandpass', fs=fs)
    eeg = signal.filtfilt(b, a, chunk)
    r = np.zeros((5, 1))
    for k in range(len(Freq)):
        y = np.zeros((6, 250))
        y[0, :] = np.sin(np.arange(0, 250, 1) / 250 * np.pi * 2 * Freq[k])
        y[1, :] = np.cos(np.arange(0, 250, 1) / 250 * np.pi * 2 * Freq[k])
        y[2, :] = np.sin(np.arange(0, 250, 1) / 250 * np.pi * 2 * Freq[k] * 2)
        y[3, :] = np.cos(np.arange(0, 250, 1) / 250 * np.pi * 2 * Freq[k] * 2)
        y[4, :] = np.sin(np.arange(0, 250, 1) / 250 * np.pi * 2 * Freq[k] * 3)
        y[5, :] = np.cos(np.arange(0, 250, 1) / 250 * np.pi * 2 * Freq[k] * 3)
        cca = CCA(n_components=1)
        X_c, Y_c = cca.fit_transform(eeg.T, y.T)
        r[k] = np.corrcoef(X_c.T, Y_c.T)[0, 1]
    pred = np.argmax(r).item()
    print(r[pred])

    return Freq[pred]



