

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap

from music21.musicxml.m21ToXml import GeneralObjectExporter
from music21 import converter
import verovio
import cairosvg


class ScoreViewer(QLabel):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.chunk_size = 4
        
        self.setText("Test")
        self.open_file(stream)
    
    # open file and display the first 4 measures with verovio
    def open_file(self, stream):
        try:
            
            vrv_toolkit = verovio.toolkit()
            exporter = GeneralObjectExporter()
            xml_data = exporter.parse(stream).decode("utf-8")
            vrv_toolkit.loadData(xml_data)
            vrv_toolkit.setOptions({"scale": 40, "adjustPageHeight": True})
            if vrv_toolkit.getPageCount() < 1:
                raise ValueError("no pages to render")
            svg_data = vrv_toolkit.renderToSVG(1)
            
            svg_filepath = "temp_excerpt.svg"
            with open(svg_filepath, "w") as f:
                f.write(svg_data)
            png_filepath = "temp_excerpt.png"
            cairosvg.svg2png(url=svg_filepath, write_to=png_filepath)
            pixmap = QPixmap(png_filepath)
            self.setPixmap(pixmap)
        except Exception as e:
            self.setText(f"Error: {e}")
            
    