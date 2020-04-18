# coding=utf-8
import requests
# step1单局游戏，返回单局游戏所猜次数，输入异常处理
def Guess_Number():
    result = requests.get('https://python666.cn/cls/number/guess/').json()
    Game_times = 0
    print(result)
    while True:
        Game_times += 1
        try:
            guess_num = eval(input('请输入一个1-100的整数，以回车结束:\n'))
            if guess_num > result:
                print("大了")
            elif guess_num < result:
                print("小了")
            else :
                print("恭喜,猜中！")
                return (Game_times)
        except :
            print('输入有误,请重新输入1-100的整数以回车结束:\n')
# 重复游戏，更新游戏记录
def Repeated_game(User_Name,Count_Round,Count_Times,Least_Times):
    choice = '是'
    while choice == "是":
        print("\n第%d次游戏开始" % (Count_Round + 1))
        count = Guess_Number()
        Count_Times += count
        if count < Least_Times:
            Least_Times = count
        Count_Round += 1
        print("%s已经进行了%d轮游戏，共猜了%d次,最少%d次猜对,平均每一轮猜了%.2f次"
              % (User_Name, Count_Round, Count_Times, Least_Times,Count_Times/Count_Round))
        choice = input("是否继续游戏（请输入'是'继续游戏，其他输入退出本次游戏）:\n")
    return ([User_Name, Count_Round, Count_Times, Least_Times, Count_Times/Count_Round])
# 依据用户名，返回用户游戏记录，没有就新建
def Check_Record(user_name):
    specified_userexist = False
    try:
        open("Game_History.txt", "rt")
    except:
        open("Game_History.txt", "x")
    data_archiving = [user_name, 0, 0, 100]
    with open("Game_History.txt", "rt") as f:
        users_data = f.read()
        if users_data == "":
            users_data = str([['User_Name','Count_Round','Count_Times','Least_Times']])
        users_data = eval(users_data)
        for user_data in users_data:
            if user_data[0] == user_name:
                data_archiving = user_data
                specified_userexist = True
                del users_data[users_data.index(user_data)]
    if specified_userexist == True:
        print("%s已经玩了%d轮游戏，最少%d次猜出答案，平均%.2f次猜出答案"
              % (user_data[0], user_data[1], user_data[3], user_data[2] / user_data[1]))
    else:
        print("您是新玩家，请开始您的第一次游戏吧！")
    return (data_archiving, users_data, specified_userexist)
# 游戏记录存储
def SaveData(data):
    with open("Game_History.txt", "wt") as users_data:
        users_data.write(str(data))
# 程序主模块
def main():
    user_name = input("请输入您的用户名：\n")
    user_data, users_data, specified_userexist = Check_Record(user_name)
    update_data = Repeated_game(user_data[0], user_data[1], user_data[2], user_data[3])
    users_data.append(update_data)
    SaveData(users_data)

main()
