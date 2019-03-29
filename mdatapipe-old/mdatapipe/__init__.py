from os.path import dirname, realpath, join

script_dir = dirname(realpath(__file__))
with open(join(script_dir, 'version')) as version_file:
    version = version_file.readline().strip("\r\n")
