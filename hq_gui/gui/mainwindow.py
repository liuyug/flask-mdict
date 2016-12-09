#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import logging
import json
import time
import datetime
import os.path
import tempfile
from collections import OrderedDict

from six.moves.urllib.parse import urlencode
from six.moves import configparser, StringIO
from PyQt5 import QtWidgets, QtCore, QtGui

from .ui.ui_mainwindow import Ui_MainWindow
from .utils import url_downloader, string_to_bool
from .datatype import DataType, UserDataType
from .policy import get_policy_desc

from .model import StockTableModel, FormatItemDelegate

logger = logging.getLogger(__name__)


class HQWorker(QtCore.QObject):
    _timer = None
    _url = None
    _internal = 1000
    _open_time = datetime.time(9, 0, 0)
    _end_time = datetime.time(15, 30, 0)
    dataReady = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(HQWorker, self).__init__(parent)
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.do_timer_work)

    def set_request(self, url, internal):
        self._url = url
        self._internal = internal

    def moveToThread(self, thread):
        self._timer.moveToThread(thread)
        super(HQWorker, self).moveToThread(thread)

    @QtCore.pyqtSlot()
    def do_work(self):
        self.do_update()
        self._timer.start(self._internal)

    @QtCore.pyqtSlot()
    def do_timer_work(self):
        now = datetime.datetime.now().time()
        if self._open_time < now < self._end_time:
            self.do_update()

    def do_update(self):
        url = self._url
        res = url_downloader(url)
        if res['data'] is None:
            logger.warn(res['error'])
            return
        hq_data = json.loads(res['data'].decode('utf8')).get('hq')
        self.dataReady.emit(hq_data)


class MainWindow(QtWidgets.QMainWindow):
    ui = None
    _setting_ini = 'stockhq.ini'
    _setting = None
    _stock_code = None
    _stock_datatype = None
    _selected_lineedit_submited = False
    _worker_object = None
    _work_thread = None
    _lcd_clock = None
    _clock_timer = None
    _selected_header = ['MCODE', 'ZQMC', '_policy']

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Stock HQ')

        self._lcd_clock = QtWidgets.QLCDNumber(self)
        self._lcd_clock.setDigitCount(8)
        self.ui.statusBar.addPermanentWidget(self._lcd_clock)
        self._clock_timer = QtCore.QTimer(self)
        self._clock_timer.timeout.connect(self.on_clock_timer)
        self._clock_timer.start(1000)

        # setup by order!!
        self.setup_stock_setting()
        self.setup_selected_stock()
        self.setup_selected_hq_header()
        self.setup_stock_hq()

        setting = self.get_setting()
        state = (setting['state'].get('mainwindow') or '').encode()
        self.restoreGeometry(
            QtCore.QByteArray.fromBase64(state))

        # hq worker
        self._worker_object = HQWorker()
        self._work_thread = QtCore.QThread()
        self._worker_object.moveToThread(self._work_thread)
        self._worker_object.dataReady.connect(self.hq_update)
        self._work_thread.started.connect(self._worker_object.do_work)
        self._work_thread.finished.connect(self.hq_update_stop)

        # beep test
        self.beep()

    def closeEvent(self, e):
        setting = self.get_setting()

        selected_stock = self.get_selected_stock()
        setting['general']['stockhq_url'] = self.ui.lineEdit_url.text()
        setting['general']['selected'] = ','.join(list(selected_stock.keys()))

        header_dt = []
        for row in range(self.ui.listWidget_hq_header_right.count()):
            item = self.ui.listWidget_hq_header_right.item(row)
            header_dt.append(item.data(QtCore.Qt.UserRole))
        setting['general']['hq_header'] = ','.join(header_dt)

        state = self.ui.tableView_hq.horizontalHeader().saveState()
        setting['state']['hq_header'] = bytes(state.toBase64()).decode()
        state = self.saveGeometry()
        setting['state']['mainwindow'] = bytes(state.toBase64()).decode()

        for k, v in selected_stock.items():
            setting['policy'][k] = v['_policy']
        setting['log']['log'] = self.ui.checkBox_log_to_file.isChecked()
        setting['log']['logfile'] = self.ui.lineEdit_logfile.text()

        config = configparser.ConfigParser()
        config.optionxform = str
        for section in setting:
            config.add_section(section)
            for option, value in setting[section].items():
                if value is None:
                    value = ''
                else:
                    value = '%s' % value
                config.set(section, option, value)
        with open(self._setting_ini, 'w') as f:
            config.write(f)
        self._work_thread.quit()
        self._work_thread.wait()

    @QtCore.pyqtSlot()
    def on_clock_timer(self):
        self._lcd_clock.display(datetime.datetime.now().strftime('%H:%M:%S'))

    def get_setting(self):
        if self._setting:
            return self._setting
        if os.path.exists(self._setting_ini):
            logger.info('Read setting from %s' % self._setting_ini)
            config = configparser.ConfigParser()
            config.optionxform = str
            with open(self._setting_ini, 'rb') as f:
                text = f.read().decode('utf8')
                config.readfp(StringIO(text))
                self._setting = OrderedDict()
                for section in config.sections():
                    self._setting[section] = OrderedDict(config.items(section))
        else:
            self._setting = OrderedDict()
            self._setting['general'] = OrderedDict((
                ('stockhq_url', 'http://www.mylocal.home/hq'),
                ('selected', ''),
                ('hq_header', 'MCODE', 'ZQMC', '_policy'),
            ))
            self._setting['state'] = OrderedDict((
                ('hq_header', ''),
                ('mainwindow', ''),
            ))
            self._setting['policy'] = OrderedDict()
            self._setting['log'] = OrderedDict((
                ('log', 'false'),
                ('logfile', 'stockhq.log'),
            ))
        return self._setting

    def setup_stock_setting(self):
        setting = self.get_setting()
        # stock
        self.ui.lineEdit_url.setText(setting['general']['stockhq_url'])
        sh_count = sz_count = 0
        for k in self.get_stock_code():
            if k['market'] == 'SH':
                sh_count += 1
            elif k['market'] == 'SZ':
                sz_count += 1
            else:
                raise ValueError(k)
        self.ui.label_sh.setNum(sh_count)
        self.ui.label_sz.setNum(sz_count)
        # log
        checked = string_to_bool(setting['log']['log'])
        self.ui.lineEdit_logfile.setText(setting['log']['logfile'])
        self.ui.checkBox_log_to_file.setChecked(checked)
        self.setting_checkbox_log_toggled(checked)
        self.ui.checkBox_log_to_file.toggled.connect(self.setting_checkbox_log_toggled)

    def setup_selected_stock(self):
        abbrs = []
        for k in self.get_stock_code():
            abbrs.append('%(market)s%(code)s %(name)s %(abbr)s' % k)
        completer = QtWidgets.QCompleter(abbrs, self)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.activated.connect(self.selected_completer_activated)
        self.ui.lineEdit_stock.setCompleter(completer)
        self.ui.lineEdit_stock.returnPressed.connect(self.selected_lineedit_returnpressed)
        self.ui.lineEdit_stock.textEdited.connect(self.selected_lineedit_textedited)

        self.ui.pushButton_add_stock.clicked.connect(self.selected_stock_add)
        self.ui.pushButton_delete_stock.clicked.connect(self.selected_stock_delete)
        self.ui.pushButton_clearall_stock.clicked.connect(self.selected_stock_clearall)

        model = StockTableModel(self)
        setting = self.get_setting()

        header = []
        for dt in self._selected_header:
            if dt in DataType:
                desc = DataType[dt].get('desc')
            elif dt in UserDataType:
                desc = UserDataType[dt].get('desc')
            else:
                desc = dt
            header.append({
                QtCore.Qt.DisplayRole: desc,
                QtCore.Qt.UserRole: dt,
            })

        data = []
        mcodes = setting['general']['selected'].split(',')
        stock_code = self.get_stock_code()
        for s in stock_code:
            s_mcode = '%(market)s%(code)s' % s
            if s_mcode in mcodes:
                record = []
                record.append({QtCore.Qt.DisplayRole: s_mcode})
                record.append({
                    QtCore.Qt.DisplayRole: s['name'],
                    QtCore.Qt.UserRole: s['abbr'],
                })
                policy = setting['policy'].get(s_mcode) or ''
                record.append({QtCore.Qt.EditRole: policy})
                mcodes.remove(s_mcode)
                data.append(record)
        model.setTableData(data, header)

        self.ui.tableView_selected_stock.setModel(model)
        self.ui.tableView_selected_stock.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.ui.tableView_selected_stock.setTabKeyNavigation(False)
        self.ui.tableView_selected_stock.horizontalHeader().setStretchLastSection(True)
        model.dataChanged.connect(self.on_data_changed)

    def setup_selected_hq_header(self):
        setting = self.get_setting()

        self.ui.listWidget_hq_header_right.setDragDropMode(
            QtWidgets.QAbstractItemView.InternalMove)

        hq_header = OrderedDict()
        for h in setting['general']['hq_header'].split(','):
            hq_header[h] = ''
        for h in self._selected_header:
            if h not in hq_header:
                hq_header[h] = ''

        for dt, data in DataType.items():
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, data.get('desc'))
            item.setData(QtCore.Qt.UserRole, dt)
            if dt in hq_header:
                hq_header[dt] = item
            else:
                self.ui.listWidget_hq_header_left.addItem(item)
        for dt, data in UserDataType.items():
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, data.get('desc'))
            item.setData(QtCore.Qt.UserRole, dt)
            if dt in hq_header:
                hq_header[dt] = item
            else:
                self.ui.listWidget_hq_header_left.addItem(item)
        for item in list(hq_header.values()):
            self.ui.listWidget_hq_header_right.addItem(item)

        self.ui.listWidget_hq_header_right.itemDoubleClicked.connect(
            self.selected_hq_header_move)
        self.ui.listWidget_hq_header_left.itemDoubleClicked.connect(
            self.selected_hq_header_move)

    def setup_stock_hq(self):
        model = StockTableModel(self)

        header = OrderedDict()
        for row in range(self.ui.listWidget_hq_header_right.count()):
            item = self.ui.listWidget_hq_header_right.item(row)
            header[item.data(QtCore.Qt.UserRole)] = {
                QtCore.Qt.DisplayRole: item.data(QtCore.Qt.DisplayRole),
                QtCore.Qt.UserRole: item.data(QtCore.Qt.UserRole),
            }

        data = []
        for s in self.get_selected_stock().values():
            row = self.hq_create_stock_record(s, list(header.keys()))
            data.append(row)

        model.setTableData(data, list(header.values()))

        format_delegate = FormatItemDelegate('%s', self)
        for column in range(model.columnCount()):
            self.ui.tableView_hq.setItemDelegateForColumn(column, format_delegate)

        self.ui.tableView_hq.setModel(model)

        self.ui.tableView_hq.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.ui.tableView_hq.setTabKeyNavigation(False)

        setting = self.get_setting()
        state = (setting['state'].get('hq_header') or '').encode()
        self.ui.tableView_hq.horizontalHeader().restoreState(
            QtCore.QByteArray.fromBase64(state)
        )

        model.dataChanged.connect(self.on_data_changed)
        self.ui.pushButton_hq_start_stop.clicked.connect(self.hq_button_start_stop)

    def status_show_message(self, message):
        self.ui.statusBar.showMessage(message)

    def beep(self):
        QtWidgets.QApplication.beep()

    def get_stock_code(self):
        if self._stock_code:
            return self._stock_code

        # add local cache
        stock_code_json = os.path.join(tempfile.gettempdir(), 'stock_code.json')
        if os.path.exists(stock_code_json):
            day_second = 3600 * 24
            m_time = os.path.getmtime(stock_code_json)
            if time.time() < (m_time + day_second):
                self._stock_code = json.load(open(stock_code_json))
                logger.info('Read stock code from "%s"' % stock_code_json)
                return self._stock_code
        base_url = self.ui.lineEdit_url.text()
        url = '%s/ths/code/' % base_url
        logger.debug('request stock code from ' + url)
        res = url_downloader(url)
        self._stock_code = json.loads(res['data'].decode('utf8')).get('code')
        json.dump(self._stock_code, open(stock_code_json, 'w'))
        return self._stock_code

    @QtCore.pyqtSlot(bool)
    def setting_checkbox_log_toggled(self, checked):
        self.ui.label_log.setEnabled(checked)
        self.ui.lineEdit_logfile.setEnabled(checked)
        if checked:
            logfile = self.ui.lineEdit_logfile.text()
            file_handler = logging.FileHandler(logfile)
            formatter = logging.Formatter('[%(module)-10s: %(levelname)-5s] %(message)s')
            file_handler.setFormatter(formatter)
            logging.getLogger('').addHandler(file_handler)

    @QtCore.pyqtSlot()
    def selected_lineedit_returnpressed(self):
        completer = self.ui.lineEdit_stock.completer()
        if self._selected_lineedit_submited:
            self.selected_stock_add()
            self.ui.lineEdit_stock.clear()
            self._selected_lineedit_submited = False
        else:
            self.ui.lineEdit_stock.setText(completer.currentCompletion())
            self._selected_lineedit_submited = True

    @QtCore.pyqtSlot()
    def selected_lineedit_textedited(self):
        self._selected_lineedit_submited = False

    @QtCore.pyqtSlot(str)
    def selected_completer_activated(self, text):
        self._selected_lineedit_submited = True

    @QtCore.pyqtSlot()
    def selected_stock_add(self, mcode=None):
        model = self.ui.tableView_selected_stock.model()
        mcode = mcode or self.ui.lineEdit_stock.text()[:8]
        selected_stock = self.get_selected_stock()
        if mcode in selected_stock:
            self.status_show_message(
                'Already exists stock: %(mcode)s[%(zqmc)s]' % selected_stock[mcode])
            self.ui.lineEdit_stock.clear()
            return
        stock_code = self.get_stock_code()
        for s in stock_code:
            s_mcode = '%(market)s%(code)s' % s
            if s_mcode == mcode:
                record = []
                record.append({QtCore.Qt.DisplayRole: s_mcode})
                record.append({QtCore.Qt.DisplayRole: s['zqmc']})
                record.append({QtCore.Qt.EditRole: ''})
                row = model.rowCount()
                model.insertRow(row)
                for column in range(len(record)):
                    model.setItemData(model.index(row, column), record[column])
                self.ui.lineEdit_stock.clear()
                self.status_show_message('Add stock: %s[%s]' % (mcode, s['zqmc']))
                break

    @QtCore.pyqtSlot()
    def selected_stock_delete(self):
        selected_indexes = self.ui.tableView_selected_stock.selectionModel().selectedRows()
        model = self.ui.tableView_selected_stock.model()
        rows = sorted([x.row() for x in selected_indexes])[::-1]
        for x in rows:
            model.removeRow(x)

    @QtCore.pyqtSlot()
    def selected_stock_clearall(self):
        model = self.ui.tableView_selected_stock.model()
        count = model.rowCount()
        model.removeRows(0, count)

    @QtCore.pyqtSlot('QListWidgetItem*')
    def selected_hq_header_move(self, item):
        left_row = self.ui.listWidget_hq_header_left.row(item)
        right_row = self.ui.listWidget_hq_header_right.row(item)
        if left_row > -1:
            self.ui.listWidget_hq_header_left.takeItem(left_row)
            self.ui.listWidget_hq_header_right.addItem(item)
        elif right_row > -1:
            self.ui.listWidget_hq_header_right.takeItem(right_row)
            self.ui.listWidget_hq_header_left.addItem(item)
        else:
            raise ValueError('Unknow item "%s"' % item.text())

    def get_selected_stock(self):
        selected_stock = {}
        model = self.ui.tableView_selected_stock.model()
        header = []
        for x in range(model.columnCount()):
            header.append(model.headerData(
                x, QtCore.Qt.Horizontal, QtCore.Qt.UserRole))

        for row in range(model.rowCount()):
            stock = {}
            for column in range(model.columnCount()):
                h = model.headerData(
                    column, QtCore.Qt.Horizontal, QtCore.Qt.UserRole).lower()
                if h == 'zqmc':
                    abbr = model.data(model.index(row, column), QtCore.Qt.UserRole)
                    stock['abbr'] = abbr
                stock[h] = model.data(model.index(row, column))
            selected_stock[stock['mcode']] = stock
        return selected_stock

    def hq_create_stock_record(self, stock, datatype):
        row = []
        for dt in datatype:
            if dt == 'MCODE':
                row.append({QtCore.Qt.DisplayRole: stock['mcode']})
            elif dt == 'ZQMC':
                row.append({
                    QtCore.Qt.DisplayRole: stock['zqmc'],
                    QtCore.Qt.UserRole: stock['abbr'],
                })
            elif dt in ['DATE', 'TIME']:
                row.append({QtCore.Qt.DisplayRole: ''})
            elif dt == '_policy':
                row.append({QtCore.Qt.EditRole: stock['_policy']})
            else:
                row.append({QtCore.Qt.DisplayRole: float('nan')})
        return row

    def hq_check_policy(self, index, record):
        if record['NEW'] is None:
            return

        model = index.model()
        dt = UserDataType.get('_policy')
        item = model.itemData(index)

        policies = item.get(QtCore.Qt.EditRole).split(',')
        if 'inc_10' not in policies:
            policies.append('inc_10')
        if 'dec_10' not in policies:
            policies.append('dec_10')
        new_states = set(dt['calc'](policies, record))
        states = item.get(QtCore.Qt.UserRole) or set()
        item[QtCore.Qt.UserRole] = new_states
        diff_on = new_states - states
        diff_off = states - new_states

        bold_font = self.font()
        bold_font.setBold(True)

        for d in diff_off:
            if d in ['inc_10', 'dec_10']:
                self.beep()
            message = '[%s %s][%s %s][OFF]: %s' % (
                record['DATE'], record['TIME'],
                record['MCODE'], record['ZQMC'], get_policy_desc(d))
            logger.info(message)
            self.status_show_message(message)
            model.setRowData(index.row(), self.font(), QtCore.Qt.FontRole)
        for d in diff_on:
            if d in ['inc_10', 'dec_10']:
                self.beep()
            else:
                self.beep()
            message = '[%s %s][%s %s][ON] : %s' % (
                record['DATE'], record['TIME'],
                record['MCODE'], record['ZQMC'], get_policy_desc(d))
            logger.info(message)
            self.status_show_message(message)
            model.setRowData(index.row(), bold_font, QtCore.Qt.FontRole)

    @QtCore.pyqtSlot(list)
    def hq_update(self, hq_data):
        model = self.ui.tableView_hq.model()
        header_datatype = []
        for column in range(model.columnCount()):
            dt = model.headerData(column, QtCore.Qt.Horizontal, QtCore.Qt.UserRole)
            header_datatype.append(dt)

        red = QtGui.QColor('red')
        green = QtGui.QColor('green')
        black = QtGui.QColor('black')
        mcode_column = header_datatype.index('MCODE')
        for hq in hq_data:
            for record in hq.values():
                cur_row = None
                for row in range(model.rowCount()):
                    if record['MCODE'] == model.data(model.index(row, mcode_column)):
                        cur_row = row
                        break
                # not find mcode in model
                if cur_row is None:
                    logger.warn('Do not find %(MCODE)s %(ZQMC)s' % record)
                    continue
                # from source
                for k, v in record.items():
                    if k not in header_datatype:
                        continue
                    if k in ['MCODE', 'ZQMC', 'DATE', 'TIME']:
                        # must be string
                        v = v or ''
                    elif record['NEW'] is None:
                        # pause transaction
                        v = float('nan')
                    elif v is None:
                        # no value at some datetype
                        v = float('nan')
                    elif k in ['VOL']:
                        v = float(v) / 100.0
                    else:
                        # reset to '0' for '-0.0'
                        v = float(v) or 0.0
                    column = header_datatype.index(k)
                    model.setData(model.index(cur_row, column), v)
                # calculate
                if record['NEW'] is None:
                    continue
                for k, dt in UserDataType.items():
                    if k not in header_datatype:
                        continue
                    column = header_datatype.index(k)
                    if k == '_policy':
                        self.hq_check_policy(
                            model.index(cur_row, column), record)
                        continue
                    value = dt['calc'](record)
                    if k == '_zhangdiefu':
                        color = black
                        if value > 0:
                            color = red
                        elif value < 0:
                            color = green
                        model.setData(model.index(cur_row, column),
                                      color, QtCore.Qt.ForegroundRole)
                    model.setData(model.index(cur_row, column), value)

    @QtCore.pyqtSlot()
    def hq_update_stop(self):
        self.ui.pushButton_hq_start_stop.setText('开始')

    @QtCore.pyqtSlot()
    def hq_button_start_stop(self):
        if self._work_thread.isRunning():
            self._work_thread.quit()
            return

        model = self.ui.tableView_hq.model()

        header = OrderedDict()
        for row in range(self.ui.listWidget_hq_header_right.count()):
            item = self.ui.listWidget_hq_header_right.item(row)
            header[item.data(QtCore.Qt.UserRole)] = {
                QtCore.Qt.DisplayRole: item.data(QtCore.Qt.DisplayRole),
                QtCore.Qt.UserRole: item.data(QtCore.Qt.UserRole),
            }

        diff = model.columnCount() - len(header)
        if diff > 0:
            model.removeColumns(0, diff)
        elif diff < 0:
            model.insertColumns(0, -diff)

        column = 0
        for dt, data in header.items():
            # set header
            for role, value in data.items():
                model.setHeaderData(
                    column, QtCore.Qt.Horizontal, value, role)
            # set item delegate
            if dt in DataType:
                fmt = DataType[dt].get('format')
                prefmt = DataType[dt].get('preformat')
            elif dt in UserDataType:
                fmt = UserDataType[dt].get('format')
                prefmt = UserDataType[dt].get('preformat')
            self.ui.tableView_hq.setItemDelegateForColumn(
                column, FormatItemDelegate(fmt, prefmt, self))
            column += 1

        selected_stock = self.get_selected_stock()
        hq_stock = []
        for row in range(model.rowCount())[::-1]:
            mcode = model.data(model.index(row, 0))
            if mcode in selected_stock:
                hq_stock.append(mcode)
            else:
                model.removeRow(row)
        for s in selected_stock.values():
            if s['mcode'] not in hq_stock:
                record = self.hq_create_stock_record(s, list(header.keys()))
                row = model.rowCount()
                model.insertRow(row)
                for column in range(len(record)):
                    model.setItemData(model.index(row, column), record[column])

        base_url = self.ui.lineEdit_url.text()
        data = {
            'mcode': ';'.join(list(selected_stock.keys())),
            'datatype': ','.join(list(DataType.keys())),
        }
        hq_source = 'ths'
        url = '%s/%s/hq?%s' % (
            base_url, hq_source, urlencode(data, safe=';,'))
        logger.debug('request hq from ' + url)

        self._worker_object.set_request(url, 500)
        self._work_thread.start()
        self.ui.pushButton_hq_start_stop.setText('停止')

    @QtCore.pyqtSlot('QModelIndex', 'QModelIndex', 'QVector<int>')
    def on_data_changed(self, lf, br, roles):
        dt = lf.model().headerData(
            lf.column(), QtCore.Qt.Horizontal, QtCore.Qt.UserRole)
        if dt == '_policy' and QtCore.Qt.EditRole in roles:
            mcode = lf.sibling(lf.row(), 0).data()
            if lf.model() == self.ui.tableView_hq.model():
                model = self.ui.tableView_selected_stock.model()
            else:
                model = self.ui.tableView_hq.model()

            for row in range(model.rowCount()):
                if mcode == model.data(model.index(row, 0)):
                    break
            for column in range(model.columnCount()):
                if dt == model.headerData(
                        column, QtCore.Qt.Horizontal, QtCore.Qt.UserRole):
                    break
            model.setData(
                model.index(row, column),
                lf.data(), QtCore.Qt.EditRole)
