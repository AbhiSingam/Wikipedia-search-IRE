digits = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_+=|?.<>`~[]:;}{,'
yo_momma = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15, 'g': 16, 'h': 17, 'i': 18, 'j': 19, 'k': 20, 'l': 21, 'm': 22, 'n': 23, 'o': 24, 'p': 25, 'q': 26, 'r': 27, 's': 28, 't': 29, 'u': 30, 'v': 31, 'w': 32, 'x': 33, 'y': 34, 'z': 35, 'A': 36, 'B': 37, 'C': 38, 'D': 39, 'E': 40, 'F': 41, 'G': 42, 'H': 43, 'I': 44, 'J': 45, 'K': 46, 'L': 47, 'M': 48, 'N': 49, 'O': 50, 'P': 51, 'Q': 52, 'R': 53, 'S': 54, 'T': 55, 'U': 56, 'V': 57, 'W': 58, 'X': 59, 'Y': 60, 'Z': 61, '!': 62, '@': 63, '#': 64, '$': 65, '%': 66, '^': 67, '&': 68, '*': 69, '(': 70, ')': 71, '-': 72, '_': 73, '+': 74, '=': 75, '|': 76, '?': 77, '.': 78, '<': 79, '>': 80, '`': 81, '~': 82, '[': 83, ']': 84, ':': 85, ';': 86, '}': 87, '{': 88, ',': 89}

base = len(digits)

def convert_to_base(decimal_number):
    remainder_stack = []

    while decimal_number > 0:
        remainder = decimal_number % base
        remainder_stack.append(remainder)
        decimal_number = decimal_number // base

    new_digits = []
    while remainder_stack:
        new_digits.append(digits[remainder_stack.pop()])

    return ''.join(new_digits)

def convert_from_base(num):
    ans = 0
    for i, c in enumerate(num[::-1]):
        ans += yo_momma[c]*(base**i)
    return ans

if __name__ == '__main__':
    print(base)
    val = 32498240
    valstr = convert_to_base(val)
    val2 = convert_from_base("wu5(")
    print(val, valstr, val2)