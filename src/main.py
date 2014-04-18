#!/usr/bin/python
# coding=utf8

from os.path         import isfile, walk
from pickle          import dump
from numpy           import sin, deg2rad, exp
from copy            import copy, deepcopy
from numpy.random    import uniform as random
from random          import sample, shuffle
from psychopy        import visual, event, core, gui
from psychopy.iohub  import launchHubServer, EventConstants
from matplotlib.path import Path as mpl_Path


def ask_user():
    info = {u'имя': '',
            u'возраст': 18,
            u'пол': [u'муж',
                    u'жен'],
            u'курс': 2,
            u'версия': 0.92}
    infoDlg = gui.DlgFromDict(dictionary=info,
                              title=u'Введите ваши данные',
                              order=[u'имя',
                                     u'возраст',
                                     u'курс',
                                     u'пол',
                                     u'версия'],
                              fixed=[u'версия'])

    result = dict()
    if infoDlg.OK:
        for k in info:
            if isinstance(info[k], basestring):
                s = info[k].encode('utf8')
            else:
                s = info[k]
            result[k.encode('utf8')] = s
        return result
    else:
        return None


user = ask_user()

if user is None:
    exit(-1)

debug = False

io = launchHubServer()

display  = io.devices.display
keyboard = io.devices.keyboard
mouse    = io.devices.mouse

size = map(lambda x: int(x*1.0), display.getPixelResolution())

viewScale = map(lambda x: float(x)/min(size), size)
viewScale.reverse()

win = visual.Window( size
                   , units='pix'
                   , rgb=[-1, -1, -1]
                   , fullscr=True
                   , winType='pyglet'
                   , screen=0)

oldMouse = event.Mouse()

imageFiles = [ r'../img/cap_match_1.png'
             , r'../img/cap_match_0.png'
             , r'../img/match_1.png'
             , r'../img/match_0.png'
             , r'../img/blink_1/%i.png'
             ]

angles  = [-90, -30, -15, 0, 15, 30, 90]

globalScale     = size[0] / 8

default = { 'scale'  : None
          , 'image'  : imageFiles[2]
          , 'anim'   : None
          , 'size'   : None
          , 'pulse'  : None
          , 'flicker': None
          , 'begin'  : None
          , 'cycle'  : True }

animated = copy(default)
animated['image'] = imageFiles[-1]
animated['anim']  = [2.0, .05, .05, .05, .05, .05, .05, .05]

defTask = { 'description': 'Нужно переложить одну спичку.'
          , 'help': 'I = 1, V = 5, X = 10, L = 50, C = 100, D = 500, M = 1000'
          , 'success': 'Верно!'
          , 'amount': 1
          , 'setup': None}


def spawn_message(text, position):
    return visual.TextStim( win
                          , pos=position
                          , alignHoriz='center'
                          , alignVert ='center'
                          , height=40
                          , text=text
                          , autoLog=False
                          , wrapWidth=size[0]*.9)


def normalize(angle):
    return (angle + 180) % 360 - 180


def vertical(x):
    return x.ori % 180 == 0


def symmetric(x, y):
    return normalize(x.ori) == - normalize(y.ori)


def horizontal(x):
    return abs(normalize(x.ori)) == 90


def current_image(style, time=0):
    quotient = (int(style['cycle']) and [2] or [1])[0]
    interval = quotient * sum(style['anim'])
    begin = time % interval
    total = quotient * len(style['anim'])
    for index in range(total):
        current = index
        if quotient != 1:
            current = min(index, total - index - 1)
        begin -= style['anim'][current]
        if begin < 0:
            index = current
            break
    return style['image'] % index


def spawn_match(style, position, angle):
    style = copy(style)
    style['pos'] = position
    style['ori'] = angle

    if style['scale'] is None:
        style['scale'] = globalScale

    if style['anim'] is None:
        begin = random(0, 4)
    else:
        begin = sum(style['anim'])

    if style['begin'] is None:
        style = copy(style)
        style['begin'] = begin

    if style['anim'] is not None:
        imageName = current_image(style)
    else:
        imageName = style['image']

    image = visual.ImageStim( win         = win
                            , name        ='match'
                            , image       = imageName
                            , ori         = angle
                            , pos         = position
                            , size        = style['size']
                            , color       = [1, 1, 1]
                            , colorSpace  = u'rgb'
                            , opacity     = 1
                            , flipHoriz   = False
                            , flipVert    = False
                            , texRes      = 128
                            , interpolate = False)

    if style['size'] is None:
        image.size = map(lambda x: x * style['scale'] / max(image.size), image.size)
        style['size'] = image.size

    return (image, style)


def spawn_sign(style, sign, position):
    sign = sign.lower()

    result = []

    if style['scale'] is not None:
        scale = style['scale']
    else:
        scale = globalScale

    ones  = { 'i' : [0]
            , '2' : [-1, 1]
            , '3' : [-1, 0, 1]
            , '4' : [-1]
            , '6' : [+1] }

    if len(sign) == 1 and \
       sign in 'i2346':
        delta = scale / 3
        for x in ones[sign]:
            result.append(
                spawn_match( style
                           , [ position[0] + x * delta
                             , position[1]]
                           , 0))
        if sign in '46':
            result.extend(
                spawn_sign( style
                          , 'v'
                          , [ position[0] - x * delta / 2
                            , position[1]]))

    if sign == 'v' or sign == 'm':
        delta = scale / 8
        for x in [-1, 1]:
            result.append(
                spawn_match( style
                           , [ position[0] + x * delta
                             , position[1]]
                           , x * 15))

    if sign == 'l':
        delta = scale / 2
        for x in [-1, 0]:
            result.append(
                spawn_match( style
                           , [ position[0] + x * delta
                             , position[1] - 0.5 * (x + 1) * scale]
                           , -(x + 1) * 90))

    if sign == 'x':
        for x in [-1, 1]:
            result.append(
                spawn_match( style
                           , [ position[0]
                             , position[1]]
                           , x * 30))

    if sign == 'c':
        for x in [-1, 0, 1]:
            result.append(
                spawn_match( style
                           , [ position[0] + (abs(x) - 1) * scale / 2
                             , position[1] + 0.5 * x * scale]
                           , x * 90))

    if sign == 'm':
        delta = scale / 4
        for x in [-1, 1]:
            result.append(
                spawn_match( style
                           , [ position[0] + x * delta
                             , position[1]]
                           , 0))

    if sign == '+':
        for x in [0, 1]:
            result.append(
                spawn_match( style
                           , [ position[0]
                             , position[1]]
                           , x * 90))

    if sign == '-':
        result.append(
                spawn_match( style
                           , [ position[0]
                             , position[1]]
                           , 90))

    if sign == '=':
        delta = scale / 4
        for y in [-1, 1]:
            result.append(
                spawn_match( style
                           , [ position[0]
                             , position[1] + y * delta]
                           , 90))

    if sign == 'd':
        delta = scale / 5
        for x in [-1, 0, 1]:
            result.append(
                spawn_match( style
                           , [ position[0] + (abs(x) - 1) * delta * 2
                             , position[1] - x * delta]
                           , x * 60))

    return result


def spawn_number(style, num, position):
    result = []
    try:
        recipe = int_to_roman(num)
        delta = max(style['size']) / 2
        for x in range(len(recipe)):
            place   = x - (len(recipe) - 1) / 2.0
            letter  = recipe[x]
            result.extend(
                spawn_sign( style
                          , letter.lower()
                          , [position[0] + place * delta, position[1]]))
    except ValueError:
        pass

    return result


def spawn_value(style, value, position):
    result = []
    try:
        result.extend(
            spawn_number( style
                        , int(value)
                        , position))
    except ValueError:
        result.extend(
            spawn_sign( style
                      , value.lower()
                      , position))
    return result


def spawn_expression(style, letters, position, width):
    result = []
    letters = letters.lower()
    if len(style) == 1 or len(style) == len(letters):
        style = style * (len(letters)/len(style))
    else:
        style = [style] * len(letters)

    delta   = 1.0 * width / len(letters)
    spaces  = [delta / (1 + ('i' in a + b and [.3] or [0])[0]
                          * (       a == b and [5] or [1])[0])
               for (a, b) in zip(letters, letters[1:])]
    begin = (width - sum(spaces))/2
    for x in range(len(letters)):
        result.extend(
            spawn_sign( style  [x]
                      , letters[x]
                      , [position[0] - width/2 + sum(spaces[:x]) + begin, position[1]]))
    return result


def translate(expression):
    parts = expression.split(' ')
    for x in range(len(parts)):
        try:
            parts[x] = int_to_roman(int(parts[x]))
        except ValueError:
            pass
    return ''.join(parts)


def int_to_roman(input):
    """
    Convert an integer to Roman numerals. Created by Paul Winkler.
    http://code.activestate.com/recipes/81611-roman-numerals/
    """
    if type(input) != type(1):
        raise TypeError, "expected integer, got %s" % type(input)
    if not 0 < input < 4000:
        raise ValueError, "Argument must be between 1 and 3999"
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = ""
    for i in range(len(ints)):
        count = int(input / ints[i])
        result += nums[i] * count
        input -= ints[i] * count
    return result


def roman_to_int(input):
    """
    Convert a roman numeral to an integer. Created by Paul Winkler.
    http://code.activestate.com/recipes/81611-roman-numerals/
    """
    if not isinstance(input, basestring):
        raise TypeError, "expected string, got %s" % type(input)
    input = input.upper()
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    ints = [1000, 500, 100, 50,  10,  5,   1]
    places = []
    for c in input:
        if not c in nums:
            raise ValueError, "input is not a valid roman numeral: %s" % input
    for i in range(len(input)):
        c = input[i]
        value = ints[nums.index(c)]
        # If the next place holds a larger number, this value is negative.
        try:
            nextvalue = ints[nums.index(input[i +1])]
            if nextvalue > value:
                value *= -1
        except IndexError:
            # there is no next place.
            pass
        places.append(value)
    sum = 0
    for n in places: sum += n
    # Easiest test for validity...
    if int_to_roman(sum) == input:
        return sum
    else:
        raise ValueError, 'input is not a valid roman numeral: %s' % input


def overlaps(left, right):
    poly_left  = mpl_Path( left, closed=True)
    poly_right = mpl_Path(right, closed=True)
    return poly_left.intersects_path(poly_right, filled=True)


def decompose(array):
    result = []
    for match in array:
        epsilon = min(match.size)
        delta   = max(match.size)

        left = match.verticesPix
        local = {match}
        for i in range(len(result) - 1, -1, -1):
            if match in result[i]:
                local = local.union(result[i])
                result.remove(result[i])

        for test in array:
            if test not in local:
                right = test.verticesPix
                if overlaps(left, right):
                    local.add(test)

        result.append(local)

    equalityCandidates = [x for x in result if len(x) == 1 and horizontal(list(x)[0])]
    for x in equalityCandidates:
        result.remove(x)

    equalityCandidates = [list(x)[0] for x in equalityCandidates]
    pushBackCandidates = range(len(equalityCandidates))

    for x in range(len(equalityCandidates)):
        for y in range(len(equalityCandidates)):
            if x != y and \
               x in pushBackCandidates and \
               y in pushBackCandidates:
                match = equalityCandidates[x]
                test  = equalityCandidates[y]
                if abs(test.pos[0] - match.pos[0]) < epsilon and\
                   abs(test.pos[1] - match.pos[1]) > epsilon / 2:
                    result.append({test, match})
                    pushBackCandidates.remove(x)
                    pushBackCandidates.remove(y)

    for x in pushBackCandidates:
        result.append({equalityCandidates[x]})

    return result


def remove(condition, array):
    return [x for x in array if not condition(x)]


def recognize(list):
    result   = ""
    position = [-size[0]*9000, -size[1]*9000]
    length   = len(list)
    if 0 < length < 5:
        epsilon = min(list[0].size)
        delta   = max(list[0].size)

        if length == 1:
            position = list[0].pos
            if vertical(list[0]):
                result = "I"
            if horizontal(list[0]):
                result = " - "

        if length == 2:
            if symmetric(list[0], list[1]) and \
               abs(list[0].pos[1] - list[1].pos[1]) < epsilon:
                if abs(list[0].pos[0] - list[1].pos[0]) < epsilon:
                    result   = "X"
                if abs(list[0].pos[0] - list[1].pos[0]) > delta * abs(sin(deg2rad(list[0].ori))) - epsilon:
                    result   = "V"
                position = [ (list[1].pos[0] + list[0].pos[0]) / 2
                           , (list[1].pos[1] + list[0].pos[1]) / 2]
            else:
                v_c = 0
                h_c = 0
                v = None
                h = None
                if vertical(list[0]):
                    v = list[0]
                    v_c += 1
                if horizontal(list[0]):
                    h = list[0]
                    h_c += 1
                if vertical(list[1]):
                    v = list[1]
                    v_c += 1
                if horizontal(list[1]):
                    h = list[1]
                    h_c += 1

                if h_c != 0:
                    position = copy(h.pos)

                if v_c == 0 and h_c == 2:
                    result = " = "
                    position[1] = min(map(abs,[list[0].pos[1], list[1].pos[1], (list[0].pos[1] + list[1].pos[1])/2]))

                if v_c == 1 and h_c == 1:
                    if abs(v.pos[1] - h.pos[1]) < epsilon and \
                       abs(v.pos[0] - h.pos[0]) < epsilon:
                        result = " + "

                    if h.pos[0] - v.pos[0] > delta / 2 - epsilon and\
                       v.pos[1] - h.pos[1] > delta / 2 - epsilon:
                        result = "L"

        if length == 3:
            closed = overlaps(list[0].verticesPix, list[1].verticesPix) and \
                     overlaps(list[2].verticesPix, list[1].verticesPix) and \
                     overlaps(list[0].verticesPix, list[2].verticesPix)
            list = remove(vertical, list)
            if len(list) == 2 and \
               abs(normalize(list[0].ori)) == abs(normalize(list[1].ori)) and \
               abs(list[0].pos[0] - list[1].pos[0]) < epsilon:
                result = (closed and ["D"] or ["C"])[0]
                position = (list[1].pos + list[0].pos) / 2

        if length == 4:
            list = remove(lambda x: x.ori == 0, list)
            if len(list) == 2 and \
               list[0].ori == - list[1].ori and \
               list[0].ori % 90 != 0:
                result = "M"
                position = [ (list[1].pos[0] + list[0].pos[0]) / 2
                           , (list[1].pos[1] + list[0].pos[1]) / 2]

    return (result, position)


def normalize_matches(recognized):
    normalized = []
    for part in recognized.strip().split(' '):
        if part.isalpha():
            try:
                normalized.append(str(roman_to_int(part)))
            except ValueError:
                normalized.append(part)
            except TypeError as e:
                print e
        else:
            normalized.append(part)
    normalized = ' '.join(normalized)
    really     = []
    for part in normalized.split('='):
        try:
            really.append('%i' % eval(part))
        except:
            really.append('???')

    normalized += ' (%s)' % ' = '.join(really)

    return (normalized, really)


def read_matches(array):
    resolved = True

    decision = []
    for s in decompose(array):
        try:
            thing = recognize(list(s))
            decision.append(thing)
            if len(thing[0]) == 0:
                resolved = False
        except Exception as e:
            print(e.message)
    recognized = ''.join(map(lambda x: x[0], sorted(decision, key=lambda x: x[1][0])))

    normalized, really = normalize_matches(recognized)

    ys = sorted(map(lambda x: x[1][1], decision))
    if len(ys) > 2:
        inner = ys[1:-1]
        mean = sum(inner)/len(inner)
        delta = max(map(lambda x: abs(x - mean), inner))
        differ = max(abs(ys[0] - mean), abs(ys[-1] - mean))
        if differ > delta + globalScale/5:
            resolved = False
    else:
        resolved = False

    try:
        if len(really) > 1:
            for statement in really:
                resolved &= int(really[0]) == int(statement)
        else:
            resolved = False
    except ValueError:
        resolved = False

    return (resolved, recognized, normalized)


def pulse_function(time, k):
    return (1 + k * (sin(time) + 0) / (10 * exp(time/20)))


def global_scale_pulse(k, size):
    return scale_pulse(globalScale, k, size)


def scale_pulse(scale, k, size):
    return pulse(scale * k / max(size), size)


def pulse(k, size):
    return map(lambda x: k * x, size)


def draw(objects, time):
    for dict in objects:
        obj   = dict['match']
        style = dict['style']
        localTime = float(style['begin']) + time
        if style.has_key('anim') and style['anim'] is not None:
            obj.setImage(current_image(style, localTime ))
        if style.has_key('pulse') and style['pulse'] is not None:
            obj.setSize(style['pulse'](localTime , obj.size))
        if style.has_key('flicker') and style['flicker'] is not None:
            obj.setOpacity(style['flicker'](localTime ))

        obj.draw()

    win.flip()


def load_data(filename, kind, default):
    result = {}
    with open(filename) as incoming:
        for data in incoming.read().split('\n\n'):
                if data.startswith('# %s' % kind):
                    into = copy(default)
                    lines = data.split('\n')
                    for line in lines[1:]:
                        if line != '':
                            name, content = line.split(':')
                            if '[f]' in name:
                                content = map(float, content.split(','))
                            elif '[s]' in name:
                                content = map(lambda x: x.strip(), content.split(','))
                            else:
                                content = content.strip()
                            into[name.split('[')[0]] = content

                    if ':' in lines[0]:
                        result[lines[0].split(':')[1].strip()] = into
                    else:
                        result[len(result)] = into

    return result


def prepare_matches(matches, setup, styleSet, task):
    expression = translate(task['expression'])
    styles = []
    for letter in expression:
        if letter.isalnum():
            spec = 'number'
        else:
            spec = 'operator'

        temp = default

        if setup is not None and setup.has_key(spec):
            if styleSet is not None:
                if styleSet.has_key(setup[spec]):
                    temp = copy(styleSet[setup[spec]])
                else:
                    if styles.has_key('default'):
                        temp = copy(styleSet['default'])

        if temp.has_key('pulse_name'):
            temp['pulse'] = pulses[temp['pulse_name']]

        if temp.has_key('flicker_name'):
            temp['flicker'] = flickers[temp['flicker_name']]

        styles.append(temp)
    for image, style in spawn_expression(styles
            , expression
            , [0, 0]
            , size[0]):
        matches.append({'match': image, 'style': style})

    return expression


def test_solution(solution):
    normalized, really = normalize_matches(solution)
    resolved = len(really) > 1

    if resolved:
        for statement in really:
            resolved &= int(really[0]) == int(statement)

    return resolved


def compare(expression, solution):
    ok = True
    amount = 0
    source = expression.split()
    result = solution.split()
    for index in range(len(source)):
        a = source[index]
        b = result[index]
        if a != b:
            if len(a) == len(b):
                pass
    raise "not implemented"


def execute_task(task, setup=None, styleSet=None):
    spent = 0
    resolved = False
    solution = ''
    input_timer = core.Clock()

    romanMessage = spawn_message('', (0.0,-(size[1]/4)))
    solveMessage = spawn_message('', (0.0,-(size[1]/3)))

    hint = spawn_message(task['description'], (0.0, size[1]/3))
    help = spawn_message(task['help'], (0.0, size[1]/4))

    clock = core.Clock()
    clock.reset()

    matches = []

    expression = prepare_matches(matches, setup, styleSet, task)

    while not resolved:
        time = clock.getTime()

        if debug:
            solveMessage.draw()

        romanMessage.setText(solution)
        romanMessage.draw()

        hint.draw()
        help.draw()
        draw(matches, time)

        kb_events = keyboard.getEvents()

        io.clearEvents()
        event.clearEvents()

        for evt in kb_events:
            if evt.type == EventConstants.KEYBOARD_PRESS:
                if evt.key_id == 27:  # Escape
                    io.quit()
                    core.quit()

                start = solution == ''

                if evt.key.lower() in u"ivxlcdm-+=":
                    if solution[-1:].isalpha() != evt.key.isalpha():
                        solution += u" "
                    solution += evt.key.upper()

                if evt.key_id == 13: # Enter
                    resolved = solution.decode().strip() in task['solution']
                    if not resolved:
                        solution = ''

                if evt.key_id == 35:
                    resolved = True

                if evt.key_id == 8: # Backspace
                    solution = solution[:-1].strip()

                if solution != '' and start:
                    input_timer.reset()

                if (solution == '' and not start) or resolved:
                    spent -= input_timer.getTime()

                if resolved:
                    spent += clock.getTime()

    inform(task['success'])

    result = [''.join([(a.isalnum() and [a] or [" " + a + " "])[0] for a in expression]), solution, spent]

    return result


def split_in_groups(dict, key):
    result = {}
    for value in dict.values():
        if result.has_key(value[key]):
            result[value[key]].append(value)
        else:
            result[value[key]] = [value]
    return result


def reset(array, amount, but=None):
    resetted = []
    for object in array:
        match = object['match']
        style = object['style']
        if match.pos[0] != style['pos'][0] or \
           match.pos[1] != style['pos'][1] or \
           match.ori != style['ori']:
            resetted.append((match, style))
    if len(resetted) > amount:
        for match, style in resetted:
            if match is not but:
                match.pos = style['pos']
                match.ori = style['ori']


pulses = { 'grow'   : lambda t, size: global_scale_pulse(pulse_function(t, +1.0), size)
         , 'shrink' : lambda t, size: global_scale_pulse(pulse_function(t, -1.0), size) }

flickers = { 'fast' : lambda t: (sin(t*5) + 2) / 3
           , 'slow' : lambda t: (sin(t*2) + 2) / 3 }

io.clearEvents('all')

demo_timeout_start = core.getTime()


def inform(what):
    lines = (what + '#Для продолжения нажмите любую клавишу.').split('#')
    text = []
    length = len(lines)
    for index in range(length):
        text.append(spawn_message(lines[index], (0.0, (size[1] / 2) - 1.0 * size[1] * (index + 1) / (length + 1))))

    while len(event.getKeys()) == 0 and not any(oldMouse.getPressed()):
        for one in text:
            one.draw()
        win.flip()

    if 'escape' in event.getKeys():
        io.quit()
        core.quit()

    while any(oldMouse.getPressed()) or len(event.getKeys()) != 0:
        event.clearEvents()


if __name__ == '__main__':
    seed = len(walk('../res/'))

    experiment = dict()

    experiment['user'] = user

    tests = load_data('../data/tasks.txt',    'task', defTask)
    styles = load_data('../data/styles.txt', 'style', default)
    setups = load_data('../data/setups.txt', 'setup', {})
    setups['default'] = None

    tasks = []
    result = []

    for i in sorted(tests.keys()):
        if tests[i]['setup'] is None:
            setup = 'default'
        elif tests[i]['setup'] is 'random':
            setup = sample(setups.keys(), 1)[0]
        elif isinstance(tests[i]['setup'], basestring):
            setup = tests[i]['setup']
        else:
            setup = tests[i]['setup'][seed % len(tests[i]['setup'])]

        temp = (tests[i], setup)
        tasks.append(temp)

    inform('Ваша задача — как можно быстрее решить головоломку, мысленно переставив \
одну из спичек, образующие выражение, таким образом, чтобы получилось верное равенство.#\
После того, как вы нашли решение, введите его с клавиатуры и нажмите [Enter].#Если решение \
неверно, введённый текст будет стёрт и ввод решения следует начать заново.#В задачах используются только \
операторы сложения и вычитания.')

    inform('Пропустить текущее задание нельзя.#[Esc] прекращает эксперимент в любой момент.')

    for task, setup in tasks:
        result.append(execute_task(task, setups[setup], styles) + [setup])

    time = 0
    try:
        time = sum(map(lambda x: x[2], result))
    except:
        pass

    inform('Поздравляем, %s, вы завершили эксперимент за %i минут %2.2f секунд.' %
           (user['имя'], int(time/60), time % 60))

    experiment['result'] = result
    win.close()

    comment = gui.Dlg(title=u'Обратная связь')
    comment.addField(u'Ваши комментарии', 80*' ', color='blue')
    comment.show()
    if comment.OK:
        experiment['comment'] = comment.data[0].strip()
    else:
        experiment['comment'] = None

    index = 0
    save = '../res/%i.save'
    while isfile(save % index):
        index += 1

    with open(save % index, 'wb') as data:
        dump(experiment, data)

    for k in user:
        print("%s : %s" % (k, str(user[k])))

    for unit in result:
        print ("%s -> %s in %f @ %s" % tuple(unit))