import zmq
import time
import hashlib

MAPPERADDRESS = "tcp://127.0.0.1"

mapperports = [
    "5557",
    "5558",
    "5559",
]

SPLITTERADDRESS = "tcp://127.0.0.1:5556"


class Splitter:
    def __init__(self):
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUSH)
        self.publisher.bind(SPLITTERADDRESS)

    def start(self):
        with open('sentences.txt', 'r') as file:
            sentences = file.read().split('.')
            for sentence in sentences:
                self.publisher.send_string(sentence)
                # wait for a second before sending the next sentence
                time.sleep(1)


class Mapper:
    def __init__(self, reducercount: int, port: int):
        self.reducercount = reducercount
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect(SPLITTERADDRESS)
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(MAPPERADDRESS + ":" + str(port))

    def start(self):
        while True:
            sentence = self.receiver.recv_string()
            words = sentence.split(' ')
            for word in words:
                # Determine counter_id by hashing the word
                counter_id = hash(word) % self.reducercount
                # Send word with counter_id
                self.publisher.send_string(f"{counter_id}:{word}")
                time.sleep(1)  # wait for a second before sending the next word


class Reducer:
    def __init__(self, id):
        self.id = id
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.SUB)  # Change PULL to SUB
        for port in mapperports:
            self.receiver.connect(MAPPERADDRESS + ":" + str(port))
        # Subscribe to messages intended for this counter
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, f"{self.id}:")
        self.word_counts = {}

    def start(self):
        while True:
            message = self.receiver.recv_string()  # Receive message directly
            # Split the message into counter_id and word
            _, word = message.split(':')
            self.word_counts[word] = self.word_counts.get(word, 0) + 1
            print(f"Counter {self.id} Word counts: {self.word_counts}")
