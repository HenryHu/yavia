"""xxx"""
import time
import logging
import argparse

import cmd
import hid
import keys


logger = logging.getLogger('main')

logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser(description="A CLI tool to interact with VIA")
parser.add_argument('key_descriptions', metavar='K', type=str, nargs='*',
                    help='a key description')
args = parser.parse_args()


dev = hid.device()
dev.open_path(b'0000:0005:01')
print("Keyboard: %s %s" % (dev.get_manufacturer_string(),
                           dev.get_product_string()))
dev.set_nonblocking(True)


def send_req(command, cmd_args=None):
    req = [0] * 33
    req[1] = command
    idx = 2
    if cmd_args:
        for arg in cmd_args:
            req[idx] = arg
            idx += 1

    logger.debug('send command: %r', req[1:])
    dev.write(req)
    resp = dev.read(32)
    while not resp:
        time.sleep(0.001)
        resp = dev.read(32)
    logger.debug('got response: %r', resp)
    return resp


def get_be32(buf):
    return (buf[0] << 24) + (buf[1] << 16) + (buf[2] << 8) + buf[3]


def get_be16(buf):
    return (buf[0] << 8) + buf[1]


def to_be16(value):
    return [(value & 0xFF00) >> 8, value & 0xFF]


def get_ver():
    response = send_req(cmd.GET_VER)
    return get_be16(response[1:3])


def get_uptime():
    response = send_req(cmd.GET_VALUE, [cmd.VALUE_UPTIME])
    return get_be32(response[2:6])


def get_layout_options():
    response = send_req(cmd.GET_VALUE, [cmd.VALUE_LAYOUT_OPTIONS])
    return get_be32(response[2:6])


def get_switch_matrix():
    response = send_req(cmd.GET_VALUE, [cmd.VALUE_SWITCH_MATRIX])
    return get_be32(response[2:6])


def req_keycode(layer, row, col):
    response = send_req(cmd.GET_KEYCODE, [layer, row, col])
    return get_be16(response[4:6])


def set_keycode(layer, row, col, keycode):
    response = send_req(cmd.SET_KEYCODE, [layer, row, col] + to_be16(keycode))
    return get_be16(response[4:6])


def get_layer_count():
    response = send_req(cmd.GET_LAYER_COUNT)
    return response[1]


def get_keyname(keycode):
    if keycode & 0xFF00:
        high = (keycode & 0xFF00) >> 8
        low = keycode & 0xFF
        if high == 0x51:
            return "MO(%d)" % low
        if high == 1:
            return 'C(%s)' % get_keyname(low)
    return keys.KEYCODE_TO_NAME.get(keycode, '#%x' % keycode)


def get_keycode_direct(name):
    return int(name)


def get_keycode_call(name, func, mask, inner_func):
    if name.startswith(func + '(') and name.endswith(')'):
        return mask | inner_func(name[len(func) + 1: -1])
    return None


def get_keycode(name):
    keycode = keys.NAME_TO_KEYCODE.get(name, None)
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
                keycode = req_keycode(layer, row, col)
                key_name = get_keyname(keycode)
                print("%10s" % key_name, end=' ')
                assert get_keycode(key_name) == keycode
            print()


def print_info():
    print("VIA ver: %d" % get_ver())
    print("Up time: ", get_uptime() / 1000.0, "s")
    print("Layout options: ", get_layout_options())
    print("Switch matrix: ", get_switch_matrix())
    print("Layer count: ", get_layer_count())


def set_key_from_description(key_description):
    (layer, row, col, key_name) = key_description.split(':', 3)
    layer = int(layer)
    row = int(row)
    col = int(col)
    keycode = get_keycode(key_name)
    orig = req_keycode(layer, row, col)
    if orig == keycode:
        return False
    logger.info("Setting key on L%d (%d, %d): new %d 0x%x %s old %d 0x%x %s",
                layer, row, col,
                keycode, keycode, key_name,
                orig, orig, get_keyname(orig))
    set_keycode(layer, row, col, keycode)
    return True


def set_keys_from_args(key_descriptions):
    changed = False
    for key_description in key_descriptions:
        changed |= set_key_from_description(key_description)

    if changed:
        print_keymap()


print_info()
print_keymap()
set_keys_from_args(args.key_descriptions)
