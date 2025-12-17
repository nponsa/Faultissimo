import sys
import os

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog, QComboBox, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread

from music21 import converter, midi, tempo, note, meter
import verovio
import cairosvg
from music21.musicxml.m21ToXml import GeneralObjectExporter

import sounddevice as sd
import scipy.io.wavfile as wav
import time
import librosa

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MusicThread(QThread):

    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    def run(self):
        self.stream.play()

# source: https://www.pythonguis.com/tutorials/plotting-matplotlib/
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        
class ScoreViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.fname = ""
        self.chunck_size = 4 # number of measures
        self.bp_measure = 4 # (default) top number of time signature
        self.tempo = 120 # (default)
        
        #GUI
        self.setWindowTitle("Music21 + Verovio Score Viewer")
        self.resize(900, 400)
        layout = QGridLayout()
        self.label = QLabel("Load a .mxl file to display the first 4 measures.")
        self.label.setScaledContents(True)
        
        #buttons
        self.open_file_button = QPushButton("Open MXL File")
        self.open_file_button.clicked.connect(self.open_file)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_rhythm) # todo change back to play_music
        self.play_rhythm_button = QPushButton("Play Rhythm")
        self.play_rhythm_button.clicked.connect(self.play_rhythm)
        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.record_audio)
        
        self.speed_option = QComboBox()
        self.speed_option.addItems(["Quarter Speed", "Half Speed", "Normal Speed"])
        self.speed_option.currentIndexChanged.connect(self.update_speed)
        
        # plot for errors
        self.graph = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.graph, 6, 0)
        
        layout.addWidget(self.open_file_button, 0, 0)
        layout.addWidget(self.label, 1, 0)
        layout.addWidget(self.play_button, 3, 0)
        layout.addWidget(self.play_rhythm_button, 4, 0)
        layout.addWidget(self.record_button, 5, 0)
        layout.addWidget(self.speed_option, 3, 1)
        
        self.setLayout(layout)
        
    def plot_rhythm(self, user_rhythm_ts): 
        actual_rhythm_ts = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 4.5]

        self.graph.axes.plot(actual_rhythm_ts, [0] * len(actual_rhythm_ts), 'ko', markersize=10, label='Actual') # The [0] * len(actual_rhythm_ts) puts all the points on the same y axis
        self.graph.axes.plot(user_rhythm_ts, [0] * len(user_rhythm_ts), 'ro', markersize=15, label='Your Rhythm', alpha=0.4)

        self.graph.axes.set_xlim(0, 5)  # x-axis limit
        self.graph.axes.set_yticks([])  # removing y-ticks
        self.graph.axes.set_xlabel("Time (s)")
        self.graph.axes.set_title("Rhythm Analysis")
        self.graph.axes.legend()
        self.graph.draw()

        # graph.tight_layout() # maybe take out?
        
    def get_measures(self):
        if self.fname != "":
            section = 1 # TODO: change to make dynamic later on
            self.score = converter.parse(self.fname)
            excerpt = self.score.measures(section, section + self.chunck_size - 1)
            #self.bp_measure = self.score.measure(1).getElementsByClass(meter.TimeSignature)[0].numerator #todo: debug index error
            #self.tempo = self.score.measusre(1).getElementsByClass(tempo.MetronomeMark)[0].number # just take the first tempo...
            #print(f"Tempo: {self.tempo} BPM, Time Signature: {self.bp_measure}/4")
            return excerpt
        else:
            self.label.setText("Please load a file first.")
            return None

    # open file and display the first 4 measures with verovio
    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open MXL File", "", "MXL Files (*.mxl)")
        if fname:
            self.fname = fname
            try:
                excerpt = self.get_measures()
                
                vrv_toolkit = verovio.toolkit()
                exporter = GeneralObjectExporter()
                xml_data = exporter.parse(excerpt).decode("utf-8")
                vrv_toolkit.loadData(xml_data)
                vrv_toolkit.setOptions({"scale": 40, "adjustPageHeight": True})
                svg_data = vrv_toolkit.renderToSVG(1)
                
                svg_filepath = "temp_excerpt.svg"
                with open(svg_filepath, "w") as f:
                    f.write(svg_data)
                png_filepath = "temp_excerpt.png"
                cairosvg.svg2png(url=svg_filepath, write_to=png_filepath)
                pixmap = QPixmap(png_filepath)
                self.label.setPixmap(pixmap)
            except Exception as e:
                self.label.setText(f"Error: {e}")
                
    # using librosa to get beat times 
    def analyze_rhythm(self, filename): 
        y, sr = librosa.load(filename)
        librosa_tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr) # get beat events as timestamps

        return beat_times
        
    def update_speed(self, index):
        
        if index == 0:
            self.tempo = 30 # TODO: make this not hardcoded later
            print("1/4 speed")
        elif index == 1:
            self.tempo = 60
            print("1/2 speed")
        elif index == 2:
            self.tempo = 120
            print("normal speed")
        else:
            self.tempo = 120
                
    def play_music(self):
        excerpt = self.get_measures()
        if excerpt is None:
            return
        self.sp = midi.realtime.StreamPlayer(excerpt)
        self.music_thread = MusicThread(self.sp)
        self.music_thread.start()
        
    def play_rhythm(self):
        excerpt = self.get_measures()
        if excerpt is None:
            return
        excerpt_rhythm = self.get_rhythm(excerpt)
    
        self.sp = midi.realtime.StreamPlayer(excerpt_rhythm)
        self.music_thread = MusicThread(self.sp)
        self.music_thread.start()
    
    def get_rhythm(self, excerpt):
        excerpt_rhythm = excerpt 
        for note in excerpt_rhythm.recurse().notes:
            note.pitch.name = 'C'
            note.pitch.octave = 4
        
        return excerpt_rhythm
    
    #toDO: this method is incomplete! 
    def analyze_excerpt(self):
        excerpt = self.get_measures()
        if excerpt is None:
            return
        excerpt.write('midi', fp='excerpt.mid')
        # Convert MIDI to WAV externally, or use a pre-existing WAV
        wav_path = 'excerpt.wav'
        if not os.path.exists(wav_path):
            self.label.setText("Please convert excerpt.mid to excerpt.wav first.")
            return
        self.analyze_with_librosa(wav_path)
    
    # record user's attempt, analyze with librosa, and output visualization
    def record_audio(self, duration, filename="output.wav", fs=44100):
        duration = 3 # in seconds #TODO: change to the duration of the piece 
        filename = "output.wav"
        
        try:
            print(f"Recording audio for {duration} seconds...")
            # Start the recording
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)  # channels=1 for mono
            sd.wait()  # Wait until the recording is finished
            print("Finished recording.")

            # Save the recording as a .wav file
            print(f"Saving audio to {filename}...")
            wav.write(filename, fs, recording)
            print("Audio saved successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None  # Explicitly return None on error
        
        beat_times = self.analyze_rhythm(filename)
        self.plot_rhythm(beat_times)
        print(beat_times)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ScoreViewer()
    viewer.show()
    sys.exit(app.exec_())