import socket

HEADER_LENGTH = 3
IP = socket.gethostname()
PORT = 2000

#Set up client details
my_username = "Patient2"
username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Try to connect:
while True:
    try:
        client_socket.connect((socket.gethostname(), PORT))
        break
    except:
        print("Problem connecting with Doctor. Please stand by....")
        continue

#Send username to Doctor
client_socket.send(username_header + username)

while True:
    # receive things
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
    except:
        #If the connection was not successful, keep trying to reconnect here (indefinitely).
        print("Problem with connection - trying to reconnect....")
        while True:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((socket.gethostname(), PORT))
                break
            except:
                continue
        client_socket.send(username_header + username)
        continue

    #Here we check if the length of the message received == length specified in the header.
    expected_message_length = int(message_header.decode("utf-8"))
    message = client_socket.recv(expected_message_length).decode("utf-8")
    actual_length = len(message)

    if actual_length == expected_message_length:
        print("Full message received.")
    else:
        print("Full message not received!!!!")
    # Code to tell server that not all message was received
        receipt = f"{my_username} did not receive the full message".encode("utf-8")
        receipt_header = f"{len(receipt):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(receipt_header + receipt)
    #Now print out the message received in the patient's screen:
    print(message)

    #Menu giving the patient options to wait for a message to come in or to send a message.
    options = input(f"Enter 'm' to send a message to the Doctor or 'w' to wait for advice : > ")
    while options != 'm' and options != 'w':
        options = input(f"Invalid entry. Enter 'm' to send a message to the Doctor or 'w' to wait for advice : > ")
    while options == 'm':
        consultMessage = input(f"Enter message for the Doctor: > ")
        consultMessage = consultMessage.encode("utf-8")
        consultMessageHeader = f"{len(consultMessage):<{HEADER_LENGTH}}".encode("utf-8")

        try:
            client_socket.send(consultMessageHeader + consultMessage)
        except:
            print("Error sending message to the Doctor.")
        options = input(f"Enter 'm' to send a message to the Doctor or 'w' to wait for advice : > ")
        while options != 'm' and options != 'w':
            options = input(f"Invalid entry. Enter 'm' to send a message to the Doctor or 'w' to wait for advice : > ")