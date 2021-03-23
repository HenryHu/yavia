"""VIA device"""

import time
import logging

import cmd

logger = logging.getLogger("device")


def send_req(dev, command, cmd_args=None):
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


def get_ver(dev):
    response = send_req(dev, cmd.GET_VER)
    return get_be16(response[1:3])


def get_uptime(dev):
    response = send_req(dev, cmd.GET_VALUE, [cmd.VALUE_UPTIME])
    return get_be32(response[2:6])


def get_layout_options(dev):
    response = send_req(dev, cmd.GET_VALUE, [cmd.VALUE_LAYOUT_OPTIONS])
    return get_be32(response[2:6])


def get_switch_matrix(dev):
    response = send_req(dev, cmd.GET_VALUE, [cmd.VALUE_SWITCH_MATRIX])
    return get_be32(response[2:6])


def req_keycode(dev, layer, row, col):
    response = send_req(dev, cmd.GET_KEYCODE, [layer, row, col])
    return get_be16(response[4:6])


def set_keycode(dev, layer, row, col, keycode):
    response = send_req(dev, cmd.SET_KEYCODE,
                        [layer, row, col] + to_be16(keycode))
    return get_be16(response[4:6])


def get_layer_count(dev):
    response = send_req(dev, cmd.GET_LAYER_COUNT)
    return response[1]


def print_info(dev):
    print("Keyboard: %s %s" % (dev.get_manufacturer_string(),
                               dev.get_product_string()))
    print("VIA ver: %d" % get_ver(dev))
    print("Up time: ", get_uptime(dev) / 1000.0, "s")
    print("Layout options: ", get_layout_options(dev))
    print("Current switch matrix state: ", get_switch_matrix(dev))
    print("Layer count: ", get_layer_count(dev))
