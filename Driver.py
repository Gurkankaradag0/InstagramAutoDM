from threading import Thread, Lock, Event
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from subprocess import CREATE_NO_WINDOW
from time import gmtime, strftime
import schedule, random, sys

class ChromeDriver:

    DEBUG = True

    stopped = True
    lock = None
    t = None

    browser = None
    user = None
    browserProfile = None

    usernameList = []
    passwordList = []
    userList = []
    sendCount = 0
    sendState = False
    maxSendCount = 0
    prewUser = ""
    message = ""

    def __init__(self, username, password, users, message, maxSend=10):
        self.lock = Lock()
        self._kill = Event()
        self.usernameList = username
        self.passwordList = password
        self.userList = users
        self.message = message
        self.maxSendCount = maxSend
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages':'en,en_US'})
        self.browserProfile.add_argument('--log-level=2')
        self.browserProfile.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.browserProfile.add_experimental_option('useAutomationExtension', False)
        if not self.DEBUG:
            self.browserProfile.add_argument('--window-size=1920,1080')
            self.browserProfile.add_argument('--headless')
            self.chrome_service = ChromeService('chromedriver')
            self.chrome_service.creationflags = CREATE_NO_WINDOW
        else:
            self.browserProfile.add_argument('--start-maximized')

        try:
            a = strftime("%M", gmtime())
            b = int(a)+1
            if len(str(b)) == 1:
                c = ":0%s" %b
            elif b == 60:
                c = ":00"
            else:
                c = ":%s" %b
            schedule.every().hour.at(c).do(self.mainBot)
        except TypeError:
            pass
        
    def getNextAccount(self, acc):
        x = acc
        if x < len(self.usernameList):
            username = self.usernameList[x]
            password = self.passwordList[x]
        else:
            username = -1
            password = -1
        return username, password

    def getNextUserList(self):
        n = []
        if len(self.userList) < self.maxSendCount:
            while len(n) < len(self.userList):
                x = random.randint(0, len(self.userList)-1)
                if x not in n:
                    n.append(x)
        else:
            while len(n) < self.maxSendCount:
                x = random.randint(0, len(self.userList)-1)
                if x not in n:
                    n.append(x)

        randomList = []
        for i in n:
            x = self.userList[i]
            randomList.append(x)

        return randomList

    def clearPrewUser(self, usrList):
        allUserList = self.userList
        
        for user in usrList:
            index = allUserList.index(user)
            allUserList.pop(index)
        
        self.lock.acquire()
        self.userList = allUserList
        self.lock.release()

    def mainBot(self):
        try:
            for i in range(len(self.usernameList)):
                id,pw = self.getNextAccount(i)
                if not id == -1:
                    self.lock.acquire()
                    self.username = id
                    self.password = pw
                    self.lock.release()
                    self.bot()
        except:
            print("Failed")

    def login(self):
        self.browser.get('https://www.instagram.com/accounts/login/')
        is_killed = self._kill.wait(0.075)
        if is_killed:
            sys.exit()
        idpwBarState = False
        while not idpwBarState:
            try:
                usrname_bar = self.browser.find_element_by_name('username')
                passwrd_bar = self.browser.find_element_by_name('password')
                idpwBarState = True
            except:
                idpwBarState = False

        usrname_bar.send_keys(self.username)
        passwrd_bar.send_keys(self.password + Keys.ENTER)

        try:
            myElem = WebDriverWait(self.browser, 6).until(EC.url_to_be('https://www.instagram.com/accounts/onetap/?next=%2F'))
            print("Page is ready!")
            elementExist = "notError"
        except TimeoutException:
            print("Loading took too much time!")

            try:
                alertMessage = self.browser.find_element_by_id("slfErrorAlert")
                if alertMessage.text == "Sorry, your password was incorrect. Please double-check your password.":
                    elementExist = "errorPass"
                else:
                    elementExist = "errorConn"
            except NoSuchElementException:
                elementExist = "notError"

        return elementExist

    def bot(self):
        if not self.DEBUG:
            self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.browserProfile, service=self.chrome_service)
        else:
            self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.browserProfile)
        is_killed = self._kill.wait(0.025)
        if is_killed:
            sys.exit()
        
        while True:
            loginError = self.login()
            if loginError == "errorPass":
                break
            elif loginError == "errorConn":
                self.browser.quit()
                is_killed = self._kill.wait(0.025)
                if is_killed:
                    sys.exit()
                if not self.DEBUG:
                    self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.browserProfile, service=self.chrome_service)
                else:
                    self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.browserProfile)
                is_killed = self._kill.wait(0.025)
                if is_killed:
                    sys.exit()
            else:
                break

        if loginError == "notError":
            userList = self.getNextUserList()
            firstUser = True

            try:
                for usrnamee in userList:
                    self.send_msg(usrnamee,self.message,firstUser)
                    self.lock.acquire()
                    self.sendCount += 1
                    self.sendState = True
                    self.user = usrnamee
                    firstUser = False
                    self.lock.release()
                    is_killed = self._kill.wait(0.20)
                    if is_killed:
                        sys.exit()
                    self.lock.acquire()
                    self.sendState = False
                    self.lock.release()

            except TypeError:
                print('Failed!')

            self.clearPrewUser(userList)
        else:
            print("Sorry, your password was incorrect. Please double-check your password.")
        self.browser.quit()

    def send_msg(self, usrnames, message, existFirstUser):
        self.browser.get('https://www.instagram.com/direct/new/')
        
        if existFirstUser:
            try:
                myElem = WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Not Now']")))
                print("Turn on Notifications")
                myElem.click()
            except TimeoutException:
                print("Loading took too much time! (Turn on Notifications)")
    
        is_killed = self._kill.wait(0.15)
        if is_killed:
            sys.exit()
        toBtnState = False
        while not toBtnState:
            try:
                to_btn = self.browser.find_element_by_name('queryBox')
                toBtnState = True
            except:
                toBtnState = False
        is_killed = self._kill.wait(0.15)
        if is_killed:
            sys.exit()
        to_btn.send_keys(usrnames)
        is_killed = self._kill.wait(5)
        if is_killed:
            sys.exit()
        elementState = False
        while not elementState:
            try:
                elements = self.browser.find_elements_by_xpath("//*[@id]/div/div")
                if len(elements) > 0:
                    is_killed = self._kill.wait(0.15)
                    if is_killed:
                        sys.exit()
                    for element in elements:
                        if element.text == usrnames:
                            element.click()
                            break
                    elementState = True
                else:
                    elementState = False
            except:
                elementState = False
        is_killed = self._kill.wait(0.15)
        if is_killed:
            sys.exit()
        nextBtnState = False
        while not nextBtnState:
            try:
                nxt_btn = self.browser.find_elements_by_xpath('//div[text()="Next"]')
                nextBtnState = True
            except:
                nextBtnState = False
        nxt_btn = nxt_btn[len(nxt_btn)-1]
        nxt_btn.click()
        
        try:
            myElem = WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@placeholder='Message...']")))
            print("Ready to send message")
            myElem.send_keys(message)
        except TimeoutException:
            print("Not ready to send message")
        
        is_killed = self._kill.wait(0.15)
        if is_killed:
            sys.exit()

        sendBtnState = False
        while not sendBtnState:
            try:
                snd_btn = self.browser.find_elements_by_xpath('//button[text()="Send"]')
                sendBtnState = True
            except:
                sendBtnState = False
        snd_btnn = snd_btn[len(snd_btn)-1]
        snd_btnn.click()
        is_killed = self._kill.wait(0.3)
        if is_killed:
            sys.exit()

    def start(self):
        self.stopped = False
        self.t = Thread(target=self.run)
        self.t.start()
    
    def stop(self):
        self.stopped = True
        self.kill()
        self.t.join()

    def alive(self):
        return self.t.isAlive()

    def kill(self):
        self._kill.set()

    def run(self):
        while not self.stopped:
            schedule.run_pending()
            is_killed = self._kill.wait(1)
            if is_killed:
                sys.exit()
        try:
            if self.stopped:
                self.browser.quit()
        except:
            print("Stop")
