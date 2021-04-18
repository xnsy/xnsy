# 输入一个三位数，计算n的各个位数的和

n = int(input())
a = n // 100
b = (n % 100) // 10
c = (n % 100) % 10
d = n % 10
print(a,b,c,d)
e = a + b + d
print(e)