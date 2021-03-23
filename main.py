#!/usr/bin/env python3
"""Main program"""
import logging
import argparse

import hid

import device
import keys


logger = logging.getLogger('main')


def print_keymap(dev, rows, cols):
    for layer in range(device.get_layer_count(dev)):
        print("Layer %d" % layer)
        for row in range(rows):
            for col in range(cols):
                keycode = device.req_keycode(dev, layer, row, col)
                key_name = keys.get_keyname(keycode)
                print("%10s" % key_name, end=' ')
                assert keys.get_keycode(key_name) == keycode
            print()


def set_key_from_description(dev, key_description):
    (layer, row, col, key_name) = key_description.split(':', 3)
    layer = int(layer)
    row = int(row)
    col = int(col)
    keycode = keys.get_keycode(key_name)
    orig = device.req_keycode(dev, layer, row, col)
    if orig == keycode:
        return False
    logger.info("Setting key on L%d (%d, %d): new %d 0x%x %s old %d 0x%x %s",
                layer, row, col,
                keycode, keycode, key_name,
                orig, orig, keys.get_keyname(orig))
    device.set_keycode(dev, layer, row, col, keycode)
    return True


def set_keys_from_args(dev, key_descriptions):
    changed = False
    for key_description in key_descriptions:
        changed |= set_key_from_description(dev, key_description)
    return changed


def list_devices():
    print("Here are the devices. Please choose one and set --path <path>.")
    for dev in hid.enumerate():
        print("%s %s (%04x:%04x) interface %d: path %s" % (
            dev['manufacturer_string'],
            dev['product_string'],
            dev['vendor_id'], dev['product_id'],
            dev['interface_number'],
            dev['path'].decode('utf-8')))


def main():
    parser = argparse.ArgumentParser(
        description="A CLI tool to interact with VIA")
    parser.add_argument('key_descriptions', metavar='K', type=str, nargs='*',
                        help='a key description')
    parser.add_argument('--list', action='store_const', const=True)
    parser.add_argument('--debug', action='store_const', const=True)
    parser.add_argument('--rows', type=int, default=3)
    parser.add_argument('--cols', type=int, default=3)
    parser.add_argument('--path')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.list or not args.path:
        list_devices()
        return

    dev = hid.device()
    dev.open_path(args.path.encode('utf-8'))
    dev.set_nonblocking(True)

    device.print_info(dev)
    print_keymap(dev, args.rows, args.cols)
    if set_keys_from_args(dev, args.key_descriptions):
        print_keymap(dev, args.rows, args.cols)


if __name__ == "__main__":
    main()
