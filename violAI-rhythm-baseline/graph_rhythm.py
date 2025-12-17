import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# source: https://www.pythonguis.com/tutorials/plotting-matplotlib/
class GraphRhythm(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, score_data=[], pitches_played=[]):
        super().__init__()
        fig = Figure(figsize=(width, height), dpi=100)
        self.axes = fig.add_subplot(111)
        
        self.score_data = score_data
        self.pitches_played = pitches_played
        
        self.player_times = []
        self.player_freqs = []
        
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Frequency (Hz)")
        
        self.plot_player_points()
        self.plot_score_points()
        
        super().__init__(fig)
    
    def plot_player_points(self):
        for point in self.pitches_played:
            self.player_times.append(point['time'])
            self.player_freqs.append(point['estimated_pitch'])
        self.axes.plot(self.player_times, self.player_freqs, 'o-', markersize=0.5)
            
    def plot_score_points(self):
        for point in self.score_data:
            try:
                start_time = point['start_time_s']
                end_time = point['end_time_s']
                freq = point['frequency'][0]
                
                self.axes.hlines(y=freq, xmin=start_time, xmax=end_time, colors='blue', lw=2)
            except Exception as e:
                print(f"Error plotting {point}: {e}")
            
        
    
    