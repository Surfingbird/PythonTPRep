# -*- encoding: utf-8 -*-
import re
from collections import Counter
from datetime import datetime




def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):

    def is_file(url_path):
        """Checks if URL path has file in it """
        if url_path and not url_path.endswith(r'/'):
            return True
        else:
            return False

    pattern = re.compile(r"""
        \[(?P<time>.+)\] \s+                        # parse time 
        \"(?P<request_type>\w+) \s+                 # parse request type
        (?P<scheme>\w+)  ://                        # parse scheme
        (?P<URL>                                    # URL BEGINNING
        ((?P<login>\w+):(?P<password>.+)@)?         # parse login and password
        (?P<www>www\.)?                             # parse WWW.
        (?P<host>[a-zA-Z0-9.]+)                     # parse host without WWW.
        (:(?P<port>\d+))?                           # parse port
        \/(?P<URL_path>[a-zA-Z0-9._/-]+)?           # parse URL
        (\?(?P<queries>.+?))?                       # parse queries
        (\#(?P<fragment>\w+))?                      # parse fragment
        )  \s+                                      # URL END
        (?P<protocol>\w+/[0-9/.]+)  \" \s+
        (?P<response_code>\d+) \s+                  # parse response code
        (?P<response_time>\d+)                      # parse response time
        """, re.VERBOSE)

    if start_at:
        start_at = datetime.strptime(start_at, '%d/%b/%Y %H:%M:%S')
    if stop_at:
        stop_at = datetime.strptime(stop_at, '%d/%b/%Y %H:%M:%S')

    if slow_queries:
        response_time = dict()
    else:
        counter = Counter()

    with open('log.log', 'r') as f:
        for line in f:
            m = re.match(pattern, line)
            if m:
                time = datetime.strptime(m.group('time'), '%d/%b/%Y %H:%M:%S')
            if (
                    m and                                                                           # checks if match is found
                    not (is_file(m.group('URL_path')) and ignore_files) and                         # checks if files must be ignored
                    (m.group('URL') not in ignore_urls) and                                         # checks if URL must be ignored
                    ((not request_type) or (m.group('request_type') == request_type.upper())) and   # checks if we must show only
                                                                                                    # certain request type (implication)
                    ((not start_at) or time >= start_at) and                                         # checks if start time is set and
                                                                                                    # smaller than time (implication)
                    ((not stop_at) or time <= stop_at)                                               # checks if stop time is set and
                                                                                                    # bigger than time (implication)
            ):

                if m.group('www') and ignore_www:  # checks if www must be ignored
                    url = (m.group()[m.start('URL'): m.start('www')] +
                           m.group()[m.end('www'):m.end('URL')])
                else:
                    url = m.group('URL')

                if slow_queries:
                    response_time[url] = response_time.get(url, []) + [int(m.group('response_time'))]
                else:
                    counter[url] += 1



    if slow_queries:
        response_time = [int(sum(time)/len(time)) for url, time in response_time.items()]
        return sorted(response_time, reverse = True)[:5]
    else:
        return [i[1] for i in counter.most_common(5)]

print(parse())
print(parse(start_at ="18/Mar/2018 11:19:41", stop_at = "25/Mar/2018 11:17:31"))
print(parse(ignore_files= True))
print(parse(slow_queries= True))
print(parse(request_type='PUT', slow_queries= True))
print(parse(request_type='GET', slow_queries= True))
print(parse(ignore_www=True))