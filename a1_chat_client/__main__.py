import socket
import threading

def handleReceive(sock):
    while True:
        buff = ""
        while "\n" not in buff:
            try:
                data = sock.recv(4096).decode("utf-8")
                if not data:
                    print("Socket is closed.")
                    return
                buff += data
            except:
                print("Socket error occurred.")
                return
        
        for line in buff.splitlines():
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            header = parts[0]
            
            if header == "LIST-OK":
                if len(parts) > 1:
                    users = []
                    for part in parts[1:]:
                        users.extend(part.split(','))
                    users = [u for u in users if u]
                    print(f"There are {len(users)} online users:")
                    for user in users:
                        print(user)
                else:
                    print("There are 0 online users:")
                    
            elif header == "DELIVERY":
                if len(parts) < 3:
                    print("Error: Unknown issue in previous message header.")
                    continue
                sender = parts[1]
                message = " ".join(parts[2:])
                print(f"From {sender}: {message}")
                
            elif header == "SEND-OK":
                print("The message was sent successfully")
                
            elif header == "BAD-DEST-USER":
                print("The destination user does not exist")
                
            else:
                print("Error: Unknown issue in previous message body.")

def handleSend(sock, user):
    while True:
        message = input().strip()
        if not message:
            continue
            
        if message.startswith("!"):
            if message == "!quit":
                sock.send("QUIT\n".encode("utf-8"))
                break
            elif message == "!who":
                sock.send("LIST\n".encode("utf-8"))
                
        elif message.startswith("@"):
            parts = message.split(maxsplit=1)
            if len(parts) < 2:
                print("Invalid format. Use '@username message'")
                continue
                
            destUser = parts[0][1:]
            if not destUser:
                print("Invalid format. Use '@username message'")
                continue
                
            if destUser == user:
                print("Cannot send a message to yourself.")
                continue
                
            textOfMessage = parts[1]
            full_message = f"SEND {destUser} {textOfMessage}\n"
            sock.send(full_message.encode("utf-8"))
                
        else:
            print("Invalid format. Use '@username message' or commands (!quit, !who)")

def chatClient():
    print("Welcome to Chat Client. Enter your login:")
    
    while True:
        host_port = ("127.0.0.1", 5378)
        chatSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            chatSocket.connect(host_port)
        except:
            print("Cannot connect to server.")
            return
            
        user_name = input().strip()
        
        if user_name == "!quit":
            chatSocket.close()
            return
            
        forbidden_symbols = " !@#$%^&*"
        has_forbidden = any(char in forbidden_symbols for char in user_name)
        is_command = user_name.startswith("@") or user_name.startswith("!")

        if is_command:
            chatSocket.close()
            print(f"Cannot log in as {user_name}. That username contains disallowed characters.")
            print("Enter your login:")
            continue
        elif has_forbidden:
            chatSocket.close()
            print(f"Cannot log in as {user_name}. That username contains disallowed characters.")
            print("Enter your login:")
            continue
       
        chatSocket.send(("HELLO-FROM " + user_name + "\n").encode("utf-8"))
        
        buff = ""
        while "\n" not in buff:
            try:
                data = chatSocket.recv(4096).decode("utf-8")
                if not data:
                    print("Connection closed by server.")
                    chatSocket.close()
                    print("Enter your login:", end=" ")
                    break
                buff += data
            except:
                print("Connection error occurred.")
                chatSocket.close()
                print("Enter your login:", end=" ")
                break
                
        if not buff:
            continue
            
        response = buff.strip()
        
        if response.startswith("HELLO"):
            print(f"Successfully logged in as {user_name}!")
            break
        elif response == "IN-USE":
            chatSocket.close()
            print(f"Cannot log in as {user_name}. That username is already in use.")
            print("Enter your login:")
        elif response == "BUSY":
            chatSocket.close()
            print("Cannot log in. The server is full!")
            return
        else:
            chatSocket.close()
            print("Error: Unknown login response from server.")
            print("Enter your login:")

    receive_thread = threading.Thread(target=handleReceive, args=(chatSocket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        handleSend(chatSocket, user_name)
    except:
        pass
        
    chatSocket.close()

if __name__ == '__main__':
    chatClient()