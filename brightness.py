#!/usr/bin/env python3

'''
brightness.py
Usage:
    brightness.py [show]
    brightness.py set [--] <value>
'''

import re
import sys
import docopt

backlight_prefix_path = '/sys/class/backlight/intel_backlight'


def read_brightness():
    '''
    Return the current brightness value as reported by the driver.
    '''
    # We can use either the `brightness' file or `actual_brightness'.
    # The differences are documented in the linux kernel tree at
    # Documentation/sysfs-class-backlight.txt
    # Briefly speaking, reading the `brigthness' file returns the
    # brightness as reported by the driver whereas reading
    # `actual_brigthess` returns the value queried directly from the
    # hardware.
    with open(backlight_prefix_path + '/brightness') as fd:
        return int(fd.read())


def read_max_brightness():
    '''
    Return the maximum brightness value that is supported.
    '''
    with open(backlight_prefix_path + '/max_brightness') as fd:
        return int(fd.read())


def print_current_brightness():
    '''
    Output the current brightness first as a value over the maximum
    value, then as a percentage.
    '''

    max_brightness = read_max_brightness()
    cur_brightness = read_brightness()

    percentage_brightness = cur_brightness * 100 / max_brightness

    output = 'Current brightness: {cur}/{max} ({percentage:.2f}%)'.format(
        cur=cur_brightness, max=max_brightness,
        percentage=percentage_brightness)

    print(output)


def set_current_brightness(value):
    '''
    Set the current brightness value according to the parameter.
    The parameter can take multiple forms:
    1) a number (e.g. 650);
    2) a number followed by the '%' sign (e.g. 70%);
    3) a number preceded by a '+' or '-' sign (e.g. +30);
    4) a number number preceded by a '+' or '-' sign and followed by a '%' sign
      (e.g. +10%).
    '''

    matches = re.fullmatch('([+-])?(\d+)(%)?', value)

    if matches is None:
        raise ValueError()

    groups = matches.groups()
    # The first group is either '+', '-' or None.
    # The second group is a number.
    # The third group is either '%' or None.
    max_brightness = None
    cur_brightness = None
    new_brightness = None

    # If we are going to increment / decrement the the value, we need to know
    # what the current value is.
    if groups[0] is not None:
        cur_brightness = read_brightness()
    # If we want to play around with percentage values, we need to know what
    # the maximum value is.
    if groups[2] is not None:
        max_brightness = read_max_brightness()

    # option 1)
    if groups[0] is None and groups[2] is None:
        new_brightness = int(groups[1])
    # option 2)
    elif groups[0] is None and groups[2] is not None:
        new_brightness = round(int(groups[1]) * max_brightness / 100)
    # option 3)
    elif groups[0] is not None and groups[2] is None:
        if groups[0] == '+':
            new_brightness = cur_brightness + int(groups[1])
        else:
            new_brightness = cur_brightness - int(groups[1])
    # option 4)
    else:
        delta = round(int(groups[1]) * max_brightness / 100)
        if groups[0] == '+':
            new_brightness = cur_brightness + delta
        else:
            new_brightness = cur_brightness - delta

    with open(backlight_prefix_path + '/brightness', mode='w') as fd:
        print(new_brightness, file=fd)


def main(argv=None):
    args = docopt.docopt(__doc__, version='1', argv=argv)

    try:
        if args['set']:
            set_current_brightness(args['<value>'])
        else:
            print_current_brightness()

    except ValueError as e:
        raise docopt.DocoptExit(str(e))


if __name__ == '__main__':
    main()
