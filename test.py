import threading
import time
def function_to_be_executed_concurrently():
    for i in range(5):
        time.sleep(1)
        print('running in separate thread', i)

thread = threading.Thread(target=function_to_be_executed_concurrently)
thread.start()

for i in range(5):
    time.sleep(1)
    print('running in main thread', i)