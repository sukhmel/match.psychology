import os
import sys
import pickle

i = 4
result = [['"имя"', '"возраст"', '"№"', '"эффект"',
           '"задание"', '"решение"', '"тип"', '"время"',
           '"отношение"', '"курс"', '"пол"', '"комментарий"']]

lines = [['"имя"', '"возраст"', '"курс"', '"пол"', '"комментарий"'] + ['"№"', '"эффект"',
           '"задание"', '"решение"', '"тип"', '"время"', '"отношение"']*8]

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
                    info = []
                    data = pickle.load(input, encoding='utf8')
                    try_append(data['user'], info, u'имя')
                    try_append(data['user'], info, u'возраст')
                    try_append(data['user'], info, u'курс')
                    try_append(data['user'], info, u'пол')
                    try_append(data, info, 'comment')

                    temp.extend(info[:2])
                    temp.extend(['','','','','','',''])
                    temp.extend(info[2:])
                    result.append(temp)
                    for index in range(len(data['result'])):
                        temp = []
                        line = data['result'][index]
                        info.append(str(index+1))
                        info.append('"' + line[3] + '"')
                        info.append('"' + line[0] + '"')
                        info.append('"' + line[1] + '"')
                        info.append('')
                        info.append(str(line[2]))
                        info.append('')
                        temp.extend(['',''])
                        temp.extend(info[-7:])
                        result.append(temp)
                    lines.append(info)

with open('../res/tables.csv', 'w') as output:
    output.write('\n'.join(map(';'.join, result)))
with open('../res/lines.csv', 'w') as output:
    output.write('\n'.join(map(';'.join, lines)))
