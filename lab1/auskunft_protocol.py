"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    def serve(self):

        phonebook = {
            "John": "1234567890",
            "Jane": "0987654321",
            "Bob": "1122334455",
            "Alice": "5566778899",
            "Charlie": "2233445566",
            "David": "3344556677",
            "Eve": "4455667788",
            "Frank": "5566778899",
            "Grace": "6677889900",
            "Heidi": "7788990011"
        }

        """ Serve phonebook """
        self.sock.listen(1)

        while self._serving:
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    command = data.decode('ascii')
                    if command == "GETALL":
                        all_numbers = ""
                        for name, number in phonebook.items():
                            all_numbers += (name + "=" + number + ";")
                        connection.send(all_numbers.encode('ascii'))
                    elif command.startswith("GET "):
                        name = command[4:]
                        if name in phonebook:
                            connection.send((name + "=" + phonebook[name] + ";").encode('ascii'))
                        else:
                            connection.send(("ERROR=Name not found;").encode('ascii'))
                    elif command == "EXIT":
                        self._serving = False
                        break
                    else:
                        connection.send(("ERROR=Invalid command;").encode('ascii'))
                connection.close()
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def callall(self):
        """ Call server for all phonebooks """
        self.logger.info("Client calling for all phonebooks.")
        self.sock.send("GETALL".encode('ascii'))  # send encoded string as data

        data = self.sock.recv(1024)  # receive the response
        phonebook_entries = data.decode('ascii').split(';')[:-1]  # split the response into phonebooks
        phonebook_list = []
        print(f"{'-'*60}")
        print(f"| {'Name'.ljust(20)} | {'Number'.ljust(15)} |")
        print(f"{'-'*60}")
        for phonenumber in phonebook_entries:
            name, number = phonenumber.split('=')
            phonebook_list.append((name, number))
            print(f"| {name.ljust(20)} | {number.ljust(15)} |")
        print(f"{'-'*60}")
        self.sock.close()
        self.logger.info("Client down.")
        return phonebook_list

    def callnumber(self, name):
        """ Call server for a single phone number """
        self.logger.info(f"Client calling for phone number of {name}.")
        self.sock.send(("GET " + name).encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        response = data.decode('ascii')
        returnvalue = response
        if response.startswith("ERROR="):
            print(response[6:])
            return (name, None)
        else:
            name, number = response.split('=')
            number = number.rstrip(';')  # remove semicolon from the end of the number
            print(f"| {name.ljust(20)} | {number.ljust(15)} |")
            returnvalue = (name, number)
        self.sock.close()
        self.logger.info("Client down.")
        return returnvalue

    def close(self):
        """ Close socket """
        self.sock.close()
