# flake8: noqa
from mdatapipe.core.plugins.parse.using.csv import CSVMapper
from mdatapipe.core.plugins.parse.using.grok import GrokMapper


data = '111.222.333.123 HOME - [01/Feb/1998:01:08:46 -0800] "GET /bannerad/ad.htm HTTP/1.0" 200 28083 "http://www.referrer.com/bannerad/ba_intro.htm" "Mozilla/4.01 (Macintosh; I; PPC)"'
csv_parser = CSVMapper(['client_ip', 'ident', 'auth', 'timestamp:2', 'request', 'response', 'bytes', 'referer', 'agent'], delimiter=" ")
grok_parser = GrokMapper('%{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "(?:%{WORD:verb} %{NOTSPACE:request}(?: HTTP/%{NUMBER:httpversion})?|%{DATA:rawrequest})" %{NUMBER:response} (?:%{NUMBER:bytes}|-) %{QS:referrer} %{QS:agent}') # NOQA: E401

%timeit csv_parser.parse(data)
%timeit grok_parser.parse(data)

