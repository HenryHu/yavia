"""Key codes"""


def populate_keys(template):
    for i in range(26):
        template[i + 4] = chr(ord('A') + i)
    for i in range(9):
        template[i + 30] = chr(ord('1') + i)
    template[39] = '0'
    return template


KEYCODE_TO_NAME = populate_keys({
    1:   '______',
    41:  'ESC',

    73:  'INS',
    74:  'HOME',
    75:  'PGUP',
    76:  'DEL',
    77:  'END',
    78:  'PGDN',
    79:  'RIGHT',
    80:  'LEFT',
    81:  'DOWN',
    82:  'UP',

    0xA8: 'MUTE',
    0xAB: 'MNEXT',
    0xAC: 'MPREV',
    0xAE: 'PLAY',

    0xF0: 'MS_UP',
    0xF1: 'MS_DOWN',
    0xF2: 'MS_LEFT',
    0xF3: 'MS_RIGHT',
    0xF4: 'MS_BTN1',
    0xF5: 'MS_BTN2',
    0xF6: 'MS_BTN3',
    0xF7: 'MS_BTN4',
    0xF8: 'MS_BTN5',

    0x5C00: 'RESET',
    0x5CC2: 'RGB_TOG',
    0x5CC3: 'RGB_MOD',
    0x5CD6: 'VLK_TOG',
})


def gen_name_to_keycode():
    ret = {}
    for keycode, name in KEYCODE_TO_NAME.items():
        ret[name] = keycode
    return ret


NAME_TO_KEYCODE = gen_name_to_keycode()


def get_keyname(keycode):
    if keycode & 0xFF00:
        high = (keycode & 0xFF00) >> 8
        low = keycode & 0xFF
        if high == 0x51:
            return "MO(%d)" % low
        if high == 1:
            return 'C(%s)' % get_keyname(low)
    return KEYCODE_TO_NAME.get(keycode, '#%x' % keycode)


def get_keycode_direct(name):
    return int(name)


def get_keycode_call(name, func, mask, inner_func):
    if name.startswith(func + '(') and name.endswith(')'):
        return mask | inner_func(name[len(func) + 1: -1])
    return None


def get_keycode(name):
    keycode = NAME_TO_KEYCODE.get(name, None)
    if keycode is not None:
        return keycode

    if name.startswith('#'):
        return int(name[1:], 16)

    keycode = get_keycode_call(name, "MO", 0x5100, get_keycode_direct)
    if keycode is not None:
        return keycode

    keycode = get_keycode_call(name, "C", 0x100, get_keycode)
    if keycode is not None:
        return keycode

    raise Exception("Unknown key name: %s" % name)
