import threading
import time

current = 0
bound = 4
msg = ["0","0","0","0","0"]
while True:
    count = 0
    temp = input()
    if temp == msg[current]:
            msg[current] = "0"
            if current != 0:
                current -= 1
    elif msg[current] == "0":
        msg[current] = temp
    elif current < bound:
        current = current + 1
        msg[current] = temp
        last_msg = temp
    print("\n")
    for count in range(5):
        print(msg[count])

