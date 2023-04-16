import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QFileDialog, QLineEdit, QMessageBox,QComboBox
from PyQt5.QtGui import QIcon, QPalette, QColor,QBrush,QPixmap,QCursor
from PyQt5.QtCore import Qt
from fitting_functions import *
import interpolation_functions
import os.path as path
import pandas as pd


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        MainWindow.least_squares=least_squares
        MainWindow.fit_gaussian=fit_gaussian
        MainWindow.fit_lorentzian=fit_lorentzian
        MainWindow.fit_voigt=fit_voigt
        MainWindow.def1=interpolation_functions.def1
        MainWindow.newton1=interpolation_functions.newton1
        MainWindow.newton2=interpolation_functions.newton2
        # Set window properties
        self.setWindowTitle("Fitting")
        self.setStyleSheet("*{font-size:16px;}QPushButton:disabled{background-color:grey;}QLineEdit:disabled{background-color:lightgrey}")

        self.setWindowIcon(QIcon("./assets/icon.png"))
        # Load the background image
        # background_image = QPixmap("./assets/background.jpg")
        # # Create a palette for the QMainWindow
        # palette = QPalette()
        # palette.setBrush(QPalette.Background, QBrush(background_image))
        # self.setPalette(palette)

        self.setGeometry(100, 100, 800, 600)

        # Create central widget and grid layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.grid_layout = QGridLayout(central_widget)

        # Create labels and line edits for file input
        file_label = QLabel("Choose JSON or CSV File:")
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        file_button = QPushButton("Browse")
        file_button.clicked.connect(self.browse_file)
        file_button.setCursor(QCursor(Qt.PointingHandCursor))

        # Create labels and line edits for plot input
        title_label = QLabel("Graph title:")
        self.title_edit = QLineEdit()
        xlabel_label = QLabel("X Label:")
        self.xlabel_edit = QLineEdit()
        ylabel_label = QLabel("Y Label:")
        self.ylabel_edit = QLineEdit()
        fitting_method_label=QLabel("Fitting method:")
        self.fitting_method_edit=QComboBox()
        self.fitting_method_edit.addItems(["Least squares","Gaussian(normal) distribution","Lorentzian distribution","Voigt distribution"])
        self.fitting_method_edit.currentIndexChanged.connect(self.remove_interpolation)
        experiment_label=QLabel("Experiment:")
        self.experiment_edit=QComboBox()
        self.experiment_edit.addItems(["","Simple pendulum","Hooke's law"])

        # Create buttons for plot and interpolation
        plot_button = QPushButton("Plot")
        plot_button.clicked.connect(self.plot)
        plot_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.interp_button = QPushButton("Interpolate")
        self.interp_button.clicked.connect(self.interpolate)
        self.interp_button.setCursor(QCursor(Qt.PointingHandCursor))
        # Create label for interpolation input
        self.interp_label = QLabel("Interpolation Value:")
        self.interp_edit = QLineEdit()

        # Create label for results
        self.result_label = QLabel()

        # Create figure canvas for plot output
        self.canvas = FigureCanvas(plt.Figure())

        # Add widgets to grid layout
        self.grid_layout.addWidget(file_label, 0, 0)
        self.grid_layout.addWidget(self.file_edit, 0, 1, 1, 3)
        self.grid_layout.addWidget(file_button, 0, 4)
        self.grid_layout.addWidget(title_label, 1, 0)
        self.grid_layout.addWidget(self.title_edit, 1, 1, 1, 3)
        self.grid_layout.addWidget(xlabel_label, 2, 0)
        self.grid_layout.addWidget(self.xlabel_edit, 2, 1)
        self.grid_layout.addWidget(ylabel_label, 2, 2)
        self.grid_layout.addWidget(self.ylabel_edit, 2, 3)
        self.grid_layout.addWidget(fitting_method_label, 3, 0)
        self.grid_layout.addWidget(self.fitting_method_edit, 3, 1)
        self.grid_layout.addWidget(experiment_label, 3, 2)
        self.grid_layout.addWidget(self.experiment_edit, 3, 3)
        self.grid_layout.addWidget(plot_button, 4, 0)
        self.grid_layout.addWidget(self.interp_button, 4, 1)
        self.grid_layout.addWidget(self.interp_label, 4, 2)
        self.grid_layout.addWidget(self.interp_edit, 4, 3)
        self.grid_layout.addWidget(self.result_label, 6, 0, 1, 5,Qt.AlignCenter)

    def browse_file(self):
        # Open file dialog and get selected file path
        file_path,_= QFileDialog.getOpenFileName(self, "Open JSON or CSV File", "./data_sets", "JSON or CSV Files (*.json  *.csv)")
        if file_path:
            file_ext = path.splitext(file_path)[1]
            # Read  file and set default input values
            if(file_ext==".csv"):
                file= pd.read_csv(file_path)
            elif(file_ext==".json"):
                file= pd.read_json(file_path)

            try:
                title=file['title'][0]
                self.title_edit.setText(title)
                for i in range(self.experiment_edit.count()):
                    if(self.experiment_edit.itemText(i)==title):
                        self.experiment_edit.setCurrentIndex(i)
            except KeyError:
                self.title_edit.setText("")
                self.experiment_edit.setCurrentIndex(0)
            
            try:
                xlabel=file['xlabel'][0]
                self.xlabel_edit.setText(xlabel)
            except KeyError:
                self.xlabel_edit.setText("")
            
            try:
                ylabel=file['ylabel'][0]
                self.ylabel_edit.setText(ylabel)
            except KeyError:
                self.ylabel_edit.setText("")


            try:
                self.x = file['x']
                self.y = file['y']
            except KeyError as error:
                self.title_edit.setText("")
                self.experiment_edit.setCurrentIndex(0)
                self.xlabel_edit.setText("")
                self.ylabel_edit.setText("")
                QMessageBox.warning(self, "Data error", f"Please provide a valid {error} column name in the chosen file .")
                return

            self.n = len(self.x)
            self.file_edit.setText(file_path)

    def shared_plot(self,interp_value=None):
        # Get input values
        filename = self.file_edit.text()
        xlabel = self.xlabel_edit.text()
        ylabel = self.ylabel_edit.text()
        title = self.title_edit.text()
        self.setWindowTitle(title)


        # Check if all input values are provided
        if not all([filename, xlabel, ylabel, title]):
            QMessageBox.warning(self, "Error", "Please provide all input values.")
            return
        experiment=self.select_fitting_method()
        self.result = f"{self.add_experiment_result()}"
        

        # Clear previous plot and draw new plot on canvas
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.scatter(experiment.x, experiment.y,label="Before fitting")
        ax.plot(experiment.x_smooth, experiment.y_fit,'r-',label=experiment.after_fitting_label)
        # Clear previous result label and write new text in it
        self.result_label.setText("")
        self.result_label.setStyleSheet("background:transparent;")
        # Plot cut part point
        if(self.fitting_method_edit.currentText()=="Least squares"):
            ax.plot(0, experiment.c, "h m")
            ax.text(0, experiment.c, f"Cut point")
            self.result_label.setStyleSheet("background:darkgreen;color:white;padding:5px 50px;font-size:16px;")
            self.result_label.setText(self.result)
        ax.legend(loc="best")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()
        if(interp_value != None):
            # Zoom in to show the interpolated/extrapolated point
            if interp_value >= min(experiment.x) and interp_value < (max(experiment.x)-3):
                ax.set_xlim(0, max(experiment.x))
                ax.set_ylim(0, max(experiment.y_fit))
            elif(interp_value < 0):
                ax.set_xlim(interp_value-5, round(max(experiment.x)*1.6))

            # Plot interpolated/extrapolated point
            ax.plot(interp_value, experiment.newton2(interp_value), "s y")

            # Determine if interpolated/extrapolated point is within plot range
            if interp_value <= max(experiment.x) and interp_value >= min(experiment.x):
                interpolation_text=f"The interpolated point is ({interp_value},{round(experiment.newton2(interp_value),3)})"
                ax.text(interp_value, experiment.newton2(interp_value), f"Interpolation point")
            else:
                interpolation_text=f"The extrapolated point is ({interp_value},{round(experiment.newton2(interp_value),3)})"
                ax.text(interp_value, experiment.newton2(interp_value), f"Extrapolation point")
            self.result = f"{self.result}\n{interpolation_text}"

        self.grid_layout.addWidget(self.canvas, 5, 0, 1, 5)
        self.canvas.draw()

    def plot(self):
        self.shared_plot()

    # plot with interpolation
    def interpolate(self):
        interp_value = self.interp_edit.text()
        try:
            interp_value = float(interp_value)
        except ValueError:
            QMessageBox.warning(self, "Error", "Please provide a valid interpolation value.")
            return
        self.shared_plot(interp_value)

    def remove_interpolation(self):
        if(self.fitting_method_edit.currentText()=="Least squares"):
            self.interp_button.setEnabled(True)
            self.interp_edit.setEnabled(True)
        else:
            self.interp_button.setEnabled(False)
            self.interp_edit.setEnabled(False)


    def select_fitting_method(self):
        current_method = self.fitting_method_edit.currentText()

        if current_method == "Least squares":
            self.least_squares()    
            self.after_fitting_label="Least squares fit"     
        elif current_method == "Gaussian(normal) distribution":
            self.fit_gaussian()
            self.after_fitting_label="Gaussian fit"     
        elif current_method == "Lorentzian distribution":
            self.fit_lorentzian()
            self.after_fitting_label="Lorentzian fit"     
        elif current_method == "Voigt distribution":
            self.fit_voigt()
            self.after_fitting_label="Voigt fit"     

        return self
    
    def add_experiment_result(self):
        current_experiment=self.experiment_edit.currentText()
        result=""
        if(self.fitting_method_edit.currentText()=="Least squares"):
            if(current_experiment=="Simple pendulum"):
                g = 4*(np.pi**2)/self.m
                result=f"Slope = {self.m} s2/cm\nCut part = {self.c:.5f} s2\nEarth gravitational acceleration = {g} cm/s2"
            elif(current_experiment=="Hooke's law"):
                result=f"Slope = {self.m} s2/gm\nCut part = {self.c:.5f} cm"
            else:
                result=f"Slope = {self.m}\nCut part = {self.c:.5f}"
        return result

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style to light mode
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(0,150,0))
    palette.setColor(QPalette.ButtonText, QColor("white"))
    palette.setColor(QPalette.BrightText, Qt.black)
    palette.setColor(QPalette.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.Highlight, QColor("green"))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    window = MainWindow()
    combo_palette = QPalette()
    combo_palette.setColor(QPalette.Button, QColor(240,240,240))
    combo_palette.setColor(QPalette.ButtonText, QColor("black"))
    combo_palette.setColor(QPalette.Highlight, QColor(0,255,0,100))
    window.fitting_method_edit.setPalette(combo_palette)
    window.experiment_edit.setPalette(combo_palette)
    window.show()
    sys.exit(app.exec_())