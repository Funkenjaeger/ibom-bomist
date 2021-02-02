from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal, QModelIndex
from PySide6.QtWidgets import QLineEdit, QHeaderView


class PandasTableModel(QStandardItemModel):
    def __init__(self, data, parent=None):
        QStandardItemModel.__init__(self, parent)
        self._data = data
        for row in data.values.tolist():
            data_row = [QStandardItem("{}".format(x)) for x in row]
            self.appendRow(data_row)
        return

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[x]
        return None

    def row(self, index):
        return self._data.loc[index].to_list()

    def set_data(self, row, col, val):
        colindex = self._data.columns.get_loc(col)
        #index = self.createIndex(row,colindex)
        self._data.at[row, col] = val
        # self.dataChanged.emit(index, index, [])
        # self.layoutChanged.emit()
        self.setItem(row, colindex, QStandardItem('{}'.format(val)))


class FilterHeader(QHeaderView):
    filterActivated = Signal(list)

    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self._editors = []
        self._padding = 4
        self.setStretchLastSection(True)
        self.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setSortIndicatorShown(False)
        self.sectionResized.connect(self.adjustPositions)
        parent.horizontalScrollBar().valueChanged.connect(self.adjustPositions)

    def setFilterBoxes(self, count):
        while self._editors:
            editor = self._editors.pop()
            editor.deleteLater()
        for index in range(count):
            editor = QLineEdit(self.parent())
            editor.setPlaceholderText('Filter')
            editor.textChanged.connect(self.emitFilterActivated)
            self._editors.append(editor)
        self.adjustPositions()

    def emitFilterActivated(self):
        filter_strings = [e.text() for e in self._editors]
        self.filterActivated.emit(filter_strings)

    def sizeHint(self):
        size = super().sizeHint()
        if self._editors:
            height = self._editors[0].sizeHint().height()
            size.setHeight(size.height() + height + self._padding)
        return size

    def updateGeometries(self):
        if self._editors:
            height = self._editors[0].sizeHint().height()
            self.setViewportMargins(0, 0, 0, height + self._padding)
        else:
            self.setViewportMargins(0, 0, 0, 0)
        super().updateGeometries()
        self.adjustPositions()

    def adjustPositions(self):
        for index, editor in enumerate(self._editors):
            height = editor.sizeHint().height()
            editor.move(self.sectionPosition(index) - self.offset() + 2,
                        height + (self._padding // 2))
            editor.resize(self.sectionSize(index), height)

    def filterText(self, index):
        if 0 <= index < len(self._editors):
            return self._editors[index].text()
        return ''

    def setFilterText(self, index, text):
        if 0 <= index < len(self._editors):
            self._editors[index].setText(text)

    def clearFilters(self):
        for editor in self._editors:
            editor.clear()


class CustomSortFilterProxyModel(QSortFilterProxyModel):
    """
    Implements a QSortFilterProxyModel that allows for custom
    filtering. Add new filter functions using addFilterFunction().
    New functions should accept two arguments, the column to be
    filtered and the currently set filter string, and should
    return True to accept the row, False otherwise.
    Filter functions are stored in a dictionary for easy
    removal by key. Use the addFilterFunction() and
    removeFilterFunction() methods for access.
    The filterString is used as the main pattern matching
    string for filter functions. This could easily be expanded
    to handle regular expressions if needed.
    """
    def __init__(self, parent=None):
        super(CustomSortFilterProxyModel, self).__init__(parent)
        self.filterStrings = ''

    # def setFilterString(self, text):
    def setFilterStrings(self, strings):
        """
        text : string
            The string to be used for pattern matching.
        """
        self.filterStrings = strings
        self.invalidateFilter()

    def filterAcceptsRow(self, row_num, parent):
        """
        Reimplemented from base class to allow the use
        of custom filtering.
        """
        model = self.sourceModel()
        # The source model should have a method called row()
        # which returns the table row as a python list.
        return all([fs in s for s, fs in zip(model.row(row_num),
                                             self.filterStrings)])