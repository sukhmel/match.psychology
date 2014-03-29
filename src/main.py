from psychopy        import visual, event
from matplotlib.path import Path as mpl_Path

win = visual.Window([600, 600])

imageFiles = [ r'../img/match_1.png'
             , r'../img/match_0.png'
             ]

matches = []


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
    image.autoDraw = True


def spawn_sign(style, sign, position):
    scale = style['scale']
    if sign == 'i':
        spawn_match( style
                  , [ position[0]
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
                      , (x + 1) * 90)

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


def spawn_expression(style, expression, position, width):
    parts   = expression.split(' ')
    for x in range(len(parts)):
        try:
            parts[x] = int_to_roman(int(parts[x]))
        except ValueError:
            pass
    letters = ''.join(parts)
    delta   = 2 * float(width) / len(letters)
    for x in range(len(letters)):
        spawn_value( style
                  , letters[x]
                  , [position[0] - width + x * delta + delta / 2, position[1]])


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

def decompose():
    result = []
    for match in matches:
        left = match.verticesPix
        local = {match}
        for i in range(len(result) - 1, -1, -1):
            if match in result[i]:
                local = local.union(result[i])
                result.remove(result[i])

        for test in matches:
            if test not in local:
                right = test.verticesPix
                if overlaps(left, right):
                    local.add(test)

        result.append(local)

    return result



default = { 'scale' : 0.25
          , 'image' : imageFiles[0] }

k = ['i']

while k[0] not in ['escape', 'esc']:
    for s in decompose():
        print( len(s))

    while len(matches) > 0:
        matches[0].autoDraw = False
        del matches[0]

    spawn_expression( default
                    , '10 + 9 - 5 = 14'
                    , [0, 0]
                    , 1)
    win.flip()

    k = event.waitKeys()