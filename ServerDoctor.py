import socket
import select

HEADER_LENGTH = 3   #Header will be used to specify the length of the message received
IP  = socket.gethostname()
PORT = 2000

#This function returns a message received in the format: header, message_body- will be called further down.
def receive_message (client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode("utf-8"))
        return {"header": message_header, "data": client_socket.recv(message_length).decode("utf-8")}

    except:
        return False

#Set up the server socket details:
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(False)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Not really sure if this line is necessary.
server_socket.bind((IP, PORT))
server_socket.listen()   #Might be able to limit the number of clients by specifying a number here

# Sockets from which we expect to read
sockets_list = [server_socket]
# Sockets to which we expect to write
outputs = [ ]

#This is a clients dictionary (key/value pair)
clients = {}

print("Waiting for incoming connections...")

while True:
    #Monitor I/O ports for activity:
    read_sockets, write_sockets, exception_sockets = select.select(sockets_list, outputs, sockets_list)  #Could we just have one list?
    #Now go through each socket in which activity was detected:
    for notified_socket in read_sockets:
        if notified_socket == server_socket:#ie if the activity was detected on the server socket then it must be a new
            #connection request. Otherwise the activity would have been on a client socket. When the server receives
            #a connection request, it sets up a new socket on a new port and then uses that to communicate with that client.
            #The server socket is only used to accept new connections, not to communicate once the connection is established. I think!
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)#Here we're calling the function defined above.
            #so, in the above line, the user will be a header, data pair as defined in the function above
            #The user 'data' field represents the name of the patient
            user_id = user['data']#The patient id
            sockets_list.append(client_socket)#Add the client socket to the list of sockets
            clients[client_socket] = user #Also add the client socket to the dictionary of clients
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data']}")

            #Now send a welcome message to the new connection
            welcome_message = ("You are connected - stand by for advice.").encode("utf-8")
            welcome_header = f"{len(welcome_message):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(welcome_header + welcome_message)

        else:
            #Here the socket on which activity was detected is not the server socket so it must be regular communication
            #and not a new connection request.
            try:
                message = receive_message(notified_socket)
                user = clients[notified_socket]
                print(f"Received from {user['data']}: {message['data']}")

            except:
                print(f"Closed connection from {clients[notified_socket]['data']}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                #continue

    #Now print out a list of connected patients:
    print("The clients currently connected are:")
    for eachClient in clients:
        print(clients[eachClient]['data']),

    #See what the doctor wants to do next:
    options = input(f"Enter a patient name to send advice or enter 's' to stand-by for more connections: > ")
    while (options != 's'):
        if options == 'p':
            print("The clients currently connected are:")
            for eachClient in clients:
                print(clients[eachClient]['data']),
        else:
            patientFound = False
            for eachClient in clients:
                if clients[eachClient]['data'] == options:
                    patientFound = True
                    adviceMessage = input(f"Enter advice for {clients[eachClient]['data']}: > ")
                    adviceMessage = adviceMessage.encode("utf-8")
                    adviceMessage_header = f"{len(adviceMessage):<{HEADER_LENGTH}}".encode("utf-8")

                    try:
                        eachClient.send(adviceMessage_header + adviceMessage)
                    except:
                        print("Error sending advice to the patient.")

            if not patientFound:
                print("Unable to find patient. Please try again.")

        options = input(f"Enter patient name, 's' to stand-by for more connections or 'p' to print the list again: > ")