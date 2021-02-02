from PySide6.QtGui import QPainter, QBrush, QColor, QFont
from PySide6.QtWidgets import QMainWindow, QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QFile, QAbstractItemModel, QModelIndex, QObject

class TreeItem(object):
    def __init__(self, data, rowtype, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []
        self._rowtype = rowtype

    def appendChild(self, item):
        self.childItems.append(item)
        return self.childItems[-1]

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def row_type(self):
        return self._rowtype


class TreeModel(QAbstractItemModel):
    def __init__(self, projects, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(("Projects",), None)
        self.setupModelData(projects, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.FontRole:
            if item.row_type() == 'build':
                font = QFont()
                font.setBold(True)
                font.setItalic(True)
                return font

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, projects: list, parent: QModelIndex):
        for project in projects:
            p = parent.appendChild(TreeItem(("Project {}".format(project['mpn']),), 'project', parent))
            for rev in project['revs']:
                r = p.appendChild(TreeItem(("Rev {}".format(rev['revcode']),), 'rev', p))
                for build in rev['builds']:
                    r.appendChild(TreeItem(("Build {}".format(build['buildcode']),), 'build', r))
        pass