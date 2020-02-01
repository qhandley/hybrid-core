import signal
import time

def SIG(sig, frame):
    print("ALARM")
    exit()
signal.signal(signal.SIGALRM, SIG)
signal.alarm(5)
temp = input("this should timeout")
signal.alarm(0)
print("hold to see if alarm still goes")
time.sleep(10)
