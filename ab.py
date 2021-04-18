import random
a = input()
a = int(a)
b = input()
b = int(b)

a = random.randint(a,b) # 选取ab间的随机整数
b = random.randint(a,b)
print(a,b,a+b)