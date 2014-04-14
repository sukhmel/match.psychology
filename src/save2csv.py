import os
import sys
import pickle

i = 4
result = [['"имя"', '"возраст"', '"№"', '"эффект"',
           '"задание"', '"решение"', '"тип"', '',
           '"отношение"', '"курс"', '"пол"', '"комментарий"']]

def try_append(src, dst, key):
    try:
        if src[key] is None:
            dst.append('')
        else:
            dst.append('"'+str(src[key]).strip()+'"')
            
    except KeyError:
        dst.append('')

if len(sys.argv) < 2:
    for root, dirs, files in os.walk('../res'):
        for name in files:
            if name.endswith('.save'):
                with open(os.path.join(root, name), 'rb') as input:
                    temp = []
                    data = pickle.load(input, encoding='utf8')
                    try_append(data['user'], temp, u'имя')
                    try_append(data['user'], temp, u'возраст')
                    temp.extend(['','','','','','',''])
                    try_append(data['user'], temp, u'курс')
                    try_append(data['user'], temp, u'пол')
                    try_append(data, temp, 'comment')
                    result.append(temp)
                    for index in range(len(data['result'])):
                        temp = []
                        line = data['result'][index]
                        temp.extend(['',''])
                        temp.append(str(index+1))
                        temp.append('"' + line[3] + '"')
                        temp.append('"' + line[0] + '"')
                        temp.append('"' + line[1] + '"')
                        temp.append('')
                        temp.append(str(line[2]))#.replace('.',',')
                        result.append(temp)

with open('../res/res.csv', 'w') as output:
    output.write('\n'.join(map(';'.join, result)))
