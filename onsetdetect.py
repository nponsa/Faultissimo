import librosa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def hz_to_midi_safe(hz):
    return 69 + 12 * np.log2(hz / 440.0) if hz > 0 else None

def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    # === Librosa onset ===
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    onset_times_librosa = librosa.frames_to_time(onset_frames, sr=sr) 

    # === f0 detection ===
    f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C3'),
                            fmax=librosa.note_to_hz('C7'), sr=sr)
    times = librosa.times_like(f0, sr=sr)

    # === RMS ===
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    frame_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    # === Energy onset by RMS diff ===
    rms_diff = np.append(np.diff(rms), 0)
    threshold = np.percentile(rms_diff[rms_diff > 0], 84)
    energy_onset_indices = np.where(rms_diff > threshold)[0]
    energy_onset_times = frame_times[energy_onset_indices]

    # === Pitch onset ===
    f0_filled = []
    midi_filled = []
    for pitch in f0:
        if pitch is None or pitch < 350:
            f0_filled.append(0)
            midi_filled.append(None)
        else:
            f0_filled.append(pitch)
            midi_filled.append(hz_to_midi_safe(pitch))

    pitch_onset_times = []
    pitch_diff_threshold_midi = 0.5
    time_window = 0.1
    min_interval = 0.15
    last_onset_time = -np.inf

    for i, (t_i, m_i) in enumerate(zip(times, midi_filled)):
        if m_i is None or t_i - last_onset_time < min_interval:
            continue
        for j in range(i - 1, -1, -1):
            if times[j] < t_i - time_window:
                break
            m_j = midi_filled[j]
            if m_j is None:
                continue
            if abs(m_i - m_j) > pitch_diff_threshold_midi:
                pitch_onset_times.append(t_i)
                last_onset_time = t_i
                break

    # === Combine onsets ===
    combined_onsets = np.concatenate([onset_times_librosa, energy_onset_times, pitch_onset_times])
    combined_onsets = np.sort(combined_onsets)

    # === Filter by RMS threshold and variation ===
    min_rms_threshold = 0.0001
    min_rms_variation = 0.05
    valid_onsets = set(pitch_onset_times)

    for t in combined_onsets:
        if any(abs(t - p) < 0.01 for p in pitch_onset_times):
            continue
        idx = np.argmin(np.abs(frame_times - t))
        if idx >= len(rms) or rms[idx] < min_rms_threshold:
            continue
        mask = (frame_times >= t) & (frame_times <= t + 0.2)
        if np.sum(mask) < 2:
            continue
        segment = rms[mask]
        if np.max(segment) - np.min(segment) < min_rms_variation:
            continue
        valid_onsets.add(t)

    combined_onsets = np.array(sorted(valid_onsets))

    # === Remove duplicate (green / purple onset classification) ===
    final_green_onsets = []
    purple_onsets = []
    onset_window = 0.15
    all_custom_onsets = sorted(set(np.round(pitch_onset_times, 3)) |
                               set(np.round(energy_onset_times, 3)))

    for t in all_custom_onsets:
        if any(abs(t - prev_t) < onset_window for prev_t in final_green_onsets + purple_onsets):
            purple_onsets.append(t)
        else:
            final_green_onsets.append(t)

    # 再次過濾 green onset（pitch onset 優先）
    green_onsets = []
    for t in final_green_onsets + purple_onsets:
        if len(green_onsets) == 0 or t - green_onsets[-1] > 0.1 or \
           any(abs(t - p) < 0.01 for p in pitch_onset_times):
            green_onsets.append(t)

    # === note_end ===
    note_segments = []
    for i, onset in enumerate(green_onsets):
        next_onset = green_onsets[i + 1] if i + 1 < len(green_onsets) else duration
        frame_mask = (frame_times >= onset) & (frame_times <= next_onset)
        end_time = next_onset  # next onset
        for t, r in zip(frame_times[frame_mask], rms[frame_mask]):
            if r < 0.01:
                end_time = t
                break
        note_segments.append((onset, end_time))

    return times, frame_times, green_onsets, note_segments


if __name__ == '__main__':
    file_path = '203SuzukimethodVol2Bourrée.m4a'
    times, frame_times, green_onsets, note_segments = analyze_audio(file_path)

