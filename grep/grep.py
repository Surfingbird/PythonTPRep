
import argparse
import sys
import re


def output(line):
    print(line)

def count_grep(lines, regex):
    count = 0
    for line in lines:
        line = line.rstrip()
        if(re.search(regex, line)):
            count += 1
    return count


#workspace
def grep(lines, params):
    regex_str = r""

    if(params.invert):
        regex_str = r"(?!" + params.pattern + r")"
    else:
        regex_str = params.pattern

    if(params.ignore_case):
        regex = re.compile(regex_str, re.IGNORECASE)
    else:
        regex = re.compile(regex_str)

    if(params.count):
        output(str(count_grep(lines, regex)))
        return 


    for line in lines:
        #устранение пробельных символов
        line = line.rstrip()
        # print(regex.match(line))
        if(regex.search(line)):
            output(line)


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
