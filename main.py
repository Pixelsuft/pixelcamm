from threading import Thread as thread
import cv2
from sys import exit as sys_exit
from sys import argv as start_args
from PyQt5 import QtWidgets as qt_widgets
from PyQt5 import QtGui
from pixelcamm import Ui_MainWindow as main_window
from clear_cache import clear as clear_cache
from time import sleep as time_sleep
from os import access as file_exists
from os import F_OK as file_exists_param
from os import getlogin as get_user
from os import mkdir as make_dir
from os.path import isdir as is_folder
from os import name as os_type
from os import getcwd as cur_dir


vid = cv2.VideoCapture(0)
is_recording = False
checked_show = True
width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
preview_fps = 30
record_speed = 1
reload_size_sleep = 1
running = True


def get_all_cameras():
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            ui.cameraBox.addItem('Camera ' + str(index))
            cap.release()
        else:
            break
        index += 1
    return index


def change_camera():
    global vid
    global width
    global height
    vid = cv2.VideoCapture(ui.cameraBox.currentIndex())
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))


def read_config():
    if file_exists('config.txt', file_exists_param):
        global checked_show
        global preview_fps
        global reload_size_sleep
        tempf = open('config.txt', 'r')
        readed = tempf.read().split('\n')
        tempf.close()
        checked_show = bool(readed[0])
        preview_fps = int(readed[1])
        # reload_size_sleep = int(readed[2])
        ui.dirpathEdit.setText(str(readed[3]))
        ui.filepathEdit.setText(str(readed[4]))
    else:
        if os_type == 'nt':
            ui.dirpathEdit.setText('C:\\Users\\' + get_user() + '\\Documents\\Pixelcamm')
        else:
            ui.dirpathEdit.setText(cur_dir())
        ui.filepathEdit.setText('Output')


def save_config():
    full_str = str(checked_show) + '\n'
    full_str += str(preview_fps) + '\n'
    full_str += str(reload_size_sleep) + '\n'
    full_str += str(ui.dirpathEdit.text()) + '\n'
    full_str += str(ui.filepathEdit.text()) + '\n'
    tempf = open('config.txt', 'w')
    tempf.write(full_str)
    tempf.close()


def reload_size_loop():
    global checked_show
    back_width = 0
    back_height = 0
    while running:
        width = MainWindow.frameGeometry().width()
        height = MainWindow.frameGeometry().height()
        if not back_width == width or not back_height == height:
            temp_show = checked_show
            checked_show = False
            back_width = width
            back_height = height
            reload_size(width, height)
            if temp_show:
                checked_show = True
                thread(target=reload_camera).start()
        time_sleep(reload_size_sleep)


def reload_size(width, height):
    ui.mainLabel.setGeometry(int(width / 2) - 100, 0, 200, 30)
    ui.cameraBox.setGeometry(width - 360, 30, 350, 30)
    ui.showCheck.setGeometry(width - 235, 0, 120, 20)
    ui.dirpathLabel.setGeometry(width - 275, 70, 200, 30)
    ui.filepathLabel.setGeometry(width - 275, 190, 200, 30)
    ui.dirpathEdit.setGeometry(width - 360, 100, 350, 30)
    ui.dirpathButton.setGeometry(width - 360, 140, 350, 30)
    ui.filepathEdit.setGeometry(width - 360, 220, 350, 30)
    ui.formatEdit.setGeometry(width - 240, 260, 230, 30)
    ui.imgformatEdit.setGeometry(width - 240, 300, 230, 30)
    ui.formatLabel.setGeometry(width - 360, 260, 110, 30)
    ui.imgformatLabel.setGeometry(width - 360, 300, 110, 30)
    ui.snapshotButton.setGeometry(width - 360, 380, 350, 40)
    ui.recordButton.setGeometry(width - 360, 430, 350, 40)
    ui.cameraImage.setGeometry(10, 30, width - 380, height - 70)


def get_norm_filename(format):
    dirpath = ui.dirpathEdit.text().replace('/', '\\')
    if not is_folder(dirpath):
        make_dir(dirpath)
    output_file = dirpath + '\\' + ui.filepathEdit.text()
    if file_exists(output_file + '.' + format, file_exists_param):
        i = 1
        temp_file = None
        while True:
            temp_file = output_file + ' (' + str(i) + ').' + format
            if not file_exists(temp_file, file_exists_param):
                break
            i += 1
        return temp_file
    else:
        return output_file + '.' + format


def dirpath_select():
    dialog = qt_widgets.QFileDialog()
    foo_dir = dialog.getExistingDirectory(MainWindow, 'Select Path')
    ui.dirpathEdit.setText(foo_dir.replace('/', '\\'))


def reload_camera():
    global current_frame
    while checked_show:
        img = QtGui.QImage(vid.read()[1], width, height, QtGui.QImage.Format_RGB888)
        img = QtGui.QPixmap.fromImage(img)
        ui.cameraImage.setPixmap(img)
        if preview_fps > 0:
            time_sleep(1 / preview_fps)


def change_check_show():
    global checked_show
    if ui.showCheck.checkState():
        checked_show = True
        thread(target=reload_camera).start()
    else:
        checked_show = False


def snapshot_file():
    out = cv2.VideoWriter(get_norm_filename(ui.imgformatEdit.text()), cv2.VideoWriter_fourcc(*'JPEG'), record_speed * 20, (width, height))
    out.write(vid.read()[1])
    out.release()


def record_file():
    ui.dirpathEdit.setEnabled(False)
    ui.formatEdit.setEnabled(False)
    ui.dirpathButton.setEnabled(False)
    ui.dirpathButton.setEnabled(False)
    ui.filepathEdit.setEnabled(False)
    out = cv2.VideoWriter(get_norm_filename(ui.formatEdit.text()), cv2.VideoWriter_fourcc(*'DIVX'), record_speed * 20, (width, height))
    ui.recordButton.setText('Stop!')
    while is_recording:
        out.write(vid.read()[1])
    out.release()
    ui.dirpathEdit.setEnabled(True)
    ui.cameraBox.setEnabled(True)
    ui.formatEdit.setEnabled(True)
    ui.dirpathButton.setEnabled(True)
    ui.dirpathButton.setEnabled(True)
    ui.filepathEdit.setEnabled(True)


def record_click():
    global is_recording
    if not is_recording:
        thread(target=record_file).start()
        is_recording = True
    else:
        ui.recordButton.setText('Record!')
        is_recording = False


app = qt_widgets.QApplication(start_args)
MainWindow = qt_widgets.QMainWindow()
ui = main_window()
ui.setupUi(MainWindow)
reload_size(1000, 480)
read_config()
ui.recordButton.clicked.connect(record_click)
ui.snapshotButton.clicked.connect(snapshot_file)
ui.dirpathButton.clicked.connect(dirpath_select)
ui.showCheck.clicked.connect(change_check_show)
ui.cameraBox.currentIndexChanged.connect(change_camera)
if get_all_cameras() > 0:
    thread(target=reload_camera).start()
thread(target=reload_size_loop).start()
MainWindow.show()
to_exit = app.exec_()
is_recording = False
checked_show = False
running = False
vid.release()
save_config()
clear_cache()
sys_exit(to_exit)
