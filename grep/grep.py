import argparse
import sys
import re

from BoostedQueue import  BoostedQueue

def output(line):
    print(line)

def count_grep(lines, regex):
    count = 0
    for line in lines:
        line = line.rstrip()
        if(re.search(regex, line)):
            count += 1
    return count


def grep(lines, params):
    regex_str = r""
    for i in params.pattern:
        pass
        if i == '?':
            regex_str += '.'
        elif i == '*':
            regex_str += '.' + i
        else:
            regex_str += i

    if(params.invert):
        regex_str = r"(?!" + regex_str + r")"

    if(params.ignore_case):
        regex = re.compile(regex_str, re.IGNORECASE)
    else:
        regex = re.compile(regex_str)
    if(params.count):
        output(str(count_grep(lines, regex)))
        return

    before_str = 0
    after_str = 0

    if params.before_context:
        before_str = params.before_context
    elif params.context:
        before_str = params.context
    if params.after_context:
        after_str = params.after_context
    elif params.context:
        after_str = params.context

    context_info = []
    matched_index = []
    queue = BoostedQueue(before_str, after_str)

    counter = 1

    for i in lines:
        line = i.rstrip
        queue.enqueue(line)
        if not queue.current == None:
            if params.invert:
                if regex.match(line):
                    new_context_info = queue.get_all_elem()
                    context_info.extend(new_context_info)

            elif regex.search(line):
                new_context_info = queue.get_all_elem()
                context_info.extend(new_context_info)

    context_info = sorted(set(context_info), key = lambda x : x[0])
    for line in context_info:
        if(params.line_number):
            if line[0] in matched_index:
                output(str(line[0] + 1) + ":" + str(line[1]))
            else:
                output(str(line[0] + 1) + "-" + str(line[1]))
        else:
            output(line[1])
            
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
