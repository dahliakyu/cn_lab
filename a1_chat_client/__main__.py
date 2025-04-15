import socket
import threading
import sys
from argparse import Namespace, ArgumentParser

def parse_arguments() -> Namespace:
    """
    Parse command line arguments for the chat client.
    The two valid options are:
        --address: The host to connect to. Default is "0.0.0.0"
        --port: The port to connect to. Default is 5378
    :return: The parsed arguments in a Namespace object.
    """

    parser: ArgumentParser = ArgumentParser(
        prog="python -m a1_chat_client",
        description="A1 Chat Client assignment for the VU Computer Networks course.",
        epilog="Authors: Your group name"
    )
    parser.add_argument("-a", "--address",
                      type=str, help="Set server address", default="0.0.0.0")
    parser.add_argument("-p", "--port",
                      type=int, help="Set server port", default=5378)
    return parser.parse_args()

def handleReceive(sock):
    try:
        while True:
            buff = ""
            while "\n" not in buff:
                try:
                    data = sock.recv(4096)
                    if not data:
                        print("Connection closed by server.")
                        return
                    buff += data.decode("utf-8")
                except UnicodeDecodeError:
                    print("Error decoding message from server.")
                    return
                except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                    print(f"Connection error: {e}")
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
                        print(f"\nThere are {len(users)} online users:")
                        for user in users:
                            print(user)
                    else:
                        print("\nThere are 0 online users.")
                        
                elif header == "DELIVERY":
                    if len(parts) < 3:
                        print("Error: Invalid DELIVERY message format.")
                        continue
                    sender = parts[1]
                    message = " ".join(parts[2:])
                    print(f"From {sender}: {message}")
                    
                elif header == "SEND-OK":
                    print("The message was sent successfully")
                    
                elif header == "BAD-DEST-USER":
                    print("The destination user does not exist")
                    
                elif header == "BAD-RQST-HDR":
                    print("Error: Unknown issue in previous message header.")
                    
                elif header == "BAD-RQST-BODY":
                    print("Error: Unknown issue in previous message body.")
                    
                else:
                    print(f"Error: Unknown message header '{header}'")
    finally:
        sock.close()

def handleSend(sock):
    try:
        while True:
            try:
                message = input().strip()
            except EOFError:
                print("\nExiting...")
                break
                
            if not message:
                continue
                
            if message == "!quit":
                try:
                    sock.send("QUIT\n".encode("utf-8"))
                except (socket.error, BrokenPipeError, ConnectionResetError):
                    print("Connection lost. Exiting...")
                break
            
            elif message == "!who":
                try:
                    sock.send("LIST\n".encode("utf-8"))
                except (socket.error, BrokenPipeError, ConnectionResetError):
                    print("Failed to send LIST request. Connection lost.")
                    break
                    
            elif message.startswith("@"):
                parts = message.split(maxsplit=1)
                if len(parts) < 2:
                     textOfMessage = ''
                else:
                    textOfMessage = parts[1]
                    
                destUser = parts[0][1:]

                full_message = f"SEND {destUser} {textOfMessage}\n"
                try:
                    sock.send(full_message.encode("utf-8"))
                except (socket.error, BrokenPipeError, ConnectionResetError):
                    print("Failed to send message. Connection lost.")
                    break
                    
            else:
                print("Invalid format. Use '@username message' or commands (!quit, !who)")
    finally:
        sock.close()

def main() -> None:
    
    args: Namespace = parse_arguments()
    port: int = args.port
    host: str = args.address
    
    print("Welcome to Chat Client. Enter your login: ")
    
    while True:
        host_port = (host, port)
        chatSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            chatSocket.connect(host_port)
        except socket.error as e:
            print(f"Cannot connect to server: {e}")
            return
            
        user_name = input().strip()
        
        if user_name == "!quit":
            chatSocket.close()
            return
            
        if not user_name:
            print("Error: Username cannot be empty.")
            chatSocket.close()
            print("Enter your login:")
            continue
            
        # Check if username starts with command characters
        if user_name.startswith("@") or user_name.startswith("!"):
            print(f"Error: Username '{user_name}' cannot start with '@' or '!' (reserved for commands).")
            chatSocket.close()
            print("Enter your login:")
            continue
            
        # Check for forbidden characters
        forbidden_symbols = " !@#$%^&*,"
        if any(char in forbidden_symbols for char in user_name):
            print(f"Cannot log in as {user_name}. That username contains disallowed characters.")
            chatSocket.close()
            print("Enter your login:")
            continue
        
        # Send login request
        hello_msg = f"HELLO-FROM {user_name}\n"
        try:
            chatSocket.send(hello_msg.encode("utf-8"))
        except socket.error as e:
            print(f"Failed to send login request: {e}")
            chatSocket.close()
            continue
            E
        # Wait for server response
        buff = ""
        while "\n" not in buff:
            try:
                data = chatSocket.recv(4096)
                if not data:
                    print("Connection closed by server during login.")
                    chatSocket.close()
                    break
                buff += data.decode("utf-8")
            except UnicodeDecodeError:
                print("Error decoding server response.")
                chatSocket.close()
                break
            except (socket.error, ConnectionResetError) as e:
                print(f"Connection error: {e}")
                chatSocket.close()
                break
                
        if not buff:
            print("Enter your login: ")
            continue
            
        response = buff.strip()
        
        if response.startswith("HELLO"):
            print(f"Successfully logged in as {user_name}!")
            break
        elif response == "IN-USE":
            print(f"Cannot log in as {user_name}. That username is already in use.")
            chatSocket.close()
            print("Enter your login:")
        elif response == "BUSY":
            print("Cannot log in. The server is full!")
            chatSocket.close()
            return
        else:
            # Handle other server-specific rejection reasons
            print(f"Error: {response}")
            chatSocket.close()
            print("Enter your login:")

    receive_thread = threading.Thread(target=handleReceive, args=(chatSocket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        handleSend(chatSocket)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        chatSocket.close()

if __name__ == '__main__':
    main()
