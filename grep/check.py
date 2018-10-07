import bonus
from ClassElementWithIndex import  ElementWithIndex
import grep

l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

prev = bonus.GetContextInfo(l, 4, 2, 2)
new = bonus.GetContextInfo(l, 5, 2, 2)

result = bonus.FullJoin(prev, new)

print(result.ListOfElements)
print(prev.ListOfElements)
# print(new.ListOfElements)
# print(result.ListOfElements)

