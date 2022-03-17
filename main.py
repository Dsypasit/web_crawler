########################################################################
## CONVERT .UI & .QRC
# pyrcc5 resources.qrc -o resource_rc.py
# pyuic5 -x football.ui -o football_interface.py 
########################################################################

########################################################################
## IMPORTS
########################################################################
import os
import sys
import re
import webbrowser
from CrawlerManager import CrawlerManager
from model import PandasTableModel
from Worker import Worker
########################################################################
# IMPORT GUI FILE
from football_interface import *
from PyQt5.QtWidgets import QFileDialog, QListWidget, QTableWidgetItem, QApplication, QMainWindow, qApp, QListWidgetItem
from PyQt5.QtCore import Qt, QThreadPool
########################################################################

########################################################################
## MAIN WINDOW CLASS
########################################################################
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.crawler_manager = CrawlerManager()

        self.threadpool = QThreadPool()
        #######################################################################
        # ADD FUNCTION ELEMENT
        #######################################################################
        self.ui.pushButton.clicked.connect(self.search)
        self.ui.pushButton2.clicked.connect(self.refreshLink)
        self.ui.tableWidget.doubleClicked.connect(self.open_link)
        #######################################################################
        # SHOW WINDOW
        #######################################################################
        self.show()
        #######################################################################

    ########################################################################
    ## FUNCTION
    ########################################################################
    def get_n_gram_data(self, progress_callback):
        self.data = self.crawler_manager.get_n_gram_data(self.ui.lineEdit.text(), progress=progress_callback)
        return self.data
    
    def show_table(self, df):
        self.model = PandasTableModel(df)
        self.ui.tableWidget.setModel(self.model)
        self.ui.tableWidget.setColumnWidth(0, 500)
    
    def progress_fn(self, v):
        self.ui.progress_bar.setValue(v)

    def search(self):
        # self.crawler_manager.get_all_links()
        worker = Worker(self.get_n_gram_data)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.result.connect(self.show_table)
        worker.signals.finished.connect(self.ui.progress_bar.reset)

        self.threadpool.start(worker)

    def refreshLink(self):
        worker = Worker(lambda progress_callback: self.crawler_manager.get_all_links(progress=progress_callback))
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.finished.connect(self.ui.progress_bar.reset)

        self.threadpool.start(worker)
    
    def open_link(self, item):
        for index in self.ui.tableWidget.selectionModel().selectedIndexes():
            value = str(self.data.iloc[index.row()][index.column()])
            webbrowser.open(value)
            return

    ########################################################################

########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ########################################################################
    ##
    ########################################################################
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################
