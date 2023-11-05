import zmq
import time
import hashlib

class Splitter:
    def __init__(self):
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUSH)
        self.publisher.bind("tcp://*:5556")

    def start(self):
        with open('sentences.txt', 'r') as file:
            sentences = file.read().split('.')
            for sentence in sentences:
                self.publisher.send_string(sentence)
                time.sleep(1)  # wait for a second before sending the next sentence


class Mapper:
    def __init__(self, reducercount: int):
        self.reducercount = reducercount
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect("tcp://localhost:5556")
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:5557")

    def start(self):
        while True:
            sentence = self.receiver.recv_string()
            words = sentence.split(' ')
            for word in words:
                counter_id = hash(word) % self.reducercount  # Determine counter_id by hashing the word
                self.publisher.send_string(f"{counter_id}:{word}")  # Send word with counter_id
                time.sleep(1)  # wait for a second before sending the next word

class Reducer:
    def __init__(self, id):
        self.id = id
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.SUB)  # Change PULL to SUB
        self.receiver.connect("tcp://localhost:5557")
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, f"{self.id}:")  # Subscribe to messages intended for this counter
        self.word_counts = {}

    def start(self):
        while True:
            message = self.receiver.recv_string()  # Receive message directly
            _, word = message.split(':')  # Split the message into counter_id and word
            self.word_counts[word] = self.word_counts.get(word, 0) + 1
            print(f"Counter {self.id} Word counts: {self.word_counts}")
