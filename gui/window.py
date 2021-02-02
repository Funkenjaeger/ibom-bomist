import io
import json
import typing
import pandas as pd
from PySide6.QtGui import QPainter, QBrush, QColor, QFont
from PySide6.QtWidgets import QMainWindow, QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QFile, QAbstractItemModel, QModelIndex, QObject
from .table import PandasTableModel, CustomSortFilterProxyModel, FilterHeader
from .project_tree import TreeModel, TreeItem
from pcb.genericjson import GenericJsonPcbData


class Window(QMainWindow):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        loader = QUiLoader()
        file = QFile("lxinventory.ui")
        if file.open(QFile.ReadOnly):
            self.window = loader.load(file, parent)
            file.close()
            self.setCentralWidget(self.window)

        self.setWindowTitle("ibom-bomist")

        filename = "C:\\Users\\evand\\AppData\\Local\\Temp\\Neutron\\ElectronFileOutput\\16472\\brd-7c8bb298-c890-43ee-bc9b-bf307df76318\\MZMFC v8.json"
        self.pcbdata = GenericJsonPcbData(filename)
        self.df = pd.DataFrame(columns=['ref', 'footprint', 'val', 'mpn', 'source'])
        self.model = PandasTableModel(self.df)
        filter_model = CustomSortFilterProxyModel()
        filter_model.setSourceModel(self.model)
        self.table_view = self.window.tableView

        """header = FilterHeader(self.table_view)
        self.table_view.setHorizontalHeader(header)
        header.show()
        header.setFilterBoxes(model.columnCount())
        header.filterActivated.connect(filter_model.setFilterStrings) # self.handleFilterActivated)
        header.setMinimumSectionSize(80)"""

        self.table_view.setModel(self.model)
        # self.table_view.setModel(filter_model)
        self.table_view.verticalHeader().hide()
        self.table_view.horizontalHeader().show()
        self.resize(1024, 768)
        self.table_view.resizeColumnsToContents()

        # self.window.treeView.setItemDelegate(RowColorDelegate())

    def setdata(self, data):
        self.df = pd.DataFrame(data, columns=['ref', 'footprint', 'val', 'mpn', 'source'])
        self.model = PandasTableModel(self.df)
        filter_model = CustomSortFilterProxyModel()
        filter_model.setSourceModel(self.model)
        self.table_view = self.window.tableView

        """header = FilterHeader(self.table_view)
        self.table_view.setHorizontalHeader(header)
        header.show()
        header.setFilterBoxes(self.model.columnCount())
        header.filterActivated.connect(filter_model.setFilterStrings) # self.handleFilterActivated)
        header.setMinimumSectionSize(80)"""

        self.table_view.setModel(self.model)
        # self.table_view.setModel(filter_model)
        self.table_view.verticalHeader().hide()
        self.table_view.horizontalHeader().show()
        self.resize(1024, 768)
        self.table_view.resizeColumnsToContents()

    def settree(self, treemodel):
        self.window.treeView.setModel(treemodel)
