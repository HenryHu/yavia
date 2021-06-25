"""Key codes"""


def populate_keys(template):
    for i in range(26):
        template[i + 4] = chr(ord('A') + i)
    for i in range(9):
        template[i + 30] = chr(ord('1') + i)
    template[39] = '0'
    return template


KEYCODE_TO_NAME = populate_keys({
    0:   '//////',
    1:   '______',
    41:  'ESC',

    0x28: 'ENTER',
    0x29: 'ESC',
    0x2A: 'BSPACE',
    0x2B: 'TAB',
    0x2C: 'SPACE',
    0x2D: '-',
    0x2E: '=',
    0x2F: '[',
    0x30: ']',
    0x31: '\\',
    0x32: 'NONUS_HASH',
    0x33: ';',
    0x34: '\'',
    0x35: '`',

    0x36: ',',
    0x37: '.',
    0x38: '/',
    0x39: 'CLCK',
    0x3A: 'F1',
    0x3B: 'F2',
    0x3C: 'F3',
    0x3D: 'F4',
    0x3E: 'F5',
    0x3F: 'F6',
    0x40: 'F7',
    0x41: 'F8',
    0x42: 'F9',
    0x43: 'F10',
    0x44: 'F11',
    0x45: 'F12',
    0x46: 'PSCR',
    0x47: 'SLCK',
    0x48: 'PAUSE',

    0x49: 'INS',
    0x4A: 'HOME',
    0x4B: 'PGUP',
    0x4C: 'DEL',
    0x4D: 'END',
    0x4E: 'PGDN',
    0x4F: 'RIGHT',
    0x50: 'LEFT',
    0x51: 'DOWN',
    0x52: 'UP',

    0x53: 'NLCK',
    0x54: 'KP_SLASH',
    0x55: 'KP_AST',
    0x56: 'KP_MINUS',
    0x57: 'KP_PLUS',
    0x58: 'KP_ENTER',
    0x59: 'KP_1',
    0x5A: 'KP_2',
    0x5B: 'KP_3',
    0x5C: 'KP_4',
    0x5D: 'KP_5',
    0x5E: 'KP_6',
    0x5F: 'KP_7',
    0x60: 'KP_8',
    0x61: 'KP_9',
    0x62: 'KP_0',
    0x63: 'KP_DOT',
    0x64: 'NUSBS',
    0x65: 'APP',
    0x66: 'POWER',
    0x67: 'KP_EQ',
    0x68: 'F13',
    0x69: 'F14',
    0x6A: 'F15',
    0x6B: 'F16',
    0x6C: 'F17',
    0x6D: 'F18',
    0x6E: 'F19',
    0x6F: 'F20',
    0x70: 'F21',
    0x71: 'F22',
    0x72: 'F23',
    0x73: 'F24',

    0x89: 'YEN',

    0xA6: 'SLEEP',

    0xA8: 'MUTE',
    0xAB: 'MNEXT',
    0xAC: 'MPREV',
    0xAD: 'MSTOP',
    0xAE: 'PLAY',

    0xB0: 'EJCT',
    0xB1: 'MAIL',
    0xB2: 'CALC',
    0xB4: 'SRCH',
    0xB6: 'BACK',
    0xB7: 'FWD',
    0xB9: 'REFRESH',

    0xBB: 'MFWD',
    0xBC: 'MRWD',
    0xBD: 'BRUP',
    0xBE: 'BRDN',

    0xE0: 'LCTRL',
    0xE1: 'LSHIFT',
    0xE2: 'LALT',
    0xE3: 'LWIN',
    0xE4: 'RCTRL',
    0xE5: 'RSHIFT',
    0xE6: 'RALT',
    0xE7: 'RWIN',

    0xF0: 'MS_UP',
    0xF1: 'MS_DOWN',
    0xF2: 'MS_LEFT',
    0xF3: 'MS_RIGHT',
    0xF4: 'MS_BTN1',
    0xF5: 'MS_BTN2',
    0xF6: 'MS_BTN3',
    0xF7: 'MS_BTN4',
    0xF8: 'MS_BTN5',

    0xF9: 'MS_WHUP',
    0xFA: 'MS_WHDN',
    0xFB: 'MS_WHLT',
    0xFC: 'MS_WHRT',

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
