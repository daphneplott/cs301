from random import randint
from matplotlib import pyplot as plt


mylist =[]

plt.hist(mylist,bins=100)

plt.show()

print(len(mylist))
for item in mylist:
    if item > 100:
        print(item)
        