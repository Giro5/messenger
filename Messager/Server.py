import socket
import threading

def Launch():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 9170))
    users = []
    msgs = []
    addrs = []
    print("already\n")
    while True:
        data, addr = sock.recvfrom(1048576)
        data = data.decode("utf-8")
        print("address:", addr, ", text:", data)
        if data[0] == "@":
            if addr not in addrs:
                users.append(data.split()[1])
                addrs.append(addr)
                sock.sendto(f"@ {addr[0]} {addr[1]} {len(users)-1}".encode("utf-8"), addr)
                print(data.split()[1], "connected")

        elif data[0] == "#":
            sock.sendto(("# " + " ".join(users)).encode("utf-8"), addr)

        elif data[0] == "%":
            if addr in addrs:
                users.remove(data.split()[1])
                addrs.remove(addr)
                print(data.split()[1], "disconnected")

        elif data[0] == "^":
            name = data.split()[1]
            if name in users:
                i = users.index(name)
                sock.sendto(f"^ {addrs[i][0]} {addrs[i][1]} {i}".encode("utf-8"), addr)

        elif data[0] == "$":
            letter = data[2:]
            #sender_ip = letter.split(":")[0]
            #sender_port = int(letter.split(":")[1].split("|")[0])
            recipient_ip = letter.split()[1].split(":")[0]
            recipient_port = int(letter.split(":")[2].split("|")[0])
            print(addr, (recipient_ip, recipient_port))
            if addr in addrs and (recipient_ip, recipient_port) in addrs:
                msgs.append(letter)
                print("accepted msg:", letter)

        for i in range(len(addrs)):
            sock.sendto(("$\n" + "\n".join(msgs)).encode("utf-8"), addrs[i])

        for i in range(len(addrs)):
            sock.sendto(("# " + " ".join(users)).encode("utf-8"), addrs[i])

        print()
    sock.close()

if __name__ == "__main__":
    Launch()
