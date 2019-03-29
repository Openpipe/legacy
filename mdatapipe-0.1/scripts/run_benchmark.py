import sys
from IPython.terminal.embed import InteractiveShellEmbed

ipshell = InteractiveShellEmbed()
ipshell.run_line_magic("load", sys.argv[1])
ipshell()
