import os
import sys
import pickle

result = [['"имя"', '"возраст"'] + ['1']*3 + ['2']*3 + ['3']*3 + ['4']*3 + ['5']*3 +
          ['6']*3 + ['7']*3 + ['8']*3 + ['"курс"', '"пол"', '"комментарий"']]

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
                    for line in data['result']:
                        temp.append('"' + line[0] + '"')
                        temp.append('"' + line[1] + '"')
                        temp.append(str(line[2]).replace('.',','))
                    try_append(data['user'], temp, u'курс')
                    try_append(data['user'], temp, u'пол')
                    try_append(data, temp, 'comment')
                    result.append(temp)

with open('../res/res.csv', 'w') as output:
    output.write('\n'.join(map(';'.join, result)))
