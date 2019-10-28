import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.io as sio
import sys


import numpy as np
from PyQt5.QtWidgets import QCalendarWidget, QFontDialog, QColorDialog, QTextEdit, QFileDialog, \
    QCheckBox, QLabel,QComboBox,QPushButton, QGridLayout, QMainWindow, QWidget, QLineEdit, QMessageBox
from PyQt5.QtCore import QCoreApplication, Qt


from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure




#################GAGE 12/26/18#####################

class File:
    def __init__(self):
        #Open dialog window to select file path
        self.file_path = QFileDialog.getOpenFileName(None, "Open File", "/home", "Matlab Files (*.mat)")[0]
        if self.file_path != "":
            #Load .mat file from file path and store contents
            self.mat_contents = sio.loadmat(self.file_path)
            #Create a list of channel sets from .mat file contents
            self.ecog_SETS = list(self.mat_contents.keys())

class channel:
    def __init__(self, ch_select, set_select, File):
        #Create an array of y values based on the chosen channel collection and individual channel
        self.y = File.mat_contents.get(File.ecog_SETS[set_select])[:,ch_select]
        #Create an array of x values based on the length of y values
        self.x = range(0,len(self.y))
    def plot(self):
        plt.plot (self.x,self.y)
    def gap(self,y_gap):
        self.y = self.y + y_gap

class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()
        self.setWindowTitle("Graphing Application")

    def initUI(self):
        centralwidget = QWidget()


        # create file button
        file_btn = QPushButton('File', self)
        file_btn.clicked.connect(self.openFile)

        # create dropdown menu gui
        self.DropDown = QLabel('Channel Set', self)
        self.comboBox = QComboBox(self)
        self.comboBox.currentIndexChanged.connect(self.checkSet)
        self.comboBox.currentIndexChanged.connect(self.updateBtns)

        # create y-gap textbox
        self.textbox = QLineEdit(self)

        # create update button
        update_btn = QPushButton('Update', self)
        update_btn.clicked.connect(self.update)

        # instantiate main plot canvas
        plot_canvas = FigureCanvas(Figure(figsize=(5, 5)))

        # add toolbar to layout
        self.addToolBar(NavigationToolbar(plot_canvas, self))

        self._static_ax = plot_canvas.figure.subplots()
        # label graph axes
        xtext = self._static_ax.set_xlabel('my xdata')  # returns a Text instance
        ytext = self._static_ax.set_ylabel('my ydata')

        #create grid for button layout
        self.grid = QGridLayout()
        # ensures no stretching occurs when maximizing/minimizing windows
        self.grid.setSpacing(1)

        # assign grid position to each widget
        self.grid.addWidget(update_btn, 0, 1)
        self.grid.addWidget(file_btn, 0, 2)
        self.grid.addWidget(plot_canvas, 0, 0)
        self.grid.addWidget(self.textbox, 0, 3)
        self.grid.addWidget(self.comboBox, 2, 1)
        self.grid.addWidget(self.DropDown, 1, 1)


        centralwidget.setLayout(self.grid)

        self.setCentralWidget(centralwidget)

        self.selected_SET = 0

    # method creates an instance of the File object and fills the dropdown menu with associated channel sets
    def openFile(self):
        self.file1 = File()
        # clear any pre-existing channel sets
        self.comboBox.clear()
        # check that a file has been chosen by the user
        if self.file1.file_path != "":
            #iterate through all sets and fill the dropdown with the name of each channel set
            for s in range(3, len(self.file1.ecog_SETS)):
                self.comboBox.addItem(self.file1.ecog_SETS[s])

    # method checks what channel set is currently selected and gets its index
    def checkSet(self):
        # iterate through all channel sets until it matches the currently selected channel set
        for s in range(3, len(self.file1.ecog_SETS)):
            if self.comboBox.currentText() == self.file1.ecog_SETS[s]:
                self.selected_SET = s

    # method creates buttons based on the number channels in the selected set
    def updateBtns(self):
        # determine the numbet of channels based on the number of y values in the selected set
        self.num_channels = len(self.file1.mat_contents.get(self.file1.ecog_SETS[self.selected_SET])[0, :])
        # create a array of checkboxes for later reference
        self.box_array = list()
        self.list_array = list()
        # determine the maximum number of rows based on the number of channels
        max_rows = np.ceil(self.num_channels / 10)
        numB = 0
        # for each row, determine if the row will be complete
        for i in range(1, max_rows.astype(int) + 1):
            if self.num_channels - i * 10 > 0:
                columns = 10
            else:
                columns = self.num_channels % 10

            # create a label for each row indicating the number of each button
            self.list_array.append(QLabel())
            self.list_array[i - 1].setText(str((i - 1) * 10) + '-' + str(((i - 1) * 10) + columns))
            self.grid.addWidget(self.list_array[i - 1], i + 2, 1)

            for j in range(1, columns + 1):
                self.box_array.append(QCheckBox(self))
                self.grid.addWidget(self.box_array[numB], i+2, j+1)
                numB += 1
        self.channels_array = list()
        for i in range(0, self.num_channels):
            self.channels_array.append(channel(i, self.selected_SET, self.file1))
    def checkBtns(self):
        # reinstantiate selected channels
        self.channels_selected = []
        # check which buttons and selected and add the respective channel to an array
        for b in range(0, len(self.box_array)):
            if self.box_array[b].checkState() == Qt.Checked:
                self.channels_selected.append(b)
    def updatePlot(self):
        # clear the axes before graphing selected channels
        self._static_ax.clear()
        # intantiate y_gap value for later use using the current textbox value
        y_gap = self.textbox.text()

        # check that user has entered a y gap value
        if y_gap == "":
            QMessageBox.about(self,"Error", "Please enter a y-gap value.")
        else:

            for j in range(0, len(self.channels_selected)):
                self.channels_array[self.channels_selected[j]].gap(float(y_gap) * j)
                self._static_ax.plot(self.channels_array[self.channels_selected[j]].x, self.channels_array[self.channels_selected[j]].y)

        self._static_ax.figure.canvas.draw()

    def update(self):
        self.checkBtns()
        self.updatePlot()

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()
