import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.io as sio
import sys

import numpy as np
from PyQt5.QtWidgets import QCalendarWidget, QFontDialog, QColorDialog, QTextEdit, QFileDialog, \
    QCheckBox, QLabel, QComboBox, QPushButton, QGridLayout, QMainWindow, QWidget, QLineEdit, QMessageBox, QVBoxLayout, \
    QHBoxLayout, QAction
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
        # Open dialog window to select file path
        self.file_path = QFileDialog.getOpenFileName(None, "Open File", "/home", "Matlab Files (*.mat)")[0]
        if self.file_path != "":
            # Load .mat file from file path and store contents
            self.mat_contents = sio.loadmat(self.file_path)
            # Create a list of channel sets from .mat file contents
            self.ecog_SETS = list(self.mat_contents.keys())


class set:
    def __init__(self, set_select, height, File):
        self.numCol = len(File.ecog_SETS)
        for i in range(1, self.numCol):
            a = File.mat_contents.get(File.ecog_SETS[set_select])[:, i]
            index = (-height > a) | (a > height)
            for j in range(1, self.numCol):
                c = File.mat_contents.get(File.ecog_SETS[set_select])[:, j]
                c[index] = []


class channel:
    def __init__(self, ch_select, set_select, File):
        # Create an array of y values based on the chosen channel collection and individual channel
        self.y = File.mat_contents.get(File.ecog_SETS[set_select])[:, ch_select]
        # Create an array of x values based on the length of y values
        self.x = range(0, len(self.y))

    def gap(self, y_gap):
        self.y = self.y + y_gap


class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()
        self.setWindowTitle("Graphing Application")

    def initUI(self):
        centralwidget = QWidget()

        # create submenu option for later reference
        fileDiaglogue = QAction('&Open .mat file', self)

        # create instance of menu bar
        mainMenu = self.menuBar()
        # create menu option for opening file
        fileMenu = mainMenu.addMenu('&File')
        # add submenu option to tool bar
        fileMenu.addAction(fileDiaglogue)
        # connect openFile method to submenu selection
        fileDiaglogue.triggered.connect(self.openFile)

        # create dropdown menu gui
        self.dropLabel = QLabel('Channel Set', self)
        self.comboBox = QComboBox(self)
        self.comboBox.currentIndexChanged.connect(self.checkSet)
        self.comboBox.currentIndexChanged.connect(self.updateBtns)

        # create y-gap textbox
        self.yLabel = QLabel('Y Axis Gap', self)
        self.textbox = QLineEdit(self)

        # create graph all checkbox

        self.graphAll = QPushButton('Select All Channels', self)
        self.graphAll.clicked.connect(self.selectAll)

        # create update button
        update_btn = QPushButton('Update', self)
        update_btn.clicked.connect(self.update)

        # instantiate main plot canvas
        plot_canvas = FigureCanvas(Figure(figsize=(5, 5)))

        # add toolbar to layout
        self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(plot_canvas, self))

        self._static_ax = plot_canvas.figure.subplots()
        # label graph axes
        xtext = self._static_ax.set_xlabel('my xdata')  # returns a Text instance
        ytext = self._static_ax.set_ylabel('my ydata')

        # create grid for button layout
        self.grid = QGridLayout()
        # ensures no stretching occurs when maximizing/minimizing windows
        # self.grid.setSpacing(1)

        # assign grid position to each widget
        self.grid.addWidget(update_btn, 4, 0, 1, 5)
        self.grid.addWidget(self.yLabel, 1, 1)
        self.grid.addWidget(self.textbox, 1, 2)
        self.grid.addWidget(self.comboBox, 2, 2)
        self.grid.addWidget(self.dropLabel, 2, 1)
        self.grid.addWidget(self.graphAll, 3, 0, 1, 5)
        # create grid for channel button layout
        self.gridButtons = QGridLayout()
        self.gridButtons.setAlignment(Qt.AlignTop)

        # create layout for the graph canvas
        canvasBox = QHBoxLayout()
        canvasBox.addWidget(plot_canvas)

        # create main layout
        mainBox = QVBoxLayout()
        mainBox.addLayout(self.grid, 25)
        mainBox.addLayout(self.gridButtons, 75)
        mainBox.setAlignment(Qt.AlignHCenter)

        # create top layout
        topBox = QHBoxLayout()
        topBox.addLayout(canvasBox, 75)
        topBox.addLayout(mainBox, 25)

        centralwidget.setLayout(topBox)

        self.setCentralWidget(centralwidget)

        self.selected_SET = 0

    # method creates an instance of the File object and fills the dropdown menu with associated channel sets
    def openFile(self):
        self.file1 = File()
        # clear any pre-existing channel sets
        self.comboBox.clear()
        # check that a file has been chosen by the user
        if self.file1.file_path != "":
            # iterate through all sets and fill the dropdown with the name of each channel set
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
        # deletes any checkboxes from any previous set selection
        for i in reversed(range(self.gridButtons.count())):
            self.gridButtons.itemAt(i).widget().setParent(None)
        # determine the number of channels based on the number of y values in the selected set
        self.num_channels = len(self.file1.mat_contents.get(self.file1.ecog_SETS[self.selected_SET])[0, :])
        # create a array of checkboxes for later reference
        self.box_array = list()
        self.list_array = list()
        # determine the maximum number of rows based on the numbe
        # r of channels
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
            self.gridButtons.addWidget(self.list_array[i - 1], i + 2, 1)

            for j in range(1, columns + 1):
                self.box_array.append(QCheckBox(self))
                self.gridButtons.addWidget(self.box_array[numB], i + 2, j + 1)
                numB += 1
        self.channels_array = list()
        for i in range(0, self.num_channels):
            self.channels_array.append(channel(i, self.selected_SET, self.file1))

    def selectAll(self):
        # if user checks the "graph all" checkbox, append all channels to be graphed
        for b in range(0, len(self.box_array)):
            self.box_array[b].setCheckState(Qt.Checked)

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
            QMessageBox.about(self, "Error", "Please enter a y-gap value.")
        else:

            for j in range(0, len(self.channels_selected)):
                self.channels_array[self.channels_selected[j]].gap(float(y_gap) * j)
                self._static_ax.plot(self.channels_array[self.channels_selected[j]].x,
                                     self.channels_array[self.channels_selected[j]].y)

        self._static_ax.figure.canvas.draw()

    def update(self):
        # check if an instance of the File() object has been created
        try:
            self.test = self.file1
        # if no File() object exists instruct the user to select a file
        except:
            QMessageBox.about(self, "Error", "Please load a .mat file.")
        # call checkBtn() and updatePlot() method if file exists.
        else:
            self.checkBtns()
            self.updatePlot()


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()