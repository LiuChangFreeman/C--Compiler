from __future__ import print_function
A=open('StatesA.txt','r').read().split('\n\n')
B=open('StatesB.txt','r').read().split('\n\n')
count=0
for state in A:
    if not state in B:
        count+=1
        print(state+'\n')
print(count)