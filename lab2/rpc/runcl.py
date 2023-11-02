import rpc
import logging

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def pretty_print(obj, indent=0):
    for key, value in obj.__dict__.items():
        if isinstance(value, dict):
            print('\033[91m' + '\t' * indent + str(key) + '\033[0m')
            pretty_print(value, indent+1)
        else:
            print('\033[91m' + '\t' * indent + str(key) + ': ' + str(value) + '\033[0m')

base_list = rpc.DBList({'foo'})
waitthread = cl.append('bar', base_list, pretty_print)
waitthread.join()
print("Thread is done")

# print("Result: {}".format(result_list.value))

cl.stop()
