#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QFileDialog, QLineEdit, QMessageBox,QComboBox,QSlider,QScrollArea
from PyQt5.QtGui import QIcon, QPalette, QColor,QCursor
from PyQt5.QtCore import Qt
from fitting_functions import *
import interpolation_functions
import os.path as path
import pandas as pd


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_dir=path.dirname(__file__)

        MainWindow.linear_fit=linear_fit
        MainWindow.gaussian_fit=gaussian_fit
        MainWindow.lorentzian_fit=lorentzian_fit
        MainWindow.voigt_fit=voigt_fit
        MainWindow.def1=interpolation_functions.def1
        MainWindow.newton1=interpolation_functions.newton1
        MainWindow.newton2=interpolation_functions.newton2

        # Set window properties
        self.setWindowTitle("Fitting")
        self.setStyleSheet("""
        *{
            font-size:20px;
            font-family:arial;
        }
        QPushButton:disabled{
            background-color:grey;
        }
        QLineEdit:disabled{
            background-color:lightgrey
        }
        QMainWindow{
            background:rgb(245,245,245);
        }
        QPushButton::hover{
            background:green;
        }
        QPushButton,QLineEdit,QComboBox{
            padding:5px 10px;
        }
        """)
        self.font_size=16

        self.setWindowIcon(QIcon(path.join(self.app_dir,'assets','icon.png')))
        self.setGeometry(100, 100, 800, 720)

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
        title_label = QLabel("Graph Title:")
        self.title_edit = QLineEdit()
        xlabel_label = QLabel("X Label:")
        self.xlabel_edit = QLineEdit()
        ylabel_label = QLabel("Y Label:")
        self.ylabel_edit = QLineEdit()

        fitting_method_label=QLabel("Fitting Method:")
        self.fitting_method_edit=QComboBox()
        self.fitting_method_edit.addItems(["Linear","Gaussian","Lorentzian","Voigt"])
        self.fitting_method_edit.currentIndexChanged.connect(self.disable_enable_interpolation)
        experiment_label=QLabel("Preset:")
        self.experiment_edit=QComboBox()
        self.experiment_edit.addItems(["","Simple pendulum","Hooke's law"])

        # will be used if we used custom fitting functions instead of the models
        self.start_end_xsmooth_edit = QLineEdit()
        self.start_end_xsmooth_edit.setPlaceholderText('Start,End,X_Smooth')
        self.amplitude_edit = QLineEdit()
        self.amplitude_edit.setPlaceholderText('Amplitude')
        self.center_edit = QLineEdit()
        self.center_edit.setPlaceholderText('Center')
        self.sigma_edit = QLineEdit()
        self.sigma_edit.setPlaceholderText('Sigma')

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
        # When pressing enter button
        self.interp_edit.returnPressed.connect(self.interp_button.click)

        # Create slider for graph zoom
        self.slider=QSlider(Qt.Horizontal)
        self.slider.setRange(0,1000)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.graph_draw_zoom)

        # Create figure canvas for plot output
        self.toolbar=None
        self.canvas = FigureCanvas(plt.Figure())

        # Create label for results
        self.result_label = QLabel()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.result_label)

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

        # will be used if we used custom fitting functions instead of the models
        self.grid_layout.addWidget(self.start_end_xsmooth_edit,4,0)
        self.grid_layout.addWidget(self.amplitude_edit,4,1)
        self.grid_layout.addWidget(self.center_edit,4,2)
        self.grid_layout.addWidget(self.sigma_edit,4,3)
        self.start_end_xsmooth_edit.setEnabled(False)
        self.amplitude_edit.setEnabled(False)
        self.center_edit.setEnabled(False)
        self.sigma_edit.setEnabled(False)

        self.grid_layout.addWidget(plot_button, 5, 0)
        self.grid_layout.addWidget(self.interp_button, 5, 1)
        self.grid_layout.addWidget(self.interp_label, 5, 2)
        self.grid_layout.addWidget(self.interp_edit, 5, 3)

        self.grid_layout.addWidget(self.scroll_area, 9, 0, 1, 5)


    def browse_file(self):
        # Open file dialog and get selected file path
        file_path,_= QFileDialog.getOpenFileName(self, "Open JSON or CSV File", path.join(self.app_dir,'data_sets'), "JSON or CSV Files (*.json  *.csv)")

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
                self.experiment_edit.setCurrentIndex(0)
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
                indexes = list(range(len(self.x)))
                indexes.sort(key=self.x.__getitem__)
                self.x=np.array(list(map(self.x.__getitem__,indexes)))
                self.y=np.array(list(map(self.y.__getitem__,indexes)))
                # those value values to restore x and y when errors happens
                self.x_temp=self.x
                self.y_temp=self.y
            except KeyError as error:
                self.title_edit.setText("")
                self.experiment_edit.setCurrentIndex(0)
                self.xlabel_edit.setText("")
                self.ylabel_edit.setText("")
                QMessageBox.warning(self, "Data error", f"Please provide a valid {error} column name in the chosen file .")
                return

            self.n = len(self.x)
            self.file_edit.setText(file_path)


    def shared_plot(self):
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
        self.x=self.x_temp
        self.y=self.y_temp
        
        # Clear previous plot and draw new plot on canvas
        self.canvas.figure.clear()
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.tick_params(axis='both', which='major', labelsize=self.font_size-4)
        self.ax.plot(experiment.x, experiment.y,'ro',markersize=5,label="Before fitting")
        self.ax.plot(experiment.x_smooth, experiment.y_fit,'b',label=experiment.after_fitting_label)

        # Plot cut part point
        if(self.fitting_method_edit.currentText()=="Linear"):
            self.ax.plot(0, experiment.c, "h m")
            self.ax.text(0, experiment.c, f"Cut point (0,{experiment.c:.3f})")
            self.result_label.setText(self.result)
            self.result_label.setStyleSheet("background:darkgreen;color:white;padding:5px 50px;")
        else:
            self.result_label.setText(self.peak_result)
            self.result_label.setStyleSheet("background:darkgreen;color:white;padding:5px;")

        self.min_x=min(*experiment.x,*experiment.x_smooth)
        self.max_x=max(*experiment.x,*experiment.x_smooth)
        self.min_y=min(*experiment.y,*experiment.y_fit)
        self.max_y=max(*experiment.y,*experiment.y_fit)

        self.ax.legend(loc="best")
        self.ax.set_xlabel(xlabel,fontsize=self.font_size)
        self.ax.set_ylabel(ylabel,fontsize=self.font_size)
        self.ax.set_title(title,fontsize=self.font_size)
        self.ax.grid()


    def plot(self):
        self.shared_plot()
        self.graph_draw_zoom()


    # plot with interpolation
    def interpolate(self):
        interp_value = self.interp_edit.text()
        try:
            interp_value = float(interp_value)
        except ValueError:
            QMessageBox.warning(self, "Error", "Please provide a valid interpolation value.")
            return
        self.shared_plot()
        
        experiment=self
        y_interp= experiment.newton1(interp_value)
        # Plot interpolated/extrapolated point
        self.ax.plot(interp_value, y_interp, "s y")

        # Determine if interpolated/extrapolated point is within plot range
        interp_point=f"({interp_value},{y_interp:.3f})"
        if min(experiment.x) <=interp_value <= max(experiment.x):
            interpolation_text=f"The interpolated point is {interp_point}"
            self.ax.text(interp_value, y_interp, f"Interpolation point {interp_point}")
        else:
            interpolation_text=f"The extrapolated point is {interp_point}"
            self.ax.text(interp_value, y_interp, f"Extrapolation point {interp_point}")
        self.result = f"{self.result}\n{interpolation_text}"
        self.result_label.setText(self.result)

        self.graph_draw_zoom()


    def disable_enable_interpolation(self):
        if(self.fitting_method_edit.currentText()=="Linear"):
            self.interp_button.setEnabled(True)
            self.interp_edit.setEnabled(True)
            self.start_end_xsmooth_edit.setEnabled(False)
            self.amplitude_edit.setEnabled(False)
            self.center_edit.setEnabled(False)
            self.sigma_edit.setEnabled(False)
        else:
            self.interp_button.setEnabled(False)
            self.interp_edit.setEnabled(False)
            self.start_end_xsmooth_edit.setEnabled(True)
            self.amplitude_edit.setEnabled(True)
            self.center_edit.setEnabled(True)
            self.sigma_edit.setEnabled(True)



    def select_fitting_method(self):
        current_method = self.fitting_method_edit.currentText()

        if current_method == "Linear":
            self.linear_fit()    
            self.after_fitting_label="Linear fitting"
            self.grid_layout.removeWidget(self.scroll_area)
            self.grid_layout.addWidget(self.canvas, 8, 0, 1, 5)
            self.grid_layout.addWidget(self.scroll_area, 9, 0, 1, 5)
        else:
            self.grid_layout.removeWidget(self.scroll_area)
            self.grid_layout.addWidget(self.canvas, 8, 0, 2, 3)
            self.grid_layout.addWidget(self.scroll_area, 8, 3, 2, 2)
            if current_method == "Gaussian":
                self.gaussian_fit()
            elif current_method == "Lorentzian":
                self.lorentzian_fit()
            elif current_method == "Voigt":
                self.voigt_fit()
            self.after_fitting_label="Peak fitting" 

        return self


    def add_experiment_result(self):
        current_experiment=self.experiment_edit.currentText()
        result=""
        if(self.fitting_method_edit.currentText()=="Linear"):
            if(current_experiment=="Simple pendulum"):
                g = 4*(np.pi**2)/self.m
                result=f"Slope = {self.m} s2/cm\nCut part = {self.c:.3f} s2\nEarth gravitational acceleration = {g} cm/s2"
            elif(current_experiment=="Hooke's law"):
                result=f"Slope = {self.m} s2/gm\nCut part = {self.c:.3f} cm"
            else:
                result=f"Slope = {self.m}\nCut part = {self.c:.3f}"
        return result


    def graph_draw_zoom(self):
        lim_percentage=self.slider.value()/100
        self.ax.set_xlim(self.min_x-(self.max_x-self.min_x)*lim_percentage, self.max_x+(self.max_x-self.min_x)*lim_percentage)
        self.ax.set_ylim(self.min_y-(self.max_y-self.min_y)*lim_percentage, self.max_y+(self.max_y-self.min_y)*lim_percentage)
        
        self.grid_layout.removeWidget(self.slider)
        self.grid_layout.addWidget(self.slider, 6, 0, 1, 5)
        if(self.toolbar==None):
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.toolbar.locLabel.setStyleSheet("color:initial")
            self.grid_layout.addWidget(self.toolbar, 7, 0, 1, 5)
        self.canvas.draw()



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