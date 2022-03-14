"""Server for multithreaded (asynchronous) chat application."""
import time
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from tkinter import *
from PIL import ImageTk, Image
from deuces import Card, Evaluator, Deck
import scipy.stats as ss
# create an evaluator
evaluator = Evaluator()

clients = {}
addresses = {}
HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)


class MainWindow:

    def __init__(self, main):
        connect_thread = Thread(target=self.connect)
        connect_thread.start()
        # variables
        self.num_player = 0
        self.board = [0, 0, 0, 0, 0]
        self.player = [[0, 0], [0, 0], [0, 0], [0, 0]]
        # where card puts
        self.board_card_str = ['', '', '', '', '']
        self.player_card_str = [['', ''], ['', ''], ['', ''], ['', '']]
        self.coins = [1000, 1000, 1000, 1000]
        self.lead = 3  # To let lead % 4 at the first time can be zero
        self.player_str = ['', '', '', '']
        self.player_flag = [1, 1, 1, 1]
        self.player_var = []
        self.banner_var = StringVar()
        self.thread = Thread(target=self.banner_for_turn)
        self.turn = 0
        self.rank = [0, 0, 0, 0]
        # initial sequence
        self.seq = [1, 2, 3, 4]
        self.turns = 0
        self.collect = 0
        for i in range(0, 4):
            self.player_var.append(StringVar())
        # player score
        self.p_score = [0, 0, 0, 0]
        self.percent = [0, 0, 0, 0]
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
        # Button First
        self.b1 = Button(win, text="First", command=self.first_round, bg='gray')
        self.b1.configure(width=20, height=10, activebackground="#33B5E5", relief=FLAT)
        self.b1_win = self.cv.create_window(600, 600, anchor=NW, window=self.b1)
        # Button Second
        self.b2 = Button(win, text="Second", command=self.second_round, bg='gray')
        self.b2.configure(width=20, height=10, activebackground="#33B5E5", relief=FLAT)
        self.b2_win = self.cv.create_window(800, 600, anchor=NW, window=self.b2)
        # Button Third
        self.b3 = Button(win, text="Third", command=self.third_round, bg='gray')
        self.b3.configure(width=20, height=10, activebackground="#33B5E5", relief=FLAT)
        self.b3_win = self.cv.create_window(1000, 600, anchor=NW, window=self.b3)
        # Button Fill Money
        self.b4 = Button(win, text="Fill Money", command=self.fill_money, bg='gray')
        self.b4.configure(width=20, height=10, activebackground="#33B5E5", relief=FLAT)
        self.b4_win = self.cv.create_window(700, 20, anchor=NW, window=self.b4)
        # Label of player1 (down)
        self.l1 = Label(win, textvariable=self.player_var[0], bg='white', font=('Arial', 12), width=15, height=2)
        self.l1.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l1_win = self.cv.create_window(70, 640, anchor=NW, window=self.l1)
        self.l2 = Label(win, text='Player0 →', bg='white', font=('Arial', 12), width=15, height=2)
        self.l2.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l2_win = self.cv.create_window(70, 580, anchor=NW, window=self.l2)
        # Label of player2 (left)
        self.l3 = Label(win, textvariable=self.player_var[1], bg='white', font=('Arial', 12), width=15, height=2)
        self.l3.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l3_win = self.cv.create_window(50, 80, anchor=NW, window=self.l3)
        self.l4 = Label(win, text='Player1 ↓', bg='white', font=('Arial', 12), width=15, height=2)
        self.l4.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l4_win = self.cv.create_window(50, 20, anchor=NW, window=self.l4)
        # Label of player3 (top)
        self.l5 = Label(win, textvariable=self.player_var[2], bg='white', font=('Arial', 12), width=15, height=2)
        self.l5.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l5_win = self.cv.create_window(550, 100, anchor=NW, window=self.l5)
        self.l6 = Label(win, text='Player2 ←', bg='white', font=('Arial', 12), width=15, height=2)
        self.l6.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l6_win = self.cv.create_window(550, 40, anchor=NW, window=self.l6)
        # Label of player3 (right)
        self.l7 = Label(win, textvariable=self.player_var[3], bg='white', font=('Arial', 12), width=15, height=2)
        self.l7.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l7_win = self.cv.create_window(1052, 520, anchor=NW, window=self.l7)
        self.l8 = Label(win, text='Player3 ↑', bg='white', font=('Arial', 12), width=15, height=2)
        self.l8.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l8_win = self.cv.create_window(1052, 460, anchor=NW, window=self.l8)
        # create banner
        self.l9 = Label(win, textvariable=self.banner_var, bg='white', font=('Arial', 12), width=15, height=2)
        self.l9.configure(width=12, height=3, activebackground="#33B5E5", relief=FLAT)
        self.l9_win = self.cv.create_window(900, 70, anchor=NW, window=self.l9)
        self.cv.pack()

    def first_round(self):
        self.new()
        self.board = self.int_to_string(board)
        self.player[0] = self.int_to_string(player1_hand)
        self.player[1] = self.int_to_string(player2_hand)
        self.player[2] = self.int_to_string(player3_hand)
        self.player[3] = self.int_to_string(player4_hand)
        # Send to All Player
        msg = ('T/' + str(self.board[0:3]) + ':P/' + str(self.player)).encode('utf-8')
        print(msg)
        self.broadcast(msg, "Server:")
        self.board_card_str = self.string_to_place(self.board)
        for i in range(0, 4):
            self.player_card_str[i] = self.string_to_place(self.player[i])
        global photo1, photo2, photo3, photod, photol, photot, photor, photod1, photol1, photot1, photor1
        # image1
        im1 = Image.open(self.board_card_str[0])
        im1 = im1.resize((118, 177), Image.ANTIALIAS)
        photo1 = ImageTk.PhotoImage(im1)
        # image2
        im2 = Image.open(self.board_card_str[1])
        im2 = im2.resize((118, 177), Image.ANTIALIAS)
        photo2 = ImageTk.PhotoImage(im2)
        # image3
        im3 = Image.open(self.board_card_str[2])
        im3 = im3.resize((118, 177), Image.ANTIALIAS)
        photo3 = ImageTk.PhotoImage(im3)
        # Show Table Card
        self.cv.itemconfigure(self.p1, image=photo1)
        self.cv.itemconfigure(self.p2, image=photo2)
        self.cv.itemconfigure(self.p3, image=photo3)
        self.cv.itemconfigure(self.p4, image=self.photo)
        self.cv.itemconfigure(self.p5, image=self.photo)
        # image down
        imd = Image.open(self.player_card_str[0][0])
        imd = imd.resize((118, 177), Image.ANTIALIAS)
        photod = ImageTk.PhotoImage(imd)
        imd1 = Image.open(self.player_card_str[0][1])
        imd1 = imd1.resize((118, 177), Image.ANTIALIAS)
        photod1 = ImageTk.PhotoImage(imd1)
        # image left
        iml = Image.open(self.player_card_str[1][0])
        iml = iml.resize((118, 177), Image.ANTIALIAS)
        photol = ImageTk.PhotoImage(iml)
        iml1 = Image.open(self.player_card_str[1][1])
        iml1 = iml1.resize((118, 177), Image.ANTIALIAS)
        photol1 = ImageTk.PhotoImage(iml1)
        # image top
        imt = Image.open(self.player_card_str[2][0])
        imt = imt.resize((118, 177), Image.ANTIALIAS)
        photot = ImageTk.PhotoImage(imt)
        imt1 = Image.open(self.player_card_str[2][1])
        imt1 = imt1.resize((118, 177), Image.ANTIALIAS)
        photot1 = ImageTk.PhotoImage(imt1)
        # image right
        imr = Image.open(self.player_card_str[3][0])
        imr = imr.resize((118, 177), Image.ANTIALIAS)
        photor = ImageTk.PhotoImage(imr)
        imr1 = Image.open(self.player_card_str[3][1])
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
        # Money in the pocket
        self.collect = 0
        self.lead_the_play()
        self.reset_str()
        # Set the round
        self.turn = 1
        self.turns = 1
        self.thread.start()

    def second_round(self):
        global photo4
        # Send to All Player
        msg = ('T3/' + str(self.board[3:4])).encode('utf-8')
        self.broadcast(msg, "Server:")
        # image4
        im = Image.open(self.board_card_str[3])
        im = im.resize((118, 177), Image.ANTIALIAS)
        photo4 = ImageTk.PhotoImage(im)
        self.cv.itemconfigure(self.p4, image=photo4)
        self.turn = 2
        self.turns = 1
        flag = True

    def third_round(self):
        # Send to All Player
        msg = ('T4/' + str(self.board[4:5])).encode('utf-8')
        self.broadcast(msg, "Server:")
        global photo5
        # image5
        im = Image.open(self.board_card_str[4])
        im = im.resize((118, 177), Image.ANTIALIAS)
        photo5 = ImageTk.PhotoImage(im)
        self.cv.itemconfigure(self.p5, image=photo5)
        self.turn = 3
        self.turns = 1
        self.predict()
        self.banner_var.set('New Game')

    def predict(self):
        # count how many wins
        c = 0
        self.p_score[0] = evaluator.evaluate(board, player1_hand)
        self.p_score[1] = evaluator.evaluate(board, player2_hand)
        self.p_score[2] = evaluator.evaluate(board, player3_hand)
        self.p_score[3] = evaluator.evaluate(board, player4_hand)
        for i in range(0, 4):
            if self.player_flag[i] != 0:
                self.percent[i] = evaluator.get_five_card_rank_percentage(self.p_score[i])
            else:
                self.percent[i] = 0
        self.rank = ss.rankdata(self.percent).tolist()
        for i in range(0, 4):
            if self.rank[i] == 1.0:
                self.player_var[i].set(self.player_str[i] + '\n WIN')
                c = c + 1
            else:
                self.player_var[i].set(self.player_str[i] + '\n LOOSE')
        self.collect = self.collect / c
        for i in range(0, 4):
            if self.rank[i] == 1.0:
                self.coins[i] = self.coins[i] + int(self.collect)

    def lead_the_play(self):
        self.lead = (self.lead + 1) % 4
        self.player_str[self.lead] = 'Lead\n'
        self.player_str[(self.lead + 1) % 4] = 'Second\n'
        self.player_str[(self.lead + 2) % 4] = 'Third\n'
        self.player_str[(self.lead + 3) % 4] = 'Forth\n'
        self.coins[self.lead] = self.coins[self.lead] - 100
        self.coins[(self.lead + 1) % 4] = self.coins[(self.lead + 1) % 4] - 50
        self.collect = self.collect + 150
        # Add the sequences
        self.seq[self.lead] = 1
        self.seq[(self.lead + 1) % 4] = 2
        self.seq[(self.lead + 2) % 4] = 3
        self.seq[(self.lead + 3) % 4] = 4

    def banner_for_turn(self):
        flag = True
        while flag:
            if self.turns == 1:
                self.banner_var.set('Lead\'s turn')
            elif self.turns == 2:
                self.banner_var.set('Second\'s turn')
            elif self.turns == 3:
                self.banner_var.set('Third\'s turn')
            elif self.turns == 4:
                self.banner_var.set('Forth\'s turn')
            elif self.turns == 5:
                self.banner_var.set('Next Round')
                flag = False

    def fill_money(self):
        for i in range(0, 4):
            self.coins[i] = self.coins[i] + 1000
        self.reset_str()

    def reset_str(self):
        for i in range(0, 4):
            self.player_var[i].set(self.player_str[i] + '$' + str(self.coins[i]))

    def accept_incoming_connections(self):
        """Sets up handling for incoming clients."""
        while True:
            if self.num_player <= 3:
                client, client_address = SERVER.accept()
                print("%s:%s has connected." % client_address)
                addresses[client] = client_address
                Thread(target=self.handle_client, args=(client,)).start()
            else:
                break

    def handle_client(self, client):  # Takes client socket as argument.
        """Handles a single client connection."""
        name = 'Player' + str(self.num_player)
        welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
        client.send(bytes(welcome, "utf8"))
        time.sleep(0.5)
        msg = "%s has joined the chat!" % name
        self.broadcast(bytes(msg, "utf8"))
        time.sleep(0.5)
        msg = 'Server:O/' + str(self.num_player)
        client.send(bytes(msg, "utf8"))
        clients[client] = name
        self.num_player = self.num_player + 1
        i = int(clients[client][6:7])
        while True:
            msg = client.recv(BUFSIZ)
            if msg == bytes("{quit}", "utf8"):
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                self.broadcast(bytes("%s has left the chat." % name, "utf8"))
                break
            elif msg == bytes("throw", "utf8") and self.player_flag[i] != 0 \
                    and self.seq[i] == self.turns:
                self.player_flag[i] = 0
                self.broadcast(bytes("had throw the card", "utf8"), name + ": ")
                self.player_var[i].set(self.player_str[i] + '\n Throw')
                self.turns = self.turns + 1
            elif msg == bytes("follow", "utf8") and self.player_flag[i] != 0 \
                    and self.turn == 1 and self.seq[i] == self.turns:
                self.broadcast(bytes("had follow the card", "utf8"), name + ": ")
                if self.player_str[i] == 'Lead\n':
                    self.coins[i] = self.coins[i]
                elif self.player_str[i] == 'Second\n':
                    self.coins[i] = self.coins[i] - 50
                    self.collect = self.collect + 50
                else:
                    self.coins[i] = self.coins[i] - 100
                    self.collect = self.collect + 100
                self.turns = self.turns + 1
                self.player_var[i].set(self.player_str[i] + '$' + str(self.coins[i]))
            elif msg == bytes("follow", "utf8") and self.player_flag[i] != 0 \
                    and self.turn == 2 and self.seq[i] == self.turns:
                self.broadcast(bytes("had follow the card", "utf8"), name + ": ")
                self.coins[i] = self.coins[i] - 100
                self.collect = self.collect + 100
                self.turns = self.turns + 1
                self.player_var[i].set(self.player_str[i] + '$' + str(self.coins[i]))
            else:
                self.broadcast(msg, name + ": ")

    @staticmethod
    def broadcast(msg, prefix=""):  # prefix is for name identification.
        """Broadcasts a message to all the clients."""
        for sock in clients:
            sock.send(bytes(prefix, "utf8") + msg)

    def connect(self):
        while True:
            SERVER.listen(5)
            print("Waiting for connection...")
            accept_thread = Thread(target=self.accept_incoming_connections)
            accept_thread.start()
            accept_thread.join()
            SERVER.close()

    @staticmethod
    def int_to_string(player):
        d = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 1}
        num = []
        s_get = Card.print_pretty_cards(player)
        s = s_get.split(',')

        for i in range(0, len(s)):
            temp = s[i].split()
            for j in range(0, 2):
                try:
                    temp[j] = d[temp[j]]
                except KeyError:
                    temp[j] = temp[j]
            num.append(str(int(temp[0]) + int(temp[1]) * 13))
        print(num)
        return num

    @staticmethod
    def string_to_place(k):
        p_place = []
        for i in k:
            p_place.append('poker\\' + i + '.png')
        print(p_place)
        return p_place

    @staticmethod
    def new():
        global board, player1_hand, player2_hand, player3_hand, player4_hand
        deck = Deck()
        board = deck.draw(5)
        player1_hand = deck.draw(2)
        player2_hand = deck.draw(2)
        player3_hand = deck.draw(2)
        player4_hand = deck.draw(2)


win = Tk()
win.geometry('1200x800')
MainWindow(win)
win.mainloop()
