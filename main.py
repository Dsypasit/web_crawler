from web_ui import Ui_App
from domain_ui import DomainFilter
from model import PandasTableModel

from KeywordManager import KeywordManager

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
import sys
import webbrowser
from Worker import Worker
from PyQt5.QtCore import QThreadPool

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_App()
        self.ui.setupUi(self)
        self.keyword_manager = KeywordManager()
        self.current_domains = {}
        self.threadpool = QThreadPool()

        self.updateKeywords()
        self.keywordsTabale()

        self.ui.SearchList.itemDoubleClicked.connect(self.selectKeywordsThread)
        self.ui.base_table.doubleClicked.connect(self.openLink)
        self.ui.pushButton.clicked.connect(self.filterDomainPopup)
        self.ui.searchButton.clicked.connect(self.searchKeywordsThread)

    def updateKeywords(self):
        self.keywords = self.keyword_manager.get_all_keywords()
        self.ui.SearchList.clear()
        self.ui.SearchList.addItems(self.keywords)
    
    def showTable(self):
        self.model = PandasTableModel(self.data)
        self.ui.base_table.setModel(self.model)
        self.ui.base_table.setColumnWidth(0, 200)
        self.ui.base_table.setColumnWidth(1, 200)
    
    def searchKeyword(self, progress_callback=None):
        progress_callback.emit(0)
        keyword = self.ui.Search_LineEdit.text()
        if keyword == "":
            return
        self.keyword = keyword
        self.data = self.keyword_manager.search_keyword(self.keyword, progress_callback)
        self.showTable()
        self.ui.base_label.setText(self.keyword)
        progress_callback.emit(90)
        self.ui.status_base_label.setText(f"{len(self.data.index)} links")
        domains_list = self.keyword_manager.get_domain(self.keyword)
        self.current_domains = {name: False for name in domains_list}
        self.ui.base_label.setText(self.keyword)
        progress_callback.emit(100)
        self.updateKeywords()
        self.keywordsTabale()
        self.ui.Search_LineEdit.clear()
    
    def progress_update(self, v):
        self.ui.progress_bar.setValue(v)
    
    def searchKeywordsThread(self):
        worker = Worker(self.searchKeyword)
        worker.signals.progress.connect(self.progress_update)
        worker.signals.finished.connect(self.ui.progress_bar.reset)

        self.threadpool.start(worker)

    def selectKeywordsThread(self, item):
        worker = Worker(self.selectKeywordsData, item)
        worker.signals.progress.connect(self.progress_update)
        worker.signals.finished.connect(self.ui.progress_bar.reset)

        self.threadpool.start(worker)
        
    def selectKeywordsData(self, item, progress_callback=None):
        progress_callback.emit(0)
        self.keyword = item.text()
        self.data = self.keyword_manager.search_keyword(self.keyword, progress_callback)
        self.showTable()
        self.ui.base_label.setText(self.keyword)
        progress_callback.emit(90)
        self.ui.status_base_label.setText(f"{len(self.data.index)} links")
        domains_list = self.keyword_manager.get_domain(self.keyword)
        self.current_domains = {name: False for name in domains_list}
        self.ui.base_label.setText(self.keyword)
        progress_callback.emit(100)
   
    def openLink(self, item):
        for index in self.ui.base_table.selectionModel().selectedIndexes():
            value = str(self.data.iloc[index.row()][index.column()])
            if value.startswith("https://") or value.startswith("http://"):
                webbrowser.open(value)
                return
    
    def filterDomainPopup(self):
        print(self.current_domains)
        filter_dialog = DomainFilter(self)
        filter_dialog.show()
    
    def filterDomain(self):
        domains = [domain for domain in self.current_domains.keys() if self.current_domains[domain]]
        self.data = self.keyword_manager.filter_domain(self.keyword, *domains)
        self.showTable()

    def keywordsTabale(self):
        self.keywords_data = self.keyword_manager.keywords_information()
        self.keywords_model = PandasTableModel(self.keywords_data)
        self.ui.keywordView.setModel(self.keywords_model)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())