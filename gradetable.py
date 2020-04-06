# coding=utf-8
header = []
stu_grade = []
grade_table = []
with open('report.txt',encoding='utf-8')as f:
    for index,line in enumerate(f):
        line = line.strip() # 去掉空格
        if index == 0:
            a ='名次 '+ line+ ' 总分 平均分'
            header = [a.split()]
# 接下来按行计算每个人的总分，平均分
        else:
            stu_grade = line.split()
            sum = 0
            for i in stu_grade[1:]:
                sum += float(i)
            stu_grade.append(str(sum))
            stu_grade.append('%.2f'%(sum/9))
            grade_table.append(stu_grade)

# 按照总分降序排序
grade_table.sort(key=lambda x:x[10],reverse=True)

# 接下来计算班级各科平均分，总分，平均平均分，作为文本的第二行输出
average_score = []
for num in range(11):
    average_score.append(0)
# 增加名次，各科成绩求和
j=1
for m in grade_table:
    m.insert(0, j)
    j += 1
    subject_score = m[2:]
    for n in range(11):
        score = float(subject_score[n])
        sum_obj = float(average_score[n])
        average_score[n] = '%.2f'%(sum_obj + score)
# 插入0，平均，计算班级平均成绩
for k in range(11):
    m = float(average_score[k])
    average_score[k] = '%.2f' % float(m / (j-1))
average_score.insert(0,'0')
average_score.insert(1,'平均')

# 低于60分的替换为不及格
for stu_scores in grade_table:
    for num in range(2,11):
        if float(stu_scores[num])<60.0:
            stu_scores[num]='不及格'
report_list = header + [average_score] + grade_table

# 写入文件
with open('my result.txt','w',encoding='utf-8') as f:
    for student_scores in report_list:
        for object_scores in student_scores:
            f.write(str(object_scores)+'\t')
        f.write('\n')
