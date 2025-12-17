import sys, time
import numpy as np
import sounddevice as sd
import librosa
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QThread
from scipy import signal
import music21

from score_viewer import ScoreViewer
from graph_rhythm import GraphRhythm

# === 樂譜與節奏資料分析 ===
def load_score(score_path):
    try:
        stream = music21.converter.parse(score_path)
        excerpt = stream.measures(1, 4)
        print(f"✅ Successfully loaded score from: {score_path}")
        return excerpt
    except Exception as e:
        print(f"❌ Error loading score: {e}")
        return None

def analyze_music21_stream(stream_obj, default_bpm=60):
    flat_score = stream_obj.flatten().notesAndRests
    bpm = default_bpm
    for m in stream_obj.recurse().getElementsByClass('MetronomeMark'):
        bpm = m.number
        break
    bps = bpm / 60.0
    result = []
    for elem in flat_score:
        start = elem.offset / bps
        end = (elem.offset + elem.quarterLength) / bps
        if isinstance(elem, music21.note.Note):
            result.append({'start_time_s': start, 'end_time_s': end,
                           'note': [elem.nameWithOctave], 'frequency': [elem.pitch.frequency]})
        elif isinstance(elem, music21.note.Rest):
            result.append({'start_time_s': start, 'end_time_s': end,
                           'note': ['Rest'], 'frequency': None})
    return result

# === 音高偵測背景執行緒 ===
class PitchDetectThread(QThread):
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self._running = True

    def run(self):
        self.detector.pitch_detect_loop(self)

    def stop(self):
        self._running = False

# === 主介面應用 ===
class PitchDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎻 Real-time Pitch Detection with Score")
        self.resize(400, 200)

        self.score_path = 'The_Happy_Farmer.mxl'
        self.score_stream = load_score(self.score_path)
        self.score_data = analyze_music21_stream(self.score_stream)

        # UI Layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.pitch_label = QLabel("Pitch: N/A")
        self.time_label = QLabel("Time Elapsed: 0.0s")
        self.score_label = ScoreViewer(self.score_stream)
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        self.layout.addWidget(self.pitch_label)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.score_label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)

        # Audio config
        self.samplerate = 44100
        self.blocksize = 1024
        self.audio_buffer = deque(maxlen=int(self.samplerate * 2))
        self.analysis_window_size = 0.05
        self.lowcut = 180.0
        self.highcut = 3000.0
        self.b, self.a = signal.butter(4, [self.lowcut, self.highcut], btype='band', fs=self.samplerate)
        self.stream = sd.InputStream(samplerate=self.samplerate, channels=1, callback=self.audio_callback)

        self.pitches_played = []
        self.thread = None
        self.start_time = None

        # Timeline figure (overlay with moving line + pitch trace)
        self.fig_overlay, self.ax_overlay = plt.subplots(figsize=(12, 4))
        self.ax_overlay.set_ylim(50, 100)
        self.ax_overlay.set_xlim(0, 10)
        self.ax_overlay.set_xlabel("Time (s)")
        self.ax_overlay.set_ylabel("MIDI Pitch")
        self.ax_overlay.set_title("🎼 Real-time Pitch Timeline")
        self.time_line = self.ax_overlay.axvline(0, color='red')
        self.detected_dots, = self.ax_overlay.plot([], [], 'bo', markersize=4)

        # === 加入樂譜背景軌道圖 ===
        from music21 import converter, note, chord

        score = converter.parse("The_Happy_Farmer.mxl")
        violin_part = score.parts[0]
        first_measures = violin_part.measures(1, 4)

        notes_data = []
        for elem in first_measures.flat.notes:
            if isinstance(elem, note.Note):
                notes_data.append((elem.offset, elem.pitch.midi, elem.quarterLength))
            elif isinstance(elem, chord.Chord):
                for p in elem.pitches:
                    notes_data.append((elem.offset, p.midi, elem.quarterLength))

        space_ratio = 0.95
        adjusted_notes_data = [(start, pitch, duration * space_ratio)
                            for start, pitch, duration in notes_data]

        # 畫在 ax_overlay 上（也就是 timeline 軸）
        for start, pitch, duration in adjusted_notes_data:
            self.ax_overlay.broken_barh([(start, duration)], (pitch - 0.4, 0.8), facecolors='lightgray')


        self.timeline_times = []
        self.timeline_pitches = []
        self.anim = animation.FuncAnimation(self.fig_overlay, self.update_timeline, interval=50, blit=False)
        plt.tight_layout()
        plt.show(block=False)

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print("⚠️ Audio status:", status)
        self.audio_buffer.extend(indata[:, 0])

    def pitch_detect_loop(self, thread):
        self.start_time = time.time()
        self.stream.start()
        try:
            while thread._running:
                if len(self.audio_buffer) < int(self.samplerate * self.analysis_window_size):
                    continue
                raw_audio = np.array(list(self.audio_buffer)[-int(self.samplerate * self.analysis_window_size):])
                filtered = signal.filtfilt(self.b, self.a, raw_audio)

                f0 = librosa.yin(filtered, sr=self.samplerate,
                                 fmin=self.lowcut, fmax=self.highcut,
                                 frame_length=2048, hop_length=int(self.samplerate * 0.01))
                f0_valid = f0[~np.isnan(f0)]
                if len(f0_valid) > 0:
                    pitch_hz = np.median(f0_valid)
                    pitch_midi = 69 + 12 * np.log2(pitch_hz / 440.0)
                    note_name = librosa.hz_to_note(pitch_hz)
                    t = round(time.time() - self.start_time, 2)

                    self.pitch_label.setText(f"Pitch: {note_name} ({pitch_hz:.2f} Hz)")
                    self.time_label.setText(f"Time Elapsed: {t:.2f}s")
                    self.pitches_played.append({'note': note_name, 'pitch': pitch_hz, 'time': t})

                    self.timeline_times.append(t)
                    self.timeline_pitches.append(pitch_midi)
        except Exception as e:
            print(f"❌ Error in pitch detection loop: {e}")
        finally:
            self.stream.stop()

    def update_timeline(self, frame):
        if not self.timeline_times:
            return
        now = time.time() - self.start_time if self.start_time else 0
        self.time_line.set_xdata(now)
        self.detected_dots.set_data(self.timeline_times, self.timeline_pitches)
        if now > 10:
            self.ax_overlay.set_xlim(now - 10, now + 2)

    def start(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = PitchDetectThread(self)
            self.thread.start()
            print("🎙️ Audio started...")

    def stop(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.stream.stop()
        print("🛑 Audio stopped.")
        if hasattr(self, 'rhythm_graph'):
            self.layout.removeWidget(self.rhythm_graph)
            self.rhythm_graph.deleteLater()
        self.rhythm_graph = GraphRhythm(self, score_data=self.score_data, pitches_played=self.pitches_played)
        self.layout.addWidget(self.rhythm_graph)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    detector = PitchDetector()
    detector.show()
    sys.exit(app.exec_())