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
        if url_path and not url_path.endswith(r'/'):
            return True
        else:
            return False

    pattern = re.compile(r"""
        \[(?P<TIME>.+)\] \s+                        
        \"(?P<REQUEST_TYPE>\w+) \s+                 
        (?P<SHEME>\w+)  ://                        
        (?P<URL>                                    
        ((?P<LOGIN>\w+):(?P<PASSWORD>.+)@)?         
        (?P<WWW>www\.)?                             
        (?P<HOST>[a-zA-Z0-9.]+)                     
        (:(?P<PORT>\d+))?                           
        \/(?P<URL_PATH>[a-zA-Z0-9._/-]+)?           
        (\?(?P<QUERIES>.+?))?                       
        (\#(?P<FRAGMENT>\w+))?                      
        ) \s+                                      
        (?P<PROTOCOL>\w+/[0-9/.]+)  \" \s+
        (?P<RESPONSE_CODE>\d+) \s+                  
        (?P<RESPONSE_TIME>\d+)                      
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
                time = datetime.strptime(m.group('TIME'), '%d/%b/%Y %H:%M:%S')
            if (
                    m and
                    not (is_file(m.group('URL_PATH')) and ignore_files) and
                    (m.group('URL') not in ignore_urls) and
                    ((not request_type) or (m.group('REQUEST_TYPE') == request_type.upper())) and
                    ((not start_at) or time >= start_at) and
                    ((not stop_at) or time <= stop_at)
            ):

                if m.group('WWW') and ignore_www:
                    url = (m.group()[m.start('URL'): m.start('WWW')] +
                           m.group()[m.end('WWW'):m.end('URL')])
                else:
                    url = m.group('URL')

                if slow_queries:
                    response_time[url] = response_time.get(url, []) + [int(m.group('RESPONSE_TIME'))]
                else:
                    counter[url] += 1



    if slow_queries:
        response_time = [int(sum(time)/len(time)) for url, time in response_time.items()]
        return sorted(response_time, reverse = True)[:5]
    else:
        return [i[1] for i in counter.most_common(5)]
