import sys
val = int(sys.argv[1])
if val > 32768:
    val ^= ((2 ** 16) - 1)
    val = -1 *(val + 1)
print(val)
