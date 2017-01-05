import logging

from PyQt5 import QtCore, QtGui, QtWidgets


logger = logging.getLogger(__name__)


class StockTableModel(QtCore.QAbstractTableModel):
    _header = None
    _data = None
    _blink_indexes = None
    _blink_msec = None
    _blink_color = None

    def __init__(self, parent):
        super(StockTableModel, self).__init__(parent)
        self._header = []
        self._data = []
        self._blink_indexes = []
        self._blink_msec = 500
        self._blink_color = QtGui.QColor('blue')

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._header)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if section >= 0 and section < self.columnCount():
                return self._header[section].get(role)
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            if section >= 0 and section < self.rowCount():
                return section + 1
        return None

    def setHeaderData(self, section, orientation, value, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if section >= 0 and section < self.columnCount():
                self._header[section][role] = value
                self.headerDataChanged.emit(orientation, section, section)
                return True
        return False

    def sort(self, column, order):
        col_data = []
        for row in range(self.rowCount()):
            index = self.index(row, column)
            key = self.data(index, QtCore.Qt.UserRole)
            if key is None:
                key = self.data(index, QtCore.Qt.DisplayRole)
            col_data.append((key, row))
        col_data.sort(key=lambda x: float('-inf') if x[0] != x[0] else x[0],
                      reverse=order == QtCore.Qt.AscendingOrder)

        new_data = []
        for item in col_data:
            new_data.append(self._data[item[1]])

        self.resetBlinkCell()
        self._data = new_data
        self.dataChanged.emit(
            self.index(0,0),
            self.index(self.rowCount() - 1, self.columnCount() - 1)
        )

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self._data[index.row()][index.column()]

        if role == QtCore.Qt.DisplayRole:
            return item.get(role, item.get(QtCore.Qt.EditRole))
        return item.get(role)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return False

        item = self._data[index.row()][index.column()]

        # for float('nan')
        if value != value:
            item[role] = value
            return True

        if item.get(role) == value:
            return False

        roles = []
        roles.append(role)
        item[role] = value
        if role == QtCore.Qt.DisplayRole:
            item[QtCore.Qt.BackgroundRole] = self._blink_color
            roles.append(QtCore.Qt.BackgroundRole)

        self.dataChanged.emit(index, index, roles)

        if role == QtCore.Qt.DisplayRole and \
                index not in self._blink_indexes:
            self._blink_indexes.append(index)
            QtCore.QTimer.singleShot(self._blink_msec, self.resetBlinkCell)
        return True

    def itemData(self, index):
        if index.isValid():
            return self._data[index.row()][index.column()]

    def setItemData(self, index, roleData):
        if index.isValid():
            self._data[index.row()][index.column()] = roleData
        return True

    def setRowData(self, row, value, role=QtCore.Qt.DisplayRole):
        if row < 0 or row >= self.rowCount():
            return False
        for column in range(self.columnCount()):
            self._data[row][column][role] = value
        self.dataChanged.emit(
            self.index(row, 0), self.index(row, self.rowCount() - 1), [role])
        return True

    def insertRows(self, row, count, parent=None):
        parent = parent or QtCore.QModelIndex()
        self.beginInsertRows(parent, row, row + count - 1)
        for x in range(count):
            self._data.insert(row, [{}] * self.columnCount())
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=None):
        parent = parent or QtCore.QModelIndex()
        self.beginRemoveRows(parent, row, row + count - 1)
        for x in range(count):
            del self._data[row]
        self.endRemoveRows()
        return True

    def insertColumns(self, column, count, parent=None):
        parent = parent or QtCore.QModelIndex()
        self.beginInsertColumns(parent, column, column + count - 1)
        for x in range(count):
            self._header.insert(column, {})
            for row in range(self.rowCount()):
                self._data[row].insert(column, {})
        self.endInsertColumns()
        return True

    def removeColumns(self, column, count, parent=None):
        parent = parent or QtCore.QModelIndex()
        self.beginRemoveColumns(parent, column, column + count - 1)
        for x in range(count):
            del self._header[column]
            for row in range(self.rowCount()):
                del self._data[row][column]
        self.endRemoveColumns()
        return True

    def flags(self, index):
        if index.isValid() and  \
                QtCore.Qt.EditRole in self._data[index.row()][index.column()]:
            return super(StockTableModel, self).flags(index) |  \
                QtCore.Qt.ItemIsEditable
        return super(StockTableModel, self).flags(index)

    def setTableData(self, data, header):
        self.beginResetModel()
        self._data = data
        self._header = header
        self.endResetModel()

    @QtCore.pyqtSlot()
    def resetBlinkCell(self):
        for index in self._blink_indexes:
            self._blink_indexes.remove(index)
            if index.isValid():
                item = self._data[index.row()][index.column()]
                if QtCore.Qt.BackgroundRole in item:
                    del item[QtCore.Qt.BackgroundRole]
                    self.dataChanged.emit(index, index, [QtCore.Qt.BackgroundRole])


class FormatItemDelegate(QtWidgets.QStyledItemDelegate):
    _format = None
    _preformat = None

    def __init__(self, fmt, preformat=None, parent=None):
        super(FormatItemDelegate, self).__init__(parent)
        self._format = fmt
        self._preformat = preformat

    def displayText(self, value, locale):
        if callable(self._preformat):
            value = self._preformat(value)
        # for float('nan')
        if value != value:
            return ''
        if value == '':
            return ''
        return self._format % value
