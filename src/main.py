from numpy           import sin, deg2rad
from psychopy        import visual, event, core
from psychopy.iohub  import launchHubServer, EventConstants
from matplotlib.path import Path as mpl_Path

io = launchHubServer()

display  = io.devices.display
keyboard = io.devices.keyboard
mouse    = io.devices.mouse

size = map(lambda x: int(x*0.8), display.getPixelResolution())

viewScale = map(lambda x: float(x)/min(size), size)
viewScale.reverse()

win = visual.Window( size
                   , units='pix'
                   , fullscr=False
                   , screen=1)

imageFiles = [ r'../img/match_1.png'
             , r'../img/match_0.png'
             ]

matches = []


default = { 'scale' : 75
          , 'image' : imageFiles[0] }


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


def spawn_match (style, position, angle):
    image = visual.ImageStim( win         = win
                            , name        ='match_%i' % len(matches)
                            , image       = style['image']
                            , ori         = angle
                            , pos         = position
                            , size        = [0.1 * style['scale'], style['scale']]
                            , color       = [1,1,1]
                            , colorSpace  = u'rgb'
                            , opacity     = 1
                            , flipHoriz   = False
                            , flipVert    = False
                            , texRes      = 128
                            , interpolate = False)
    matches.append(image)

def spawn_sign(style, sign, position):
    scale = style['scale']

    ones  = { 'i' : [0]
            , '2' : [-1, 1]
            , '3' : [-1, 0, 1]}

    if len(sign) == 1 and \
       sign in 'i23':
        delta = scale / 4
        for x in ones[sign]:
            spawn_match( style
                       , [ position[0] + x * delta
                         , position[1]]
                       , 0)

    if sign == 'v' or sign == 'm':
        delta = scale / 8
        for x in [-1, 1]:
            spawn_match( style
                      , [ position[0] + x * delta
                        , position[1]]
                      , x * 15)

    if sign == 'l':
        delta = scale / 2
        for x in [-1, 0]:
            spawn_match( style
                      , [ position[0] + x * delta
                        , position[1] - 0.5 * (x + 1) * scale]
                      , -(x + 1) * 90)

    if sign == 'x':
        for x in [-1, 1]:
            spawn_match( style
                      , [ position[0]
                        , position[1]]
                      , x * 30)

    if sign == 'c':
        for x in [-1, 0, 1]:
            spawn_match( style
                      , [ position[0] + (abs(x) - 1) * scale / 2
                        , position[1] + 0.5 * x * scale]
                      , x * 90)

    if sign == 'm':
        delta = scale / 4
        for x in [-1, 1]:
            spawn_match( style
                      , [ position[0] + x * delta
                        , position[1]]
                      , 0)

    if sign == '+':
        for x in [0, 1]:
            spawn_match( style
                      , [ position[0]
                        , position[1]]
                      , x * 90)

    if sign == '-':
        spawn_match( style
                  , [ position[0]
                    , position[1]]
                  , 90)

    if sign == '=':
        delta = scale / 4
        for y in [-1, 1]:
            spawn_match( style
                      , [ position[0]
                        , position[1] + y * delta]
                      , 90)

    if sign == 'd':
        delta = scale / 5
        for x in [-1, 0, 1]:
            spawn_match( style
                      , [ position[0] + (abs(x) - 1) * delta * 2
                        , position[1] - x * delta]
                      , x * 60)


def spawn_number(style, num, position):
    try:
        recipe = int_to_roman(num)
        delta = style['scale'] / 2
        for x in range(len(recipe)):
            place   = x - (len(recipe) - 1) / 2.0
            letter  = recipe[x]
            spawn_sign( style
                     , letter.lower()
                     , [position[0] + place * delta, position[1]])
    except ValueError:
        pass


def spawn_value(style, value, position):
    try:
        spawn_number( style
                   , int(value)
                   , position)
    except ValueError:
        spawn_sign( style
                 , value.lower()
                 , position)


def spawn_expression(style, letters, position, width):
    letters = letters.lower()
    if len(style) == 1 or len(style) == len(letters):
        style = style * (len(letters)/len(style))
    else:
        style = [style] * len(letters)

    delta   = 2 * float(width) / len(letters)
    for x in range(len(letters)):
        spawn_sign( style [x]
                  , letters[x]
                  , [position[0] - width + x * delta + delta / 2, position[1]])


def translate(expression):
    parts = expression.split(' ')
    for x in range(len(parts)):
        try:
            if parts[x] != '2' and parts[x] != '3':
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
    if type(input) != type(""):
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
                   abs(test.pos[1] - match.pos[1]) > 2*epsilon:
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
                    position = h.pos

                if v_c == 0 and h_c == 2:
                    result = " = "

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
               symmetric(list[0], list[1]):
                result = (closed and ["D"] or ["C"])[0]
                position = [ (list[1].pos[0] + list[0].pos[0]) / 2
                           , (list[1].pos[1] + list[0].pos[1]) / 2]

        if length == 4:
            list = remove(lambda x: x.ori == 0, list)
            if len(list) == 2 and \
               list[0].ori == - list[1].ori and \
               list[0].ori % 90 != 0:
                result = "M"
                position = [ (list[1].pos[0] + list[0].pos[0]) / 2
                           , (list[1].pos[1] + list[0].pos[1]) / 2]

    return (result, position)

io.clearEvents('all')

demo_timeout_start = core.getTime()

k = ['i']

romanMessage = spawn_message('', (0.0,-(size[1]/4)))
solveMessage = spawn_message('', (0.0,-(size[1]/3)))

spawn_expression( default
                    , translate('1666 + 1 - 2 = 3')
                    , [0, 0]
                    , size[0] * 0.5)


def read_matches(array):
    decision = []
    for s in decompose(array):
        try:
            decision.append(recognize(list(s)))
        except Exception as e:
            print(e.message)
    recognized = ''.join(map(lambda x: x[0], sorted(decision, key=lambda x: x[1][0])))
    normalized = []
    for part in recognized.split(' '):
        try:
            normalized.append(str(roman_to_int(part)))
        except ValueError:
            normalized.append(part)
    normalized = ' '.join(normalized)
    normalized += ' (%i = %i)' % tuple(map(eval, normalized.split('=')))
    romanMessage.setText(recognized)

    solveMessage.setText(normalized)


def draw(objects):
    for obj in objects:
        obj.draw()

    win.flip()

while True:
    position, posDelta = mouse.getPositionAndDelta()
    mouse_dX, mouse_dY = posDelta

    left_button, middle_button, right_button = mouse.getCurrentButtonStates()

    read_matches(matches)

    draw(matches + [romanMessage, solveMessage])

    kb_events    = keyboard.getEvents()
    mouse_events = mouse.getEvents()
    disp_events  = display.getEvents()

    io.clearEvents()

    for evt in disp_events:
        print(evt)

    for evt in kb_events:
        if evt.type == EventConstants.KEYBOARD_PRESS:
            if evt.key_id == 27: # Escape
                io.quit()
                core.quit()