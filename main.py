"""xxx"""
import time
import logging
import hid


logger = logging.getLogger('main')

CMD_VER = 0x01
CMD_GET_VALUE = 0x02
CMD_GET_KEYCODE = 0x04
CMD_GET_LAYER_COUNT = 0x11


VALUE_UPTIME = 0x01
VALUE_LAYOUT_OPTIONS = 0x02
VALUE_SWITCH_MATRIX = 0x03

logging.basicConfig(level=logging.WARN)


def populate_keys(template):
    for i in range(26):
        template[i + 4] = chr(ord('A') + i)
    for i in range(10):
        template[i + 30] = chr(ord('1') + i)
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
})


def gen_name_to_keycode():
    ret = {}
    for keycode, name in KEYCODE_TO_NAME.items():
        ret[name] = keycode
    return ret


NAME_TO_KEYCODE = gen_name_to_keycode()


dev = hid.device()
dev.open_path(b'0000:0005:01')
print("Keyboard: %s %s" % (dev.get_manufacturer_string(),
                           dev.get_product_string()))
dev.set_nonblocking(True)


def send_req(cmd, args=[]):
    req = [0] * 33
    req[1] = cmd
    idx = 2
    for arg in args:
        req[idx] = arg
        idx += 1

    logger.info('send command: %r', req[1:])
    dev.write(req)
    resp = dev.read(32)
    while not resp:
        time.sleep(0.001)
        resp = dev.read(32)
    logger.info('got response: %r', resp)
    return resp


def get_be32(buf):
    return (buf[0] << 24) + (buf[1] << 16) + (buf[2] << 8) + buf[3]


def get_be16(buf):
    return (buf[0] << 8) + buf[1]


def get_ver():
    response = send_req(CMD_VER, [])
    return get_be16(response[1:3])


def get_uptime():
    response = send_req(CMD_GET_VALUE, [VALUE_UPTIME])
    return get_be32(response[2:6])


def get_layout_options():
    response = send_req(CMD_GET_VALUE, [VALUE_LAYOUT_OPTIONS])
    return get_be32(response[2:6])


def get_switch_matrix():
    response = send_req(CMD_GET_VALUE, [VALUE_SWITCH_MATRIX])
    return get_be32(response[2:6])


def req_keycode(layer, row, col):
    response = send_req(CMD_GET_KEYCODE, [layer, row, col])
    return get_be16(response[4:6])


def get_layer_count():
    response = send_req(CMD_GET_LAYER_COUNT)
    return response[1]


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


def print_keymap():
    for layer in range(get_layer_count()):
        print("Layer %d" % layer)
        for row in range(3):
            for col in range(3):
                key = req_keycode(layer, row, col)
                key_name = get_keyname(key)
                print("%10s" % key_name, end=' ')
                print('%x' % get_keycode(key_name))
            print()


print("VIA ver: %d" % get_ver())
print("Up time: ", get_uptime() / 1000.0, "s")
print("Layout options: ", get_layout_options())
print("Switch matrix: ", get_switch_matrix())
print("Layer count: ", get_layer_count())

print_keymap()
