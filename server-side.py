import errno
import socket
import threading
from time import sleep


class ChatServer:
    clients_list = []
    last_received_message = ""
    # for re-use user
    message_list = []
    str_client_list = []
    un_expected_disconnection = []
    obj_msg = []

    def __init__(self):
        # init socket
        self.server_socket = None
        # start listening
        self.create_listening_server()

    def create_listening_server(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = '127.0.0.1'
        # TODO: apply port with input value
        server_port = 9999
        # this will allow you to immediately restart a TCP server
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # this makes the server listen to requests coming from other computers on the network
        self.server_socket.bind((server_ip, server_port))

        print('Start Server !')
        print('listening connection ...')

        self.server_socket.listen(5)
        self.receive_messages_in_a_new_thread()

    def receive_messages(self, so):
        while True:
            incoming_buffer = so.recv(1024)

            if not incoming_buffer:
                break

            self.message_list.append(incoming_buffer.decode('utf-8'))
            self.broadcast_to_all_clients(so)  # send to all clients

    def broadcast_to_all_clients(self, senders_socket):
        for client in self.clients_list:
            sock, (ip, port) = client
            if sock is not senders_socket:
                sock.sendall(self.message_list[-1].encode('utf-8'))

            # self.un_expected_disconnection.append(ip + ':' + str(port))
            # if ip + ':' + str(port) in self.str_client_list:
            #     self.str_client_list.remove(ip + ':' + str(port))

    # def reconnect(self, so, ip, port):
    #     t = threading.Thread(target=self.receive_messages, args=(so,))
    #     t.start()
    #     self.un_expected_disconnection.remove(ip + ':' + str(port))

    def receive_messages_in_a_new_thread(self):
        connection = False
        while True:
            # accept
            client = so, (ip, port) = self.server_socket.accept()
            print(ip, port)
            if ip + ':' + str(port) in self.un_expected_disconnection:
                for msg in self.message_list:
                    so.sendall(msg.encode('utf-8'))
                self.un_expected_disconnection.remove(ip + ':' + str(port))

            self.clients_list.append(client)
            self.str_client_list.append(ip + ':' + str(port))

            t = threading.Thread(target=self.receive_messages, args=(so,))
            t.start()

            if not connection:
                try:
                    so.connect((ip, port))
                    print("re-connection successful")
                    for i in self.message_list:
                        so.sendall(i.encode('utf-8'))
                    connection = True

                except socket.error as e:
                    if e.errno == 56:
                        continue
                    else:
                        print('socket error', e)
                        self.clients_list.remove(client)

                finally:
                    sleep(2)

                # if un_expected_disconnection user connect send list of msg


if __name__ == "__main__":
    ChatServer()
