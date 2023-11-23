import zmq
import time
import hashlib

MAPPERADDRESS = "tcp://127.0.0.1"
SPLITTERADDRESS = "tcp://127.0.0.1:5556"

mapperports = [
    "5557",
    "5558",
    "5559",
]


def string_to_integer_hash(input_string):
    sha256 = hashlib.sha256()

    # Update the hash object with the input string's bytes
    sha256.update(input_string.encode('utf-8'))
    # Get the hexadecimal representation of the hash
    hash_hex = sha256.hexdigest()
    # Convert the hexadecimal hash to an integer
    hash_int = int(hash_hex, 16)

    return hash_int


class Splitter:
    def __init__(self):
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUSH)
        self.publisher.bind(SPLITTERADDRESS)

    def start(self):
        with open('sentences.txt', 'r', encoding='utf-8') as file:
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
                reducer_id = string_to_integer_hash(word) % self.reducercount
                print("sending word '" + word + "' to reducer " + str( reducer_id ))
                # Send word with counter_id
                self.publisher.send_string(f"{reducer_id}:{word}")
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
            print("Counter {self.id} Word counts:")
            words_with_counts = [f"{word}: {count}" for word, count in self.word_counts.items()]
            for i in range(0, len(words_with_counts), 5):
                print("\t".join(words_with_counts[i:i+5]))
