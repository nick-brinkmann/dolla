from cs50 import get_string
import re

def verify(cnum):
    length = len(cnum)

    if length not in [13, 15, 16]:
        print("INVALID")
        return False

    # reverses order of the string of numbers
    reverse = cnum[length:: -1]

    # Multiplies every other number, in an odd index, by 2 and adds it to a total
    check = 0
    for i in range(length):
        if i % 2 != 0:
            tmp = int(reverse[i]) * 2
            tmp = str(tmp)
            check += sum(map(int, tmp))

    # Adds every other number in an even index
    total = 0
    for j in range(length):
        if j % 2 == 0:
            total += int(reverse[j])

    # Combines both totals together
    total = total + check

    # If mathematically the number is possible, checks if it corresponds to a specific type of card
    if total % 10 == 0:
        if cnum[0] + cnum[1] in ["34", "37"] and length == 15:
            return True

        elif cnum[0] + cnum[1] in ["51", "52", "53", "54", "55"] and length == 16:
            return True

        elif cnum[0] == "4" and length in [13, 16]:
            return True

        else:
            return False

    else:
        return False