from tkinter import *
from tkinter import messagebox
import socket
import threading

sign = False
myaddr = ()
name = ""
myid = -1
seladdr = ()
selname = ""
selindex = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("localhost", 9170))

root = Tk()
root.title("Messager")
root.geometry("1000x500+300+200")

listFrame = Frame(root, width = 300, bg = "#b5b5b5")
listFrame.pack(side = "left", fill = "both")

BtnSend = Button(root, text = "Send")
BtnSend.pack(side = "bottom", fill = "x")

Stroke = Entry(root)
Stroke.pack(side = "bottom", fill = "x")

chatFrame = Frame(root,  width = 700, bg = "#cfcfcf")
chatFrame.pack(fill = "both", expand = True)

listScrollY = Scrollbar(listFrame)
listScrollY.pack(side = "right", fill = "y")
listScrollX = Scrollbar(listFrame, orient = HORIZONTAL)
listScrollX.pack(side = "bottom", fill = "x")

UsersList = Listbox(listFrame, yscrollcommand = listScrollY.set, xscrollcommand = listScrollX.set, width = 40)
UsersList.pack(side = "right", fill = "both")
listScrollY.config(command = UsersList.yview)
listScrollX.config(command = UsersList.xview)

chatScrollY = Scrollbar(chatFrame)
chatScrollY.pack(side = "right", fill = "y")
chatScrollX = Scrollbar(chatFrame, orient = HORIZONTAL)
chatScrollX.pack(side = "bottom", fill = "x")

Chat = Listbox(chatFrame, yscrollcommand = chatScrollY.set, xscrollcommand = chatScrollX.set)
Chat.pack(side = "right", fill = "both", expand = True)
chatScrollY.config(command = Chat.yview)
chatScrollX.config(command = Chat.xview)

def SignIn():
    global name, sign
    if not sign:
        child = Toplevel(root)
        child.title("Login")
        child.geometry("400x150+500+400")
        child.resizable(False, False)
        child.grab_set()
        child.focus_set()
        Label(child, text = "Enter your login:").place(x = 10, y = 18)
        err = Label(child, text = "*In your name has spaces or it's already taken", fg = "#ff0000")
        nameEntry = Entry(child)
        nameEntry.place(x = 10, y = 40, width = 380, height = 20)
        def Login(event):
            global name, sign
            nam = nameEntry.get()
            if " " not in nam and nam not in UsersList.get(0, END):
                name = nam
                #serv.com(f"@ {name}")
                sock.send(f"@ {name}".encode("utf-8"))
                root.title("Messager logged as " + name)
                sign = True
                root.lift(child)
                child.destroy()
            else:
                err.place(x = 10, y = 80)
        Button(child, text = "Sign In", command = lambda: Login("")).place(x = 10, y = 110, width = 380, height = 30)
        child.bind("<Return>", Login)
        child.lift(root)
        nameEntry.focus_set()
    return

def Reception():
    global name, sign, myaddr, seladdr, selindex, selname, myid
    while True:
        #if sign:
        data, addr = sock.recvfrom(1048576)
        data = data.decode("utf-8")
        print("address:", addr, ", text:", data)
        if data[0] == "#":
            UsersList.delete(0, END)
            for user in data.split()[1:]:
                if name != user:
                    UsersList.insert(END, user)
            #if sel != None:
            #    UsersList.activate(0)
        elif data[0] == "$" and len(data) > 2:
            msgs = data.split("\n")[1:]
            cur_msgs = []
            for letter in msgs:
                sender_ip = letter.split(":")[0]
                sender_port = int(letter.split(":")[1].split("|")[0])
                recipient_ip = letter.split()[1].split(":")[0]
                recipient_port = int(letter.split(":")[2].split("|")[0])
                if myaddr == (sender_ip, sender_port) and seladdr == (recipient_ip, recipient_port):
                    cur_msgs.append(f"{name}: {' '.join(letter.split()[2:])}")
                elif seladdr == (sender_ip, sender_port) and myaddr == (recipient_ip, recipient_port):
                    cur_msgs.append(f"{selname}: {' '.join(letter.split()[2:])}")
                Chat.delete(0, END)
                for msg in cur_msgs:
                    Chat.insert(END, msg)
                Chat.see(END)
        elif data[0] == "@":
            myaddr = data.split()[1:][0], int(data.split()[1:][1])
            myid = int(data.split()[1:][2])
        elif data[0] == "^":
            seladdr = data.split()[1:][0], int(data.split()[1:][1])
            selindex = int(data.split()[1:][2])

recept = threading.Thread(target=Reception)
recept.daemon = True
recept.start()

def Closing():
    global name
    sock.send(f"% {name}".encode("utf-8"))
    sock.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", Closing)

def SelUser(event):
    global selname, seladdr, selindex
    sel = UsersList.curselection()[0]
    selname = UsersList.get(sel)
    print(selname)
    BtnSend.config(text = "Send to " + selname)
    sock.send(f"^ {selname}".encode("utf-8"))

UsersList.bind("<Double-Button-1>", SelUser)

def SendLetter(event):
    global myaddr, name, myid, seladdr, selname, selindex
    myfull = f"{myaddr[0]}:{myaddr[1]}|{name}|{myid}"
    selfull = f"{seladdr[0]}:{seladdr[1]}|{selname}|{selindex}"
    letter = f"$ {myfull} {selfull} {Stroke.get()}"
    Stroke.delete(0, END)
    print(letter)
    sock.send(letter.encode("utf-8"))

BtnSend.config(command = lambda: SendLetter(""))
Stroke.bind("<Return>", SendLetter)

sock.send("#".encode("utf-8"))
SignIn()

root.mainloop()