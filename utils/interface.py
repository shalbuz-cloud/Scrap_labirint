import sys


def loading_bar(count, total, text, size, symbol=1):
    percent = float(count) / float(total) * 100
    symbols = {1: '█', 2: '#', 3: '='}

    sys.stdout.write(
        '\r' + text + str(int(count)).rjust(3, '0') + "/" + str(int(total)).rjust(3, '0') + ' |' +
        symbols[symbol] * int(percent / 10) * size + ' ' * (10 - int(percent / 10)) * size + '|'
    )
