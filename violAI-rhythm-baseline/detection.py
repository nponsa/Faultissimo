import sys
import time
import numpy as np

from scipy import signal # Import scipy.signal for filtering
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import QTimer, Qt, QThread
from collections import deque

import music21
import sounddevice as sd
import librosa

from score_viewer import ScoreViewer
from graph_rhythm import GraphRhythm

# load score and return a section of a stream
def load_score(score_path):
    stream = None
    if score_path:
        try:
            stream = music21.converter.parse(score_path)
            excerpt = stream.measures(1, 2) # TODO: hardcoded!
            print(f"Successfully loaded score from: {score_path}")
        except Exception as e:
            print(f"Error loading score from {score_path}: {e}.")
    
    return excerpt

# extract data from the music21 stream 
# for each note -> start time (s), end time (s), frequency (Hz)
def analyze_music21_stream(stream_obj=None, default_bpm=60):
    """
    Analyzes a music21 stream to extract expected notes/frequencies and their timings.

    Args:
        score_path (str, optional): Path to a MIDI, MusicXML, or other supported score file.
        stream_obj (music21.stream.Stream, optional): A pre-loaded music21 Stream object.
        default_bpm (int): Default tempo in beats per minute if not found in the score.

    Returns:
        list: A list of dictionaries, where each dictionary represents a musical event
            with 'start_time_s', 'end_time_s', 'notes', and 'frequencies'.
            'notes' will be a list of note names (e.g., ['C4', 'E4']) or 'Rest'.
            'frequencies' will be a list of floats (Hz) or None for rests.
    """

    # If parsing failed or no stream provided, create a simple default stream
    if stream_obj is None:
        print("Creating a default simple music21 stream for demonstration.")
        s_default = music21.stream.Stream()
        s_default.insert(0, music21.clef.TrebleClef())
        s_default.insert(0, music21.key.Key('C'))
        s_default.insert(0, music21.meter.TimeSignature('4/4'))
        s_default.insert(0, music21.tempo.MetronomeMark(number=60)) # Set tempo to 60 BPM (1 beat/sec)

        s_default.append(music21.note.Note('C4', quarterLength=2)) # C4 for 2 beats
        s_default.append(music21.note.Note('D4', quarterLength=2)) # D4 for 2 beats
        s_default.append(music21.note.Rest(quarterLength=1)) # Rest for 1 beat
        s_default.append(music21.note.Note('E4', quarterLength=3)) # E4 for 3 beats
        s = s_default

    # Flatten the score to get all notes and rests in a single chronological stream
    # and apply all transformations (like clefs, key signatures, tempo marks)
    flat_score = stream_obj.flat.notesAndRests

    # Get the tempo. music21 can handle tempo changes, but for simplicity,
    # we'll find the first metronome mark or use the default.
    current_bpm = default_bpm
    found_tempo = False
    for m in stream_obj.recurse().getElementsByClass('MetronomeMark'):
        if m.referent is not None and m.referent.quarterLength != 0:
            # Use m.number directly for BPM as it represents the speed of the referent (e.g., quarter note)
            current_bpm = m.number
            found_tempo = True
            print(f"Found tempo: {current_bpm} BPM at offset {m.offset}")
            break # Use the first one found for simplicity

    if not found_tempo:
        print(f"No tempo found in score. Using default tempo: {default_bpm} BPM")

    # Calculate beats per second #TODO: might have to take into account time signature
    beats_per_second = current_bpm / 60.0
    if beats_per_second == 0:
        print("Warning: Beats per second is zero. Using 1 beat/sec.")
        beats_per_second = 1.0

    analysis_data = []
    # Iterate through all notes and rests in the flattened stream
    for element in flat_score:
        start_beat = element.offset
        duration_beats = element.duration.quarterLength # quarterLength is duration in beats

        start_time_s = start_beat / beats_per_second
        end_time_s = (start_beat + duration_beats) / beats_per_second

        notes_playing = []
        frequencies_playing = []

        if isinstance(element, music21.note.Note):
            notes_playing.append(element.nameWithOctave)
            frequencies_playing.append(element.pitch.frequency)
        elif isinstance(element, music21.chord.Chord):
            for n in element.notes:
                notes_playing.append(n.nameWithOctave)
                frequencies_playing.append(n.pitch.frequency)
        elif isinstance(element, music21.note.Rest):
            notes_playing.append("Rest")
            frequencies_playing = None # No frequency for a rest

        analysis_data.append({ #TODO: This should probably be a dictionary?
            'start_time_s': start_time_s,
            'end_time_s': end_time_s,
            'note': notes_playing,
            'frequency': frequencies_playing
        })

    return analysis_data

class PitchDetectThread(QThread):
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self._running = True

    def run(self):
        self.detector.pitch_detect_loop(self)

    def stop(self):
        self._running = False

class PitchDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.samplerate = 44100  # standard audio sample rate
        self.blocksize = 1024    # process audio in chunks of this many samples
        self.channels = 1        # mono audio
        self.analysis_window_size = 0.05 # seconds, smaller window for "real-time"
        self.buffer_size_samples = int(self.samplerate * 2) # 2 seconds of audio buffer for analysis
        self.audio_buffer = deque(maxlen=self.buffer_size_samples)
        
        self.thread = None # thread for listening
        
        self.score_path = 'Four_Seasons_Spring_I_Violin.mxl'
        self.score_stream = load_score(self.score_path)
        self.score_data = analyze_music21_stream(self.score_stream)
        self.pitches_played = []
        
        # GUI
        self.layout = QGridLayout()
        self.pitch_label = QLabel("Pitch: N/A", self)
        self.pitch_label.setAlignment(Qt.AlignCenter)
        self.time_label = QLabel("Time Elapsed: ", self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.score_label = ScoreViewer(self.score_stream)
        
        # buttons
        self.start_button = QPushButton("start")
        self.stop_button = QPushButton("stop")
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        
        self.layout.addWidget(self.pitch_label)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.score_label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.setLayout(self.layout)

        # bandpass filter for violin
        # violin frequency range: G3 (196 Hz) to E7 (2637 Hz)
        self.lowcut = 180.0  # Hz
        self.highcut = 3000.0 # Hz
        self.filter_order = 4 # Order of the Butterworth filter

        self.b, self.a = signal.butter(self.filter_order, [self.lowcut, self.highcut], btype='band', fs=self.samplerate)

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            blocksize=self.blocksize,
            callback=self.audio_callback
        )

        # update! 
        '''
        self.timer = QTimer()
        self.timer.setInterval(500)  # every 50 ms
        self.timer.timeout.connect(self.update_display)
        
        '''
        self.start_time = None
        
    def initUI(self):
        self.setWindowTitle('Real-time Violin Pitch Detector')
        self.setGeometry(100, 100, 400, 200)

    def audio_callback(self, indata, frames, time, status):
        """This function is called by sounddevice for each audio block."""
        if status:
            print(status)
        self.audio_buffer.extend(indata[:, 0]) # Assuming mono audio, take the first channel

    def pitch_detect_loop(self, thread):
        self.start_time = time.time()
        self.stream.start()
        try:
            while thread._running:
                required_samples = int(self.samplerate * self.analysis_window_size)
                if len(self.audio_buffer) < required_samples:
                    self.pitch_label.setText("Pitch: Listening...")
                    time.sleep(0.05)
                    continue

                audio_data_raw = np.array(list(self.audio_buffer)[-required_samples:], dtype=np.float32)

                try:
                    # apply bandpass filter
                    audio_data_filtered = signal.filtfilt(self.b, self.a, audio_data_raw)

                    f0 = librosa.yin(
                        y=audio_data_filtered, # Use the filtered audio here!
                        sr=self.samplerate,
                        fmin=self.lowcut,  # Constrain fmin to the filter's lowcut
                        fmax=self.highcut, # Constrain fmax to the filter's highcut
                        frame_length=2048,
                        hop_length=int(self.samplerate * 0.01)
                    )

                    valid_pitches = f0[~np.isnan(f0)]

                    if len(valid_pitches) > 0:
                        estimated_pitch = np.median(valid_pitches)
                        if estimated_pitch > (self.lowcut - 10):
                            note_name = librosa.hz_to_note(estimated_pitch)
                            elapsed = time.time() - self.start_time
                            self.time_label.setText(f"Time Elapsed: {round(elapsed, 2)}")
                            self.pitch_label.setText(f"Pitch: {note_name} ({estimated_pitch:.2f} Hz) | Expected: {self.get_expected_pitch(elapsed)}")
                            self.pitches_played.append({'note_name': note_name, 
                                                        'estimated_pitch': round(estimated_pitch, 2),
                                                        'time': round(elapsed, 2)})
                        else:
                            self.pitch_label.setText("Pitch: Too low/silent")
                    else:
                        self.pitch_label.setText("Pitch: No clear pitch detected")

                except Exception as e:
                    self.pitch_label.setText(f"Error: {e}")
                    print(f"Librosa pitch detection error: {e}")
                
                time.sleep(0.05) #updates checking intervals
        except KeyboardInterrupt:
            print("\nStopping...")
        finally: # maybe take out
            self.stream.stop()
            self.stream.close()

    # start pitch detection
    def start(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = PitchDetectThread(self)
            self.thread.start()
            print("Audio stream started. Listening for pitch...")

    # stop streama nd pitch detect thread
    def stop(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.stream.stop()
        self.stream.close()
        print("Audio stream stopped.")
        # Remove previous graph if needed
        if hasattr(self, 'rhythm_graph'):
            self.layout.removeWidget(self.rhythm_graph)
            self.rhythm_graph.deleteLater()
        self.rhythm_graph = GraphRhythm(self, score_data=self.score_data, pitches_played=self.pitches_played)
        self.layout.addWidget(self.rhythm_graph)
        self.repaint()
        
    def get_expected_pitch(self, curr_time): 
        expected_pitch = "None"
        if curr_time > self.score_data[-1]['end_time_s']:
            self.stop()
            return "DONE"
        for note in self.score_data: 
            if (note['start_time_s'] < curr_time) & (note['end_time_s'] > curr_time):
                expected_pitch = note['note']
        return expected_pitch
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    detector = PitchDetector()
    detector.show()
    sys.exit(app.exec_())