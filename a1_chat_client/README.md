## Requirements

### Authentication Requirements:

Note: If the log-in handshake fails, the server will close the connection with your client. Reasons for a failed handshake include providing an invalid or taken username, sending the wrong header, etc.

- RA1: The client must ask the user for a username and attempt to log them in. (done)
- RA2: The client must ask the user for a new username if the provided one is already in use, with an informative message. (done)
- RA3: The client must inform the user if the server is full and exit gracefully. (done)
- RA4: The client must inform the user if their username was rejected for any other reason and ask for a new username. Examples include forbidden symbols (!@#$%^&*)
- RA5: The client must inform the user if their username was rejected for any other reason and ask for a new username. Examples include commands (@username, !who)
- RA6: The client should not have to be restarted after a failed log-in attempt.(done)
- RA7: The client should be able to send a message to echobot and receive the full message
- RA8: The client should be able to stop the program with !quit at any point (including when asking for the name)

### Special Command Requirements:

- RC1: Typing the command !quit at any point must exit the client. No additional steps should be required to exit (e.g., Ctrl+C).
- RC2: Typing the command !who must print a list of users.

### Technical Requirements:
- RT1: The client must use the TCP transport layer protocol for all network communication.
- RT2: The client must not use the sendall() function in Python. (Implemented custom send_all)
- RT3: The client must not print incomplete messages.
- RT4: The client must support the sending and receiving of messages of any nonzero length.
- RT5: The client must print messages as soon as they are fully received.
- RT6: Awaiting user keyboard input should not prevent newly incoming messages from being displayed.
- RT7: Receiving any protocol header from the server at any point in the client's lifetime must be handled appropriately.

### Interface Requirements:
- RI1: The client must not print any of the protocol headers. This applies to ALL the user workflows
- RI2: On a startup, the application must print: Welcome to Chat Client. Enter your login: (done)
- RI3: If the login was successful, the application must print: Successfully logged in as <username>! (done)
- RI4: If login failed because the username is already in use, the application must print: Cannot log in as <username>. That username is already in use. (done)
- RI5: If login failed because of a malformed username, the application must print: Cannot log in as <username>. That username contains disallowed characters. (done)
- RI6: If login failed because the server is full, the application must print: Cannot log in. The server is full! (done)
- RI7: The messages must be sent by typing: @<username> <message>
- RI8: If the message was sent successfully, the client must print: The message was sent successfully
- RI9: If the message was sent to a user that does not exist, the client must print: The destination user does not exist
- RI10: When the user receives a message, the chat client must print From <username>: <message>
- RI11: The client must receive the list of users received after !who a command as:
    ```
    There are <user count> online users: 
    <username_1>
    <username_2>
    ...
    <username_n>
    ```
- RI12: The message displayed when the header is malformed must be: Error: Unknown issue in previous message header.
- R13: The message displayed when the body is malformed must be: Error: Unknown issue in previous message body.

## To do:
- notify specific disallowed characters in username
- receiver
- server message processing
- timeout?
- main pipeline
- convert to class method?

## Issue:
- The assignment is client side code, might need to finish a3 for server side protocols?
- Unclear on the connection closure on failed login attempt: does the operation need to be terminated completely or is re-attempt allowed? 