"""
UI for 2D FDTD N-slit simulator. Uses Qt5 and matplotlib to generate the plots.
Time stepping is done with matplotlib timers.

Charles Tam 2019
"""
import sys
import fdtd

from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QSlider, QLabel, QInputDialog, QLineEdit, QCheckBox
from matplotlib.backends.qt_compat import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # initialise variables
        self.sim_time = 0
        self.play = False
        self.anim_int = 500
        self.no = 1
        self.width = 10
        self.space = 11
        self.freq = fdtd.freq
        self.interp = "gaussian"
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        dynamic_canvas = FigureCanvasQTAgg(Figure(figsize=(10, 10)))
        
        # play/pause button
        self.playbutton = QPushButton("Start")
        self.playbutton.clicked.connect(self._playpause)
        
        # reset button
        self.resetbutton = QPushButton("Reset")
        self.resetbutton.clicked.connect(self._reset)
        
        # slider for number of slits
        self.slideno = QSlider(QtCore.Qt.Horizontal)
        self.slideno.setMinimum(1)
        self.slideno.setMaximum(3)
        self.slideno.setValue(self.no)
        self.slideno.setTickPosition(QSlider.TicksBelow)
        self.slideno.setTickInterval(1)
        self.labelno = QLabel("Number of Slits: %d" % self.no)
        self.slideno.valueChanged.connect(self._changeno)
        self.labelno.setAlignment(QtCore.Qt.AlignCenter)
        
        # slider for slit width
        self.slidewidth = QSlider(QtCore.Qt.Horizontal)
        self.slidewidth.setMinimum(1)
        self.slidewidth.setMaximum(10)
        self.slidewidth.setValue(self.width)
        self.slidewidth.setTickPosition(QSlider.TicksBelow)
        self.slidewidth.setTickInterval(1)
        self.labelwidth = QLabel("Slit Width: %d" % self.width)
        self.slidewidth.valueChanged.connect(self._changewidth)
        self.labelwidth.setAlignment(QtCore.Qt.AlignCenter)
        
        # slider for slit spacing (more multiple slits)
        self.slidespace = QSlider(QtCore.Qt.Horizontal)
        self.slidespace.setMinimum(1)
        self.slidespace.setMaximum(20)
        self.slidespace.setValue(self.space)
        self.slidespace.setTickPosition(QSlider.TicksBelow)
        self.slidespace.setTickInterval(1)
        self.labelspace = QLabel("Slit Spacing: %d" % self.space)
        self.slidespace.valueChanged.connect(self._changespace)
        self.labelspace.setAlignment(QtCore.Qt.AlignCenter)
        
        
        # slider for wave frequency
        self.slidefreq = QSlider(QtCore.Qt.Horizontal)
        self.slidefreq.setMinimum(1)
        self.slidefreq.setMaximum(10)
        self.slidefreq.setValue(self.freq * 10)
        self.slidefreq.setTickPosition(QSlider.TicksBelow)
        self.slidefreq.setTickInterval(1)
        self.labelfreq = QLabel("Wave Frequency: {}".format(self.freq))
        self.slidefreq.valueChanged.connect(self._changefreq)
        self.labelfreq.setAlignment(QtCore.Qt.AlignCenter)
    
        # slider for animation interval
        self.slideint = QSlider(QtCore.Qt.Horizontal)
        self.slideint.setMinimum(1)
        self.slideint.setMaximum(10)
        self.slideint.setValue(self.anim_int/100)
        self.slideint.setTickPosition(QSlider.TicksBelow)
        self.slideint.setTickInterval(1)
        self.labelint = QLabel("Animation Interval: %d ms" % self.anim_int)
        self.slideint.valueChanged.connect(self._changeint)
        self.labelint.setAlignment(QtCore.Qt.AlignCenter)
        
        # checkbox for interpolation
        self.intcheck = QCheckBox("Plot Smoothing")
        self.intcheck.setChecked(True)
        self.intcheck.stateChanged.connect(self._toggleint)
        
        # make layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(self.slideno)
        vbox.addWidget(self.labelno)
        vbox.addStretch()
        vbox.addWidget(self.slidewidth)
        vbox.addWidget(self.labelwidth)
        vbox.addStretch()
        vbox.addWidget(self.slidespace)
        vbox.addWidget(self.labelspace)
        vbox.addStretch()
        vbox.addWidget(self.slidefreq)
        vbox.addWidget(self.labelfreq)
        vbox.addStretch()
        vbox.addWidget(self.slideint)
        vbox.addWidget(self.labelint)
        vbox.addStretch()
        vbox.addWidget(self.intcheck)
        vbox.addStretch()
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.playbutton)
        hbox1.addWidget(self.resetbutton)
        vbox.addLayout(hbox1)
        hbox2 = QtWidgets.QHBoxLayout()        
        hbox2.addLayout(vbox, 1)
        hbox2.addWidget(dynamic_canvas, 5)
        self._main.setLayout(hbox2)
        self._main.show()
        
        self.setWindowTitle("N Slit FDTD")
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer()
        self._timer.interval = self.anim_int
        self._timer.add_callback(self._update_canvas)
        
    def _update_canvas(self):
        self._dynamic_ax.clear()
        data = fdtd.update(self.sim_time)
        self._dynamic_ax.imshow(data, origin="lower", interpolation=self.interp)
        self._dynamic_ax.figure.canvas.draw()
        self.sim_time += 1
        
    def _playpause(self):
        if not self.play:
            self.playbutton.setText("Pause")
            self.play = True
            self._timer.start()
        elif self.play:
            self.playbutton.setText("Resume")
            self.play = False
            self._timer.stop()
        
    def _reset(self):
        fdtd.reset()
    
    def _changeno(self):
        self.no = self.slideno.value()
        self.labelno.setText("Number of Slits: %d" % self.no)
        fdtd.updateslit(self.no, self.width, self.space)
    
    def _changewidth(self):
        self.width = self.slidewidth.value()
        self.labelwidth.setText("Slit Width: %d" % self.width)
        fdtd.updateslit(self.no, self.width, self.space)
    
    def _changespace(self):
        self.space = self.slidespace.value()
        self.labelspace.setText("Slit Spacing: %d" % self.space)
        fdtd.updateslit(self.no, self.width, self.space)
    
    def _changefreq(self):
        self.freq = self.slidefreq.value() / 10
        self.labelfreq.setText("Wave Frequency: {}".format(self.freq))
        fdtd.updatefreq(self.freq)
    
    def _changeint(self):
        self.anim_int =  100 * self.slideint.value()
        self.labelint.setText("Animation interval: %d ms" % self.anim_int)
        self._timer.interval = self.anim_int
        
    def _toggleint(self, state):
        if state == QtCore.Qt.Checked:
            self.interp = "gaussian"
        else:
            self.interp = "none"
     
if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()
