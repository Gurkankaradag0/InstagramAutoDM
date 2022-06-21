from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json, os
from time import sleep

from main import Ui_MainWindow
from AccountAdd import Ui_mw_AddAccount
from AboutMe import Ui_mw_AboutMe

from Driver import ChromeDriver
from DriverGetAcc import ChromeDriverGetAccount

import webbrowser

class AutoDM(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.AddAccountPage = QMainWindow()
        self.Aui = Ui_mw_AddAccount()
        self.Aui.setupUi(self.AddAccountPage)

        self.AboutMePage = QMainWindow()
        self.Abui = Ui_mw_AboutMe()
        self.Abui.setupUi(self.AboutMePage)

        self.SaveDirName = "AutoDM"
        self.AutoDMJson = "AutoDM.json"
        self.AccountJson = "Accounts.json"
        self.AppDataDir = os.getenv('APPDATA')
        self.SaveDir = self.AppDataDir+"\\"+self.SaveDirName
        self.AutoDMLayout = {}
        self.AccountsLayout = {}

        self.SaveJson = None

        self.startWatch = False
        self.counter = 0
        self.hour = "00"
        self.minute = "00"
        self.second = "00"
        self.count = "00"
        self.userNameList = []
        self.passwordList = []
        self.userList = []
        self.message = ""
        self.sendUserCount = 0

        self.Load()
        self.ActionButton()

        self.timer_ms = 500
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.AccountsPageCloseEvent)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showCounter)
        self.timer.start(100)

        self.timerUser = QTimer(self)
        self.timerUser.timeout.connect(self.refreshUserState)

        self.timerCheckUserCount = QTimer(self)
        self.timerCheckUserCount.timeout.connect(self.checkUserCount)

        self.timerCheckAccounts = QTimer(self)
        self.timerCheckAccounts.timeout.connect(self.checkAccounts)

        self.timerCheckErrors = QTimer(self)
        self.timerCheckErrors.timeout.connect(self.checkErrors)

        self.Driver = None
        self.DriverGetAcc = None

    def GetAccountsPage(self):
        self.AddAccountPage.show()
        self.SaveJson = "AccountsPage"
        self.Load("AccountsPage")
        self.timer2.start(self.timer_ms)

    def GetAboutMePage(self):
        self.AboutMePage.show()

    def AccountsPageCloseEvent(self):
        if not self.AddAccountPage.isVisible():
            self.SaveJson = None
            self.timer2.stop()

    def Load(self, LoadJson=None):
        if LoadJson == None:
            if not os.path.isdir(self.SaveDir):
                os.mkdir(self.SaveDir)
                with open(self.SaveDir+"\\"+self.AutoDMJson, "w") as json_data:
                    json.dump(self.AutoDMLayout, json_data, indent=4)

            else:
                self.ui.tableWidget.clear()
                self.ui.tableWidget.setHorizontalHeaderLabels(["ID","State"])
                self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
                if not os.path.exists(self.SaveDir+"\\"+self.AutoDMJson):
                    with open(self.SaveDir+"\\"+self.AutoDMJson, "w") as json_data:
                        json.dump(self.AutoDMLayout, json_data, indent=4)
                else:
                    with open(self.SaveDir+"\\"+self.AutoDMJson,"r") as json_data:
                        self.AutoDMLayout = json.load(json_data)

                    if "Accounts" in self.AutoDMLayout:
                        userCount = len(self.AutoDMLayout["Accounts"])
                        sendUserCount = 0
                        self.ui.lbl_Count.setText(str(userCount))
                        for i in self.AutoDMLayout["Accounts"]:
                            rowPosition = self.ui.tableWidget.rowCount()
                            user = self.AutoDMLayout["Accounts"][str(i)]
                            self.ui.tableWidget.insertRow(rowPosition)
                            self.ui.tableWidget.setItem(rowPosition , 0, QTableWidgetItem(user["ID"]))
                            self.ui.tableWidget.setItem(rowPosition , 1, QTableWidgetItem(user["State"]))
                            if user["State"] == "True":
                                sendUserCount += 1
                        self.ui.lbl_TrueCount.setText(str(sendUserCount))
                    else:
                        self.ui.lbl_Count.setText("0")
                        self.ui.lbl_TrueCount.setText("0")

                    if "Settings" in self.AutoDMLayout:
                        if "Message" in self.AutoDMLayout["Settings"]:
                            message = self.AutoDMLayout["Settings"]["Message"]
                            self.ui.te_Message.setPlainText(message)
                        else:
                            self.ui.te_Message.clear()

                        if "SendCount" in self.AutoDMLayout["Settings"]:
                            sendCount = self.AutoDMLayout["Settings"]["SendCount"]
                            self.ui.sb_maxSend.setValue(int(sendCount))
                        else:
                            self.ui.sb_maxSend.setValue(10)
        else:
            self.Aui.listWidget.clear()
            if not os.path.isdir(self.SaveDir):
                os.mkdir(self.SaveDir)
                with open(self.SaveDir+"\\"+self.AccountJson, "w") as json_data:
                    json.dump(self.AccountsLayout, json_data, indent=4)

            else:

                if not os.path.exists(self.SaveDir+"\\"+self.AccountJson):
                    with open(self.SaveDir+"\\"+self.AccountJson, "w") as json_data:
                        json.dump(self.AccountsLayout, json_data, indent=4)
                else:
                    with open(self.SaveDir+"\\"+self.AccountJson,"r") as json_data:
                        self.AccountsLayout = json.load(json_data)

                    if "Accounts" in self.AccountsLayout:
                        for i in self.AccountsLayout["Accounts"]:
                            username = self.AccountsLayout["Accounts"][str(i)]["ID"]
                            password = self.AccountsLayout["Accounts"][str(i)]["PW"]
                            item = QListWidgetItem()
                            item.setText(username)
                            item.setWhatsThis(password)
                            self.Aui.listWidget.addItem(item)

    def Save(self, SaveJson=None):
        if SaveJson == None:
            if self.ui.pb_Save.property("pb_State"):
                self.AutoDMLayout.clear()
                self.AutoDMLayout["Settings"] = {}
                if self.ui.te_Message.toPlainText() != "":
                    message = self.ui.te_Message.toPlainText()
                    self.AutoDMLayout["Settings"]["Message"] = message
                sendCount = self.ui.sb_maxSend.value()
                self.AutoDMLayout["Settings"]["SendCount"] = sendCount
                self.AutoDMLayout["Accounts"] = {}
                twCount = self.ui.tableWidget.rowCount()
                if twCount > 0:
                    for x in range(twCount):
                        ID = self.ui.tableWidget.item(x, 0).text()
                        State = self.ui.tableWidget.item(x, 1).text()
                        self.AutoDMLayout["Accounts"][str(x)] = {}
                        self.AutoDMLayout["Accounts"][str(x)]["ID"] = ID
                        self.AutoDMLayout["Accounts"][str(x)]["State"] = State
                with open(self.SaveDir+"\\"+self.AutoDMJson, "w") as json_data:
                    json.dump(self.AutoDMLayout, json_data, indent=4)
            else:
                self.CreateMessageBox("Şuan bunu yapamazsın...", QMessageBox.Ok)
        else:
            self.AccountsLayout.clear()
            self.AccountsLayout["Accounts"] = {}
            lwCount = self.Aui.listWidget.count()
            for x in range(lwCount):
                username = self.Aui.listWidget.item(x).text()
                password = self.Aui.listWidget.item(x).whatsThis()
                self.AccountsLayout["Accounts"][str(x)] = {}
                self.AccountsLayout["Accounts"][str(x)]["ID"] = username
                self.AccountsLayout["Accounts"][str(x)]["PW"] = password

            with open(self.SaveDir+"\\"+self.AccountJson, "w") as json_data:
                json.dump(self.AccountsLayout, json_data, indent=4)

    def ActionButton(self):
        button_action = QAction("Accounts", self)
        button_action.triggered.connect(self.GetAccountsPage)
        self.ui.toolBar.addAction(button_action)

        button_action = QAction("About Me", self)
        button_action.triggered.connect(self.GetAboutMePage)
        self.ui.toolBar.addAction(button_action)

        self.ui.pb_BotState.setProperty("pb_State", True)
        self.ui.pb_ClearTable.setProperty("pb_State", True)
        self.ui.pb_Save.setProperty("pb_State", True)
        self.ui.pb_GetAccounts.setProperty("pb_State", True)
        self.ui.pb_BotState.clicked.connect(self.GetBotState)
        self.Aui.pb_Add.clicked.connect(self.AddAccount)
        self.Aui.pb_Delete.clicked.connect(self.DelAccount)
        self.ui.pb_GetAccounts.clicked.connect(self.GetAccounts)
        self.ui.pb_ClearTable.clicked.connect(self.ClearTable)
        self.ui.pb_Save.clicked.connect(lambda: self.Save())
        self.Abui.label.mousePressEvent = self.goLink

    def goLink(self, event):
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open('https://github.com/Gurkankaradag0')

    def ClearTable(self):
        if self.ui.pb_ClearTable.property("pb_State"):
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setHorizontalHeaderLabels(["ID","State"])
            self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.tableWidget.setRowCount(0)
            self.sendUserCount = 0
            self.ui.lbl_TrueCount.setText(str(0))
            self.Save()
        else:
            self.CreateMessageBox("You can't do this right now...", QMessageBox.Ok)

    def AddAccount(self):
        username = self.Aui.le_UserName.text()
        password = self.Aui.le_Password.text()

        if username != "" and password != "":
            item = QListWidgetItem()
            item.setText(username)
            item.setWhatsThis(password)
            self.Aui.listWidget.addItem(item)
            self.Save(self.SaveJson)
            self.Aui.le_UserName.clear()
            self.Aui.le_Password.clear()

    def DelAccount(self):
        ItemSelect = list(self.Aui.listWidget.selectedItems())
        if len(ItemSelect) != 0:
            for SelectedItem in ItemSelect:
                self.Aui.listWidget.takeItem(self.Aui.listWidget.row(SelectedItem))
                self.Save(self.SaveJson)

    def GetBotState(self):
        if self.ui.pb_BotState.property("pb_State"):
            if self.ui.pb_BotState.isChecked():
                self.TimerStart()
                self.Start()
            else:
                self.TimerStop()
                self.Stop()
        else:
            self.ui.pb_BotState.setChecked(False)
            self.CreateMessageBox("You can't do this right now...", QMessageBox.Ok)

    def showCounter(self):
        if self.startWatch:
            self.counter += 1
            cnt = int((self.counter/10 - int(self.counter/10))*10)
            self.count = '0' + str(cnt)

            if int(self.counter/10) < 10 :
                self.second = '0' + str(int(self.counter / 10))
            else:
                self.second = str(int(self.counter / 10))
                if self.counter / 10 == 60.0 :
                    self.second == '00'
                    self.counter = 0
                    min = int(self.minute) + 1
                    if min < 10 :
                        self.minute = '0' + str(min)
                    else:
                        if min == 60:
                            self.minute = '00'
                            hour = int(self.hour) + 1
                            if hour < 10:
                                self.hour = '0' + str(hour)
                            else:
                                self.hour = str(hour)
                        else:
                            self.minute = str(min)

        text = self.hour + ':' + self.minute + ':' + self.second
        self.ui.lbl_StartTime.setText(text)

    def TimerStart(self):
        self.ui.pb_BotState.setText("Stop")
        self.startWatch = True

    def TimerStop(self):
        self.ui.pb_BotState.setText("Start")
        self.startWatch = False
        self.counter = 0
        self.hour = "00"
        self.minute = "00"
        self.second = "00"
        self.count = "00"
        self.ui.lbl_StartTime.setText(str(self.counter))

    def GetAccounts(self):
        if self.ui.pb_GetAccounts.property("pb_State"):
            url = self.ui.le_PostLink.text()
            if url != "":
                if not os.path.isdir(self.SaveDir):
                    self.CreateMessageBox("Please add account from the 'Accounts' tab...", QMessageBox.Ok)
                else:
                    if not os.path.exists(self.SaveDir+"\\"+self.AccountJson):
                        self.CreateMessageBox("Please add account from the 'Accounts' tab...", QMessageBox.Ok)
                    else:
                        with open(self.SaveDir+"\\"+self.AccountJson,"r") as json_data:
                            self.AccountsLayout = json.load(json_data)

                        if "Accounts" in self.AccountsLayout:
                            if len(self.AccountsLayout["Accounts"]) > 0:
                                username = self.AccountsLayout["Accounts"]["0"]["ID"]
                                password = self.AccountsLayout["Accounts"]["0"]["PW"]
                                
                                ret = self.CreateMessageBox("This process can take a long time...\nAre you sure you want to continue?")
                                if ret == 1024:
                                    self.DriverGetAcc = ChromeDriverGetAccount(username, password, url)
                                    self.DriverGetAcc.start()
                                    self.ui.pb_BotState.setProperty("pb_State", False)
                                    self.ui.pb_ClearTable.setProperty("pb_State", False)
                                    self.ui.pb_Save.setProperty("pb_State", False)
                                    self.ui.pb_GetAccounts.setProperty("pb_State", False)
                                    self.timerCheckAccounts.start(100)
                                    self.timerCheckErrors.start(100)
                        else:
                            self.CreateMessageBox("Please add account from the 'Accounts' tab...", QMessageBox.Ok)
            else:
                self.CreateMessageBox("Please do not leave the 'Post URL' part blank...", QMessageBox.Ok)
        else:
            self.CreateMessageBox("You can't do this right now...", QMessageBox.Ok)

    def GetAccountsOk(self, userList, finishTime):
        users = userList
        self.ClearTable()
        for user in users:
            rowPosition = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rowPosition)
            self.ui.tableWidget.setItem(rowPosition , 0, QTableWidgetItem(user))
            self.ui.tableWidget.setItem(rowPosition , 1, QTableWidgetItem("False"))

        rowCount = self.ui.tableWidget.rowCount()
        if rowCount > 0:
            self.ui.lbl_Count.setText(str(rowCount))
        else:
            self.ui.lbl_Count.setText("0")
        
        self.CreateMessageBox("{}".format(rowCount)+" Accounts were taken in {} seconds.".format(int(finishTime)), QMessageBox.Ok)
        self.Save()
            
    def CreateMessageBox(self, message, buttons=(QMessageBox.Ok | QMessageBox.Cancel)):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("WARNING")
        msg.setStandardButtons(buttons)
        retval = msg.exec_()
        return retval

    def refreshUserState(self):
        if not self.Driver.user is None:
            if self.Driver.sendState:
                for i in range(1):
                    text = self.ui.lbl_TrueCount.text()
                    text = int(text)
                    text += 1
                    self.ui.lbl_TrueCount.setText(str(text))

                    user = self.Driver.user
                    rowCount = self.ui.tableWidget.rowCount()
                    for i in range(rowCount):
                        itemText = self.ui.tableWidget.item(i,0).text()
                        if itemText == user:
                            userIndex = i
                            break
                    self.ui.tableWidget.item(userIndex,1).setText("True")
                    self.Save()

    def checkAccounts(self):
        if self.DriverGetAcc.getState:
            self.ui.pb_BotState.setProperty("pb_State", True)
            self.ui.pb_ClearTable.setProperty("pb_State", True)
            self.ui.pb_Save.setProperty("pb_State", True)
            self.ui.pb_GetAccounts.setProperty("pb_State", True)
            userList = self.DriverGetAcc.userList
            finishTime = self.DriverGetAcc.finishTime
            self.DriverGetAcc.resetSelfs()
            sleep(0.05)
            self.GetAccountsOk(userList, finishTime)

    def checkErrors(self):
        if self.DriverGetAcc.errorMessageState:
            self.ui.pb_BotState.setProperty("pb_State", True)
            self.ui.pb_ClearTable.setProperty("pb_State", True)
            self.ui.pb_Save.setProperty("pb_State", True)
            self.ui.pb_GetAccounts.setProperty("pb_State", True)
            errorMessage = self.DriverGetAcc.errorMessage
            self.DriverGetAcc.resetSelfs()
            sleep(0.05)
            self.CreateMessageBox(errorMessage, QMessageBox.Ok)

    def checkUserCount(self):
        tableRowCount = self.ui.lbl_Count.text()
        sendCount = self.ui.lbl_TrueCount.text()
        if int(tableRowCount) == int(sendCount):
            self.Stop()
            self.CreateMessageBox("A message has been sent to all users in the table.\nPlease refresh the table...", QMessageBox.Ok)
            self.timerCheckUserCount.stop()
            self.TimerStop()
            self.ui.pb_BotState.setCheckable(False)

    def getLists(self):
        #Get Message
        self.message = self.ui.te_Message.toPlainText()

        #Get UserList
        if not os.path.isdir(self.SaveDir):
            return False
        else:
            if not os.path.exists(self.SaveDir+"\\"+self.AutoDMJson):
                return False
            else:
                with open(self.SaveDir+"\\"+self.AutoDMJson,"r") as json_data:
                    self.AutoDMLayout = json.load(json_data)

                userList = []
                if "Accounts" in self.AutoDMLayout:
                    for i in self.AutoDMLayout["Accounts"]:
                        if self.AutoDMLayout["Accounts"][str(i)]["State"] == "False":
                            user = self.AutoDMLayout["Accounts"][str(i)]["ID"]
                            userList.append(user)

                self.userList = userList

        #Get UserNames and PassWords
        if not os.path.isdir(self.SaveDir):
            return False
        else:
            if not os.path.exists(self.SaveDir+"\\"+self.AccountJson):
                return False
            else:
                with open(self.SaveDir+"\\"+self.AccountJson,"r") as json_data:
                    self.AccountsLayout = json.load(json_data)

                userNameList = []
                passWordList = []
                if "Accounts" in self.AccountsLayout:
                    for i in self.AccountsLayout["Accounts"]:
                        username = self.AccountsLayout["Accounts"][str(i)]["ID"]
                        password = self.AccountsLayout["Accounts"][str(i)]["PW"]
                        userNameList.append(username)
                        passWordList.append(password)

                self.userNameList = userNameList
                self.passwordList = passWordList
                
        return True

    def Start(self):
        if self.ui.pb_BotState.property("pb_State"):
            self.Save()
            a = self.getLists()
            tableRowCount = self.ui.lbl_Count.text()
            sendCount = self.ui.lbl_TrueCount.text()
            maxCount = self.ui.sb_maxSend.value()
            if a and int(tableRowCount) != int(sendCount):
                self.Driver = ChromeDriver(self.userNameList, self.passwordList, self.userList, self.message, maxCount)
                self.Driver.start()
                self.sendUserCount = 0
                self.timerUser.start(200)
                self.timerCheckUserCount.start(100)
            else:
                self.CreateMessageBox("Update the table...", QMessageBox.Ok)

    def Stop(self):
        self.timerUser.stop()
        self.timerCheckUserCount.stop()
        self.Driver.stop()
        
    def closeEvent(self, event):
        self.timer.stop()
        self.timer2.stop()
        self.timerCheckAccounts.stop()
        self.timerCheckErrors.stop()
        self.timerCheckUserCount.stop()
        self.timerUser.stop()
        try:
            self.AddAccountPage.close()
        except:
            pass
        try:
            self.AboutMePage.close()
        except:
            pass
        try:
            self.Driver.stop()
        except:
            pass
        try:
            self.DriverGetAcc.stop()
        except:
            pass

def main():
	app = QApplication([])
	app.setStyle("Vista")
	ui = AutoDM()
	ui.show()
	app.exec_()

if __name__ == '__main__':
    main()