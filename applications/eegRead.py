from pylsl import StreamInlet, resolve_stream
import numpy as np
from scipy.signal import welch
from scipy.integrate import simpson
import time

# Define the bandpower function
def bandpower(data, sf, band, window_sec=None, relative=False):
    band = np.asarray(band)
    low, high = band

    if window_sec is not None:
        nperseg = window_sec * sf
    else:
        nperseg = (2 / low) * sf

    freqs, psd = welch(data, sf, nperseg=nperseg)
    freq_res = freqs[1] - freqs[0]       #Frequency resolution by simpson
    idx_band = np.logical_and(freqs >= low, freqs <= high)
    bp = simpson(psd[idx_band], dx=freq_res)

    if relative:
        bp /= simpson(psd, dx=freq_res)
    return bp

def normalize(value, min_value, max_value):
    """Normalize a value to a range [0, 1] based on min and max values."""
    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0

def eeg_data_thread(eeg_queue):
    print("Looking for an LSL stream...")
    streams = resolve_stream('name', 'BioAmpDataStream')
    if not streams:
        print("No LSL stream found!")
        return

    inlet = StreamInlet(streams[0])
    sampling_frequency = 250
    bands = {'Delta': [0.5, 4], 'Theta': [4, 8], 'Alpha': [8, 13], 'Beta': [13, 30], 'Gamma': [30, 40]}
    buffer_length = sampling_frequency * 4
    data_buffer = {'Channel1': [], 'Channel2': []}
    powerData1 = []
    powerData2 = []
    c = 0
    start_time = time.time()

    baseline1 = baseline2 = 1  # Initialize baselines
    min_power1 = min_power2 = 0
    max_power1 = max_power2 = 1

    while True:
        sample, timestamp = inlet.pull_sample()
        if len(sample) == 2:
            data_buffer['Channel1'].append(sample[0])
            data_buffer['Channel2'].append(sample[1])
            if len(data_buffer['Channel1']) > buffer_length:
                data_buffer['Channel1'].pop(0)
                data_buffer['Channel2'].pop(0)

            elapsed_time = time.time() - start_time
            if len(data_buffer['Channel1']) >= buffer_length:
                power_data = {'Channel1': {}, 'Channel2': {}}
                for band_name, band_freqs in bands.items():
                    power_data['Channel1'][band_name] = bandpower(np.array(data_buffer['Channel1']), sampling_frequency, band_freqs)
                    power_data['Channel2'][band_name] = bandpower(np.array(data_buffer['Channel2']), sampling_frequency, band_freqs)

                powerData1.append(power_data['Channel1']['Beta'] / power_data['Channel1']['Alpha'])
                powerData2.append(power_data['Channel2']['Beta'] / power_data['Channel2']['Alpha'])
                if elapsed_time >= 5:
                    if c != 1:
                        baseline1 = max(powerData1)
                        baseline2 = max(powerData2)
                        # min_power1 = min(powerData1)
                        # max_power1 = baseline1
                        # min_power2 = min(powerData2)
                        # max_power2 = baseline2
                        c = 1
                        data_time = elapsed_time
                        powerData1 = []
                        powerData2 = []
                    elif elapsed_time - data_time >= 0.25:
                        current_power1 = (max(powerData1)-baseline1)/baseline1
                        current_power2 = (max(powerData2)-baseline2)/baseline2
                        # normalized_power1 = normalize(current_power1, min_power1, max_power1)
                        # normalized_power2 = normalize(current_power2, min_power2, max_power2)
                        eeg_queue.put((current_power1, current_power2))
                        powerData1 = []
                        powerData2 = []
                        data_time = elapsed_time