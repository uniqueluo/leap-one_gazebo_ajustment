#!/usr/bin/env python
import rospy
import sys
import os
import pandas as pd
import copy

from python_qt_binding.QtCore import pyqtSlot
from python_qt_binding.QtCore import Qt
from python_qt_binding.QtCore import Signal
from python_qt_binding.QtGui import QFont
from python_qt_binding.QtWidgets import QApplication
from python_qt_binding.QtWidgets import QHBoxLayout
from python_qt_binding.QtWidgets import QLabel
from python_qt_binding.QtWidgets import QLineEdit
from python_qt_binding.QtWidgets import QPushButton
from python_qt_binding.QtWidgets import QSlider
from python_qt_binding.QtWidgets import QVBoxLayout
from python_qt_binding.QtWidgets import QGridLayout
from python_qt_binding.QtWidgets import QScrollArea
from python_qt_binding.QtWidgets import QSpinBox
from python_qt_binding.QtWidgets import QWidget
from python_qt_binding.QtWidgets import QCheckBox
from python_qt_binding.QtWidgets import QProgressBar
from python_qt_binding.QtWidgets import QListWidget
from python_qt_binding.QtWidgets import QTextEdit
from python_qt_binding.QtWidgets import QFileDialog
from python_qt_binding.QtWidgets import QMessageBox





from rosgraph_msgs.msg import Clock
from std_msgs.msg import Float64
from std_srvs.srv import Empty


config = {
    0:[True,'left_m1','/leap_one/left_m1_joint_position_controllers/command'],
    1:[True,'left_m2','/leap_one/left_m2_joint_position_controllers/command'],
    2:[True,'left_m3','/leap_one/left_m3_joint_position_controllers/command'],
    3:[True,'left_m4','/leap_one/left_m4_joint_position_controllers/command'],
    4:[True,'left_m5','/leap_one/left_m5_joint_position_controllers/command'],
    5:[True,'left_m6','/leap_one/left_m6_joint_position_controllers/command'],

    6:[True,'right_m1','/leap_one/right_m1_joint_position_controllers/command'],
    7:[True,'right_m2','/leap_one/right_m2_joint_position_controllers/command'],
    8:[True,'right_m3','/leap_one/right_m3_joint_position_controllers/command'],
    9:[True,'right_m4','/leap_one/right_m4_joint_position_controllers/command'],
    10:[True,'right_m5','/leap_one/right_m5_joint_position_controllers/command'],
    11:[True,'right_m6','/leap_one/right_m6_joint_position_controllers/command'],

    
}
enviromnt_conf = {
    'timescale':0.04,
    'joint_speed':0.08,
    'joint_max_position': 0.8,
    'joint_min_position': -0.8
}


class JointStatePublisherGui(QWidget):
    def __init__(self, title, jsp, num_rows=0):
        super(JointStatePublisherGui, self).__init__()
        font = QFont("Helvetica", 9, QFont.Bold)
        self.hlayout = QHBoxLayout(self)
        vlayout = QVBoxLayout()
        glayout = QGridLayout()
        right_l_lauout = QVBoxLayout()
        self.listVeiw = QListWidget()
        self.checkbox = []
        self.value_line_edit = []
        self.sliders = []
        self.positions = []
        self.progressbars = []

        self.value_last = []

        speed_max = enviromnt_conf['joint_speed']
        slider_max = speed_max * 1000

        position_max = enviromnt_conf['joint_max_position']
        progress_max = position_max * 1000

        #create joints widget
        for i in range(0, num_rows):
            if config[i][0]:
                g_in_g = QGridLayout()
                checkbox = QCheckBox(config[i][1])
                checkbox.setFont(font)

                self.checkbox.append(checkbox)
                
                value_line_edit = QLineEdit()
                value_line_edit.setFont(font)
                value_line_edit.setText("0.0")

                self.value_line_edit.append(value_line_edit)


                display_lable = QLabel()
                display_lable.setFont(font)
                display_lable.setText("Position:")

                position_label = QLabel()
                position_label.setFont(font)
                position_label.setText("0.0")

                self.positions.append(position_label)

                position_progress_bar = QProgressBar()
                position_progress_bar.setMaximum(progress_max)
                position_progress_bar.setMinimum(-progress_max)
                position_progress_bar.setValue(0)

                self.progressbars.append(position_progress_bar)


                slider = QSlider()
                slider.setMaximum(slider_max)
                slider.setMinimum(-slider_max)
                slider.setOrientation(Qt.Horizontal)
                slider.valueChanged.connect(self.slider_value_changed)
                self.sliders.append(slider)
                

                g_in_g.addWidget(checkbox, 0, 0)
                g_in_g.addWidget(value_line_edit, 0, 1)
                g_in_g.addWidget(display_lable, 0, 2)
                g_in_g.addWidget(position_label, 0, 3)
                g_in_g.addWidget(slider, 1, 0,1,2)
                g_in_g.addWidget(position_progress_bar, 1, 2,1,2)

                glayout.addLayout(g_in_g,i,0)
                
        
        #create v layout
        self.import_Btn = QPushButton('Import')
        self.import_Btn.setFont(font)
        self.import_Btn.clicked.connect(self.import_Btn_clecked)

        self.export_Btn = QPushButton('Export')
        self.export_Btn.setFont(font)
        self.export_Btn.clicked.connect(self.export_Btn_clicked)

        self.start_Btn = QPushButton("Start")
        self.start_Btn.setFont(font)
        self.start_Btn.clicked.connect(self.start_Btn_clicked)

        self.reset_Btn = QPushButton('Reset')
        self.reset_Btn.setFont(font)
        self.reset_Btn.clicked.connect(self.reset_Btn_clicked)

        self.record_Btn = QPushButton('Record')
        self.record_Btn.setFont(font)
        self.record_Btn.clicked.connect(self.record_Btn_clicked)

        self.replay_Btn = QPushButton('Repaly')
        self.replay_Btn.setFont(font)
        self.replay_Btn.clicked.connect(self.replay_Btn_clicked)

        self.delete_Btn = QPushButton("Delete")
        self.delete_Btn.setFont(font)
        self.delete_Btn.clicked.connect(self.delete_Btn_clicked)

        self.debug_Btn = QPushButton("Debug")
        self.debug_Btn.setFont(font)
        self.debug_Btn.clicked.connect(self.debug_Btn_clicked)

        vlayout.addWidget(self.import_Btn)
        vlayout.addWidget(self.export_Btn)
        vlayout.addWidget(self.start_Btn)
        vlayout.addWidget(self.reset_Btn)
        vlayout.addWidget(self.record_Btn)
        vlayout.addWidget(self.delete_Btn)
        vlayout.addWidget(self.replay_Btn)
        vlayout.addWidget(self.debug_Btn)


        self.master_url = QLineEdit("http://192.168.0.91:11311")
        self.master_url.setFont(font)

        self.master_ip = QLineEdit("192.168.0.91")
        self.master_ip.setFont(font)


        self.listVeiw.clicked.connect(self.listVeiw_clicked)
        self.listVeiw.currentRowChanged.connect(self.listVeiw_itemSelectionChanged)

        self.description  = QTextEdit("")
        self.description.setFont(font)

        #self.description.setGeometry(0,100,100,500)


        right_l_lauout.addWidget(self.master_url)
        right_l_lauout.addWidget(self.master_ip)
        right_l_lauout.addWidget(self.listVeiw)
        right_l_lauout.addWidget(self.description)

        right_l_lauout.setStretch(0,1)
        right_l_lauout.setStretch(1,1)
        right_l_lauout.setStretch(2,3)
        right_l_lauout.setStretch(3,1)

        self.num_rows = len(self.checkbox)
        self.hlayout.addLayout(glayout)
        self.hlayout.addLayout(vlayout)
        self.hlayout.addLayout(right_l_lauout)
        self.setLayout(self.hlayout)


        self.callback_start = None
        self.callback_pause = None
        self.callback_record = None
        self.callback_reset = None
        self.callback_replay = None
        self.callback_replay_stop = None
        self.callback_delete = None
        self.callback_debug = None
        self.callback_import = None
        self.callback_export = None
        self.callback_list_clicked = None

        self.listVeiw_isClicked = False
        self.listVeiw_current_item = 0
        self.listVeiw_len = 0
        self.f = QFileDialog()
    def who_data_changed(self):
        for i in range(0, self.num_rows):
            value_last = self.value_line_edit[i].text()
            value_last = float(value_last)*1000
            value = self.sliders[i].value()
            if value != value_last:
                return i
    def change_line_edit(self, change_index):
        value = self.sliders[change_index].value()
        value = float(value)/1000
        value = str(value)
        self.value_line_edit[change_index].setText(value)
    def change_position_edit(self, change_index):
        value = self.progressbars[change_index].value()
        value +=  self.sliders[change_index].value()
        self.progressbars[change_index].setValue(value)

        self.positions[change_index].setText(str(float(value)/1000))
    def reset_speed(self, change_index):
        self.sliders[change_index].setValue(0)
    def reset_speed_all(self):
        for i in range(0, self.num_rows):
            self.reset_speed(i)
    def set_speed(self,index,data):
        self.sliders[index].setValue(data)

    def import_Btn_clecked(self):
        self.file_path = self.f.getOpenFileName(caption='Import excel data',directory='',filter='*.xlsx',initialFilter='')
        self.file_path = self.file_path[0]
        if self.callback_import:
            self.callback_import()
        pass
    def export_Btn_clicked(self):
        self.file_path = self.f.getSaveFileName(caption='Save as excel data',directory='',filter='*.xlsx',initialFilter='')
        self.file_path = self.file_path[0]
        if self.callback_export:
            self.callback_export()
        pass
    def set_callback_start(self, func):
        self.callback_start = func
    def start_Btn_clicked(self):
        if self.start_Btn.text() == "Start":
            if self.callback_start:
                self.callback_start()
            self.start_Btn.setText("Pause")
        else:
            if self.callback_pause:
                self.callback_pause()
            self.start_Btn.setText("Start")
    def reset_Btn_clicked(self):
        self.reset_speed_all()
        self.reset_postion_all()

        if self.callback_reset:
            self.callback_reset()
    def replay_Btn_clicked(self):
        if self.replay_Btn.text() == "Replay":
            self.replay_Btn.setText("Stop")
            if self.callback_replay:
                self.callback_replay()
        else :
            self.replay_Btn.setText("Replay")
            if self.callback_replay_stop:
                self.callback_replay_stop()
    def debug_Btn_clicked(self):
        if self.callback_debug:
            self.callback_debug()
    def record_Btn_clicked(self):
        self.set_postion()
        self.listVeiw_len += 1
        if self.callback_record:
            self.callback_record()
        self.reset_speed_all()

    def listVeiw_itemSelectionChanged(self, index):
        self.listVeiw_isClicked = True
        self.listVeiw_current_item = index
        if self.callback_list_clicked:
            self.callback_list_clicked()

    def listVeiw_clicked(self, index):
        #print "index", index.row()
        if self.listVeiw_current_item != index.row():
            description_text = self.description.toPlainText()
            #self.listVeiw.item(self.listVeiw_current_item).setData(1,"123")
            #print self.listVeiw.item(self.listVeiw_current_item).data
        self.listVeiw_isClicked = True
        self.listVeiw_current_item = index.row()
        if self.callback_list_clicked:
            self.callback_list_clicked()


    def update_listView(self):
        print "update",self.listVeiw_len
        for i in range(0, self.listVeiw_len):
            view = self.listVeiw.item(i)
            view.setText(str(i))
    def get_listVeiw_current_item(self):
        return self.listVeiw_current_item
    def delete_Btn_clicked(self):
        if self.listVeiw_isClicked :
            print self.listVeiw_current_item
            self.listVeiw.removeItemWidget(self.listVeiw.takeItem(self.listVeiw_current_item))
            self.listVeiw_len -= 1
            if self.listVeiw_current_item  != self.listVeiw_len:
                self.update_listView()
            if self.callback_delete:
                self.callback_delete()
            if self.listVeiw_current_item == 0:
                self.listVeiw_current_item = 0
            else:
                self.listVeiw_current_item -= 1

            self.listVeiw.setCurrentRow(self.listVeiw_current_item )
            if self.listVeiw_len == 0:
                self.listVeiw_isClicked = False

    def listView_add_item(self, index):
        self.listVeiw.addItem(str(index))
    def listView_inset_item(self, index, label):
        self.listVeiw.insertItem(index,str(label))

    def slider_value_changed(self, data):
        change_index = self.who_data_changed()
        self.change_line_edit(change_index)
    def get_speed(self):
        speed = []
        for i in range(0, self.num_rows):
            value = self.sliders[i].value()
            value = float(value)/1000
            speed.append(value)
        return speed
    def get_position(self):
        position = []
        for i in range(0, self.num_rows):
            value = self.progressbars[i].value()
            value += self.sliders[i].value()
            value = float(value)/1000
            position.append(value)
        return position
    def set_postion(self):
        for i in range(0, self.num_rows):
            self.change_position_edit(i)
    def set_positions(self,data):
        print len(data)
        for i in range(0, len(data)):
            self.progressbars[i].setValue(data[i]*1000)
            self.positions[i].setText(str(data[i]))

    def reset_position(self, change_index):
        value = 0
        self.progressbars[change_index].setValue(value)

        self.positions[change_index].setText(str(float(value)/1000))
    def reset_postion_all(self):
        for i in  range(0, self.num_rows):
            self.reset_position(i)




class JointStatePublisher():
    def __init__(self):
        self.app = QApplication(sys.argv)
        num_rows = len(config)
        self.gui = JointStatePublisherGui("Joint State Publisher", self, num_rows)
        self.gui.show()
        self.gui.callback_start = self.start
        self.gui.callback_pause = self.pause
        self.gui.callback_reset = self.reset
        self.gui.callback_record = self.record
        self.gui.callback_replay = self.repaly
        self.gui.callback_replay_stop = self.replay_stop
        self.gui.callback_delete = self.delete
        self.gui.callback_debug = self.debug
        self.gui.callback_import = self._import
        self.gui.callback_export = self.export
        self.gui.callback_list_clicked = self.list_clicked
        self.agent = RosLeapOne(self.gui.num_rows)

        self.start_or_pause = False

        self.data_replay = []
        self.replay_flag = False
        self.replay_index = 0
        self.data_last = [0 for x in range(0, 12)]
    def list_clicked(self):
        index = self.gui.get_listVeiw_current_item()
        data_last = [0 for x in range(0, 12)]
        for i in range(0, index):
            data = copy.copy(self.data_replay[i])
            base = data_last
            for i in range(0, len(data)):
                data[i] = float(int((base[i] * 1000)) + int(data[i] * 1000))/1000
            data_last = data
        self.gui.set_positions(data_last)
        pass
    def _import(self):
        print "import"
        array =  pd.read_excel(self.gui.file_path, index_col=[0]).values.tolist()

        if len(self.data_replay) > 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setText("Data is not empty!\n Force clear")
            retval = msg.exec_()
            if retval == QMessageBox.Cancel:
                return
            else:
                self.data_replay = []
                self.gui.listVeiw.clear()

        if isinstance(array,list):
            self.data_replay = array
            for i in range(0, len(self.data_replay)):
                self.gui.listView_add_item(i)

        pass
    def export(self):
        print "export"
        print self.gui.file_path
        self.writer = pd.ExcelWriter(self.gui.file_path)
        df = pd.DataFrame(self.data_replay)
        df.to_excel(self.writer)
        self.writer.save()
        pass
    def debug(self):
        print self.data_replay
    def delete(self):
        print "delete"
        print self.data_replay
        if self.gui.listVeiw_isClicked:
            current_index = self.gui.get_listVeiw_current_item()
            self.data_replay.remove(self.data_replay[current_index])

        print self.data_replay
        pass
    def reset(self):
        print "reset"
        self.agent.reset()
    def replay_stop(self):
        self.replay_flag  = False
        self.data_last = [0 for x in range(0, 12)]
    def repaly(self):
        print "replay"
        if len(self.data_replay) > 0:
            self.replay_flag  = True
    def start(self):
        print "start"
        self.agent.set_callback(self.send_position)

    def pause(self):
        print "pause"
        self.agent.set_callback(None)
    def record(self):
        #data = self.gui.get_position()
        data = self.gui.get_speed()
        if self.gui.listVeiw_isClicked:
            self.gui.listView_inset_item(self.gui.listVeiw_current_item + 1, self.gui.listVeiw_current_item + 1 )
            self.data_replay.insert(self.gui.listVeiw_current_item + 1, data)
            self.gui.listVeiw_current_item += 1
            self.gui.listVeiw.setCurrentRow(self.gui.listVeiw_current_item)
            self.gui.update_listView()
        else:
            self.gui.listView_add_item(len(self.data_replay))
            self.data_replay.append(data)
        pass
    def send_position(self):
        if self.replay_flag:
            data = self.data_replay[self.replay_index]
            data = copy.copy(data)
            #base = self.gui.get_position()
            base = self.data_last
            for i in range(0, len(data)):
                data[i] = float(int((base[i] * 1000)) + int(data[i] * 1000))/1000
            #self.gui.set_positions(data)
            self.data_last = data

            self.replay_index += 1
            self.replay_index = self.replay_index % len(self.data_replay)
            #if self.replay_index >= len(self.data_replay):
            #    print self.data_last
            #    self.data_last = [0 for x in range(0, 12)]
            #    self.gui.set_positions(self.data_last)
            #    self.replay_flag = False
            #    self.replay_index = 0
        else:
            data = self.gui.get_position()
        self.agent.send_position(data)
    def loop(self):
        self.app.exec_()
class RosLeapOne():
    def __init__(self, num_rows=0):
        ### init ros node
        self.node =  rospy.init_node('leap_one_gazebo_control', anonymous=True)
        #self.node =  rospy.init_node('leap_one_gazebo_control','__master="http://192.168.0.91:11311"  __hostname="192.168.0.91""', anonymous=True)
        self.subscriber = rospy.Subscriber('/clock', Clock, self.clock)
        self.pub_list = []

        self.clock_counter = 0
        self.callback = None
        self.num_rows = num_rows

        for i in range(0, num_rows):
            topic_name = config[i][2]
            pub_t = rospy.Publisher(topic_name, Float64, queue_size=64)
            self.pub_list.append(pub_t)

        #### init service
        rospy.wait_for_service('/gazebo/reset_simulation')
        self.f_reset_simulation = rospy.ServiceProxy('/gazebo/reset_simulation', Empty)

    def reset(self):
        self.f_reset_simulation ()

    def set_callback(self, func):
        self.callback = func
    def clock(self, data):
        self.clock_counter += 1
        if (self.clock_counter % 40) == 0:
            if self.callback:
                self.callback()
    def send_position(self, data):
        data_lenth = len(data)
        if self.num_rows == data_lenth:
            index = 0
            for pub in self.pub_list:
                pub.publish(Float64(data[index]))
                index = index + 1

if __name__ == '__main__':
    try:
        jsp = JointStatePublisher()

        jsp.loop()
    except rospy.ROSInterruptException:
        pass
