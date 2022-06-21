from threading import Thread, Lock
import instaloader
from instaloader.exceptions import BadCredentialsException, ConnectionException, BadResponseException
from time import sleep, time

class ChromeDriverGetAccount:

    stopped = True
    lock = None
    t = None

    browser = None

    username = ""
    password = ""
    url = ""
    userList = []
    getState = False
    errorMessageState = False
    errorMessage = ""
    finishTime = 0

    def __init__(self, username, password, url):
        self.lock = Lock()
        self.username = username
        self.password = password
        self.url = url
        self.timer = time()

    def resetSelfs(self):
        self.lock.acquire()
        self.errorMessageState = False
        self.getState = False
        self.lock.release()

    def bot(self):
        self.browser = instaloader.Instaloader()
        try:
            self.browser.login(user=self.username, passwd=self.password)
            shortcode = self.url
            try:
                shortcode = shortcode.split("/")
                if shortcode[-1] == "":
                    shortcode = shortcode[-2]
                else:
                    shortcode = shortcode[-1]
            except:
                pass
            try:
                Post = instaloader.Post.from_shortcode(self.browser.context, shortcode)
            except BadResponseException as badRes:
                print(f"{badRes}")
                self.lock.acquire()
                self.errorMessageState = True
                self.errorMessage = "Lütfen urlyi düzeltiniz..."
                self.lock.release()
            users = []
            for like in Post.get_likes():
                if self.stopped:
                    break
                if like not in users:
                    try:
                        like_ = str(like).split(" ")[1]
                    except:
                        like_ = str(like)
                    users.append(like_)

            sn = time() - self.timer
            self.lock.acquire()
            self.getState = True
            self.userList = users
            self.finishTime = sn
            self.lock.release()
        except ConnectionException as con:
            print(f"{con}")
            self.lock.acquire()
            self.errorMessageState = True
            self.errorMessage = "Giriş başarısız..\nLütfen tekrar deneyiniz..."
            self.lock.release()
        except BadCredentialsException as bad:
            print(f"{bad}")
            self.lock.acquire()
            self.errorMessageState = True
            self.errorMessage = "Kullanıcı adı ve/veya Şifre Hatalı.."
            self.lock.release()

    def start(self):
        self.stopped = False
        self.t = Thread(target=self.run)
        self.t.start()
    
    def stop(self):
        self.stopped = True
        self.t.join()

    def run(self):
        if not self.stopped:
            self.bot()
