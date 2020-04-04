#BMI 指数（即身体质量指数，简称体质指数又称体重，英文为Body Mass Index，简称BMI），是用体重公斤数除以身高米数平方得出的数字
#BMI < 18.5 体重偏轻
#18.5 <= BMI < 24 体重正常
#BMI >= 24 体重偏重
#设计一个BMI计算器吧，看看自己体重是否正常。
#输入：身高、体重值
#输出：BMI 指数、是否正常
height,weight = eval(input("请输入身高(m)体重(kg)逗号隔开\n"))
BMI = weight / pow(height,2)
print("BMI=%.1f" % BMI)
if BMI <18.5:
    stature = "体重偏轻"
elif 18.5 <= BMI <= 24:
    stature = "体重正常"
elif BMI >=24:
    stature = "体重偏重"
print("{0}".format(stature))





"""print("BMI数值为:{:.2f}".format((bmi)))
who = ""
if bmi < 18.5:
    who = "偏瘦"
elif 18.5 <= bmi < 25:
    who = "正常"
elif 25 <= bmi < 30:
    who = "肥胖"
print("BMI 指标为:国际'{0}'".format(who))"""