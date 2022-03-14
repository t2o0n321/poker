from tkinter import *
from PIL import ImageTk, Image
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

num = []
player = []
host = []
table = []  # Table Card Place
first = []  # Player Card Place
HOST = '127.0.0.1'  # input('Enter host: ')
PORT = 33000  # input('Enter port: ')
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)


class MainWindow:

    def __init__(self, main):
        # put variable
        self.table_card = ['', '', '', '', '']
        self.player_card = ['', '', '', '', '', '', '', '']
        self.table_card_str = ['', '', '', '', '']
        self.player_card_str = ['', '', '', '', '', '', '', '']
        self.player_num = None
        self.banner_var = StringVar()
        # Create background
        self.cv = Canvas(main, bg='lightblue', width=1200, height=800)
        self.rect = self.cv.create_rectangle(200, 200, 1000, 500, fill='green')
        im0 = Image.open('poker\\0.png')
        im0 = im0.resize((118, 177), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(im0)
        # p1~p5 is middle card
        self.p1 = self.cv.create_image(250, 250, anchor='nw', image=self.photo)
        self.p2 = self.cv.create_image(400, 250, anchor='nw', image=self.photo)
        self.p3 = self.cv.create_image(550, 250, anchor='nw', image=self.photo)
        self.p4 = self.cv.create_image(700, 250, anchor='nw', image=self.photo)
        self.p5 = self.cv.create_image(850, 250, anchor='nw', image=self.photo)
        # Down Card
        self.p6 = self.cv.create_image(250, 550, anchor='nw', image=self.photo)
        self.p7 = self.cv.create_image(400, 550, anchor='nw', image=self.photo)
        # Left Card
        self.p8 = self.cv.create_image(50, 150, anchor='nw', image=self.photo)
        self.p9 = self.cv.create_image(50, 350, anchor='nw', image=self.photo)
        # Top Card
        self.p10 = self.cv.create_image(250, 15, anchor='nw', image=self.photo)
        self.p11 = self.cv.create_image(400, 15, anchor='nw', image=self.photo)
        # Right Card
        self.p12 = self.cv.create_image(1050, 80, anchor='nw', image=self.photo)
        self.p13 = self.cv.create_image(1050, 270, anchor='nw', image=self.photo)
        # Button
        self.b1 = Button(win, text="First", command=self.throw, bg='gray')
        self.b1.configure(width=20, height=10, activebackground="#33B5E5", relief=FLAT)
        self.b1_win = self.cv.create_window(600, 600, anchor=NW, window=self.b1)
        # Button Throw
        self.b2 = Button(win, text="Throw", command=self.throw, bg='gray')
        self.b2.configure(width=20, height=10, activebackground="#33B5E5", relief=FLAT)
        self.b2_win = self.cv.create_window(800, 600, anchor=NW, window=self.b2)
        # Button Follow
        self.b3 = Button(win, text="Follow", command=self.follow, bg='gray')
        self.b3.configure(width=20, height=10, activebackground="#33B5E5", relief=FLAT)
        self.b3_win = self.cv.create_window(1000, 600, anchor=NW, window=self.b3)
        # Label of player1 (down)
        self.l2 = Label(win, text='Player0 →', bg='white', font=('Arial', 12), width=15, height=2)
        self.l2.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l2_win = self.cv.create_window(70, 580, anchor=NW, window=self.l2)
        # Label of player2 (left)
        self.l4 = Label(win, text='Player1 ↓', bg='white', font=('Arial', 12), width=15, height=2)
        self.l4.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l4_win = self.cv.create_window(50, 20, anchor=NW, window=self.l4)
        # Label of player3 (top)
        self.l6 = Label(win, text='Player2 ←', bg='white', font=('Arial', 12), width=15, height=2)
        self.l6.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l6_win = self.cv.create_window(550, 40, anchor=NW, window=self.l6)
        # Label of player3 (right)
        self.l8 = Label(win, text='Player3 ↑', bg='white', font=('Arial', 12), width=15, height=2)
        self.l8.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l8_win = self.cv.create_window(1052, 460, anchor=NW, window=self.l8)
        # create banner
        self.l9 = Label(win, textvariable=self.banner_var, bg='white', font=('Arial', 12), width=15, height=2)
        self.l9.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l9_win = self.cv.create_window(900, 70, anchor=NW, window=self.l9)
        self.cv.pack()
        receive_thread = Thread(target=self.receive)
        receive_thread.start()

    @staticmethod
    def throw():
        client_socket.send(bytes("throw", "utf8"))

    @staticmethod
    def follow():
        client_socket.send(bytes("follow", "utf8"))

    def receive(self):
        """Handles receiving of messages."""
        while True:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            print(msg)
            if msg[:9] == 'Server:T/':
                msg = self.cut_string(msg)
                card = msg.split(':')
                card[0] = card[0].split(',')
                card[1] = card[1].split(',')
                self.table_card[:3] = card[0][:3]
                self.player_card = card[1]
                self.table_card_str[:3] = self.int_to_string(self.table_card[:3])
                self.player_card_str = self.int_to_string(self.player_card)
                print(self.table_card_str)
                print(self.player_card_str)
                self.first_round()
            elif msg[:9] == 'Server:T3':
                msg = self.cut_string(msg)
                msg = msg[1:]
                self.table_card[3] = msg
                self.table_card_str[3:4] = self.int_to_string(self.table_card[3:4])
                self.second_round()
            elif msg[:9] == 'Server:T4':
                msg = self.cut_string(msg)
                msg = msg[1:]
                self.table_card[4] = msg
                self.table_card_str[4:5] = self.int_to_string(self.table_card[4:5])
                self.third_round()
            elif msg[:9] == 'Server:O/':
                self.player_num = int(msg[9])
                self.banner_var.set('I\'m Player%s' % self.player_num)

            # msg_list.insert(tkinter.END, msg)

    def first_round(self):
        global photo1, photo2, photo3, photod, photol, photot, photor, photod1, photol1, photot1, photor1
        # image1
        im1 = Image.open(self.table_card_str[0])
        im1 = im1.resize((118, 177), Image.ANTIALIAS)
        photo1 = ImageTk.PhotoImage(im1)
        # image2
        im2 = Image.open(self.table_card_str[1])
        im2 = im2.resize((118, 177), Image.ANTIALIAS)
        photo2 = ImageTk.PhotoImage(im2)
        # image3
        im3 = Image.open(self.table_card_str[2])
        im3 = im3.resize((118, 177), Image.ANTIALIAS)
        photo3 = ImageTk.PhotoImage(im3)
        # Show Table Card
        self.cv.itemconfigure(self.p1, image=photo1)
        self.cv.itemconfigure(self.p2, image=photo2)
        self.cv.itemconfigure(self.p3, image=photo3)
        self.cv.itemconfigure(self.p4, image=self.photo)
        self.cv.itemconfigure(self.p5, image=self.photo)
        # image down
        imd = Image.open(self.player_card_str[0])
        imd = imd.resize((118, 177), Image.ANTIALIAS)
        photod = ImageTk.PhotoImage(imd)
        imd1 = Image.open(self.player_card_str[1])
        imd1 = imd1.resize((118, 177), Image.ANTIALIAS)
        photod1 = ImageTk.PhotoImage(imd1)
        # image left
        iml = Image.open(self.player_card_str[2])
        iml = iml.resize((118, 177), Image.ANTIALIAS)
        photol = ImageTk.PhotoImage(iml)
        iml1 = Image.open(self.player_card_str[3])
        iml1 = iml1.resize((118, 177), Image.ANTIALIAS)
        photol1 = ImageTk.PhotoImage(iml1)
        # image top
        imt = Image.open(self.player_card_str[4])
        imt = imt.resize((118, 177), Image.ANTIALIAS)
        photot = ImageTk.PhotoImage(imt)
        imt1 = Image.open(self.player_card_str[5])
        imt1 = imt1.resize((118, 177), Image.ANTIALIAS)
        photot1 = ImageTk.PhotoImage(imt1)
        # image right
        imr = Image.open(self.player_card_str[6])
        imr = imr.resize((118, 177), Image.ANTIALIAS)
        photor = ImageTk.PhotoImage(imr)
        imr1 = Image.open(self.player_card_str[7])
        imr1 = imr1.resize((118, 177), Image.ANTIALIAS)
        photor1 = ImageTk.PhotoImage(imr1)
        # Show Table Card
        self.cv.itemconfigure(self.p6, image=photod)
        self.cv.itemconfigure(self.p7, image=photod1)
        self.cv.itemconfigure(self.p8, image=photol)
        self.cv.itemconfigure(self.p9, image=photol1)
        self.cv.itemconfigure(self.p10, image=photot)
        self.cv.itemconfigure(self.p11, image=photot1)
        self.cv.itemconfigure(self.p12, image=photor)
        self.cv.itemconfigure(self.p13, image=photor1)

    def second_round(self):
        global photo4
        # image4
        im = Image.open(self.table_card_str[3])
        im = im.resize((118, 177), Image.ANTIALIAS)
        photo4 = ImageTk.PhotoImage(im)
        self.cv.itemconfigure(self.p4, image=photo4)

    def third_round(self):
        global photo5
        # image4
        im = Image.open(self.table_card_str[4])
        im = im.resize((118, 177), Image.ANTIALIAS)
        photo5 = ImageTk.PhotoImage(im)
        self.cv.itemconfigure(self.p5, image=photo5)

    @staticmethod
    def cut_string(message):
        message = message.replace('Server:T', '')
        message = message.replace('/', '')
        message = message.replace('P', '')
        message = message.replace('\'', '')
        message = message.replace('[', '')
        message = message.replace(']', '')
        message = message.replace(' ', '')
        return message

    @staticmethod
    def int_to_string(number):
        for i in range(0, len(number)):
            number[i] = 'poker\\' + number[i] + '.png'
        return number

    @staticmethod
    def on_closing():
        """This function is to be called when the window is closed."""
        client_socket.send(bytes("{quit}", "utf8"))


win = Tk()
win.geometry('1200x800')
MainWindow(win)
win.mainloop()





