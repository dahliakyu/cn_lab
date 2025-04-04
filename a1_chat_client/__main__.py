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

def send_all(sock, data) -> None: 
    """
    Custom function for sending data chunks through a socket replacing sendall().
    Allowing partial sends until all data is transmitted.

    Args:
        sock: Socket object for data transmission
        data: Data to be sent
    
    Raises:
        RuntimeError: Broken connection error during transimission
        ConnectionError: Other network related errors including BrokenPipeError, ConnectionResetError and OSError
    """
    total_sent = 0
    while total_sent < len(data):
        try:
            sent = sock.send(data[total_sent:])
            # Raise connection error after handing 0 bytes data
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += sent
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            print(f"Connection error: {e}")
            raise

# Login phase of the chat client
def login(sock) -> bool:
    """
    Server authetication function implementing RA1 to RA8, see inline comments for specific requirements.

    Args:
        sock: Socket object for data transmission
    
    Returns:
        bool: True if login successful, False otherwise.

    """
    # RA1, RI2: Mandatory welcome message upon startup.
    print("Welcome to Chat Client. Enter your login:")
    
    while True: # Retry loop in case of failed login attempt without restarting the client (RA6)
        try:
            username = input().strip()
            # Quit server if prompted (RC1)
            if username == '!quit':
                print("\nExiting server...")
                sock.close
                return False
            # Handle empty username input
            if not username:
                print("Please provide a non-empty username:")
                continue
            # First handshake message
            message = f"HELLO-FROM {username}\n"

            send_all(sock, f"HELLO-FROM {username}\n".encode("UTF-8")) # Convert string to bytes
            # Receive server response
            response = ''
            # Todo: Timeout implementation as a separate function
            while '\n' not in response: # Waiting for complete message
                try:
                    chunk = sock.recv(1024).decode("utf-8", errors="replace") # Convert bytes to strings, handles alien bytes instead of crashing
                    if not chunk: # Graceful closure
                        break
                    response += chunk
                except (ConnectionResetError, OSError): # Abrupt closure
                    break
            
            # Process server response
            if 'HELLO' in response:
                print(f"Successfully logged in as {username}")
                return True
            elif 'IN-USE' in response:
                print(f"Cannot log in as {username}. That username is already in use.")
                print("Please enter a different username:")
            elif 'BUSY'in response:
                print("Cannot log in. The server is full!")
                # Graceful Exit
                return False
            else:
                print(f"Cannot log in as {username}. That username contains disallowed characters")
                print("Please enter a different username:")
        
        # Final exception checks
        except (EOFError, KeyboardInterrupt):
            print("\nExiting server...")
            return False
        except Exception as e: # Catch alls
            print(f"An error has occurred during login: {e}")

# Execute using `python -m a1_chat_client`
def main() -> None:
    args: Namespace = parse_arguments()
    port: int = args.port
    host: str = args.address

    # TODO: Your implementation here


if __name__ == "__main__":
    main()
