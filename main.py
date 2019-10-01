import getopt
import os.path
import re
import sys
from urllib.parse import urlencode, urlunparse, urlparse
import uuid

from pathlib import Path


def find_parameters(content):
    parameters = []
    brackets_patterns = ['\[\'(\w*)\'\]', '\["(\w*)"\]']
    prefix = '\$_'
    functions = ['REQUEST', 'GET', 'POST', 'AJAX', 'ajax_req']
    for f in functions:
        for b in brackets_patterns:
            regex_pattern = "{}{}{}".format(prefix, f, b)
            matches = re.findall(regex_pattern, content)
            parameters.extend(matches)
    return list(set(parameters))


def enumerate_php_files(php_root_directory):
    php_files = list(Path(php_root_directory).glob('**/*.php'))
    php_files.extend(Path(php_root_directory).glob('*.php'))
    return list(set(php_files))


def create_dir_if_not_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def main(scheme='http', netloc='localhost', web_prefix='', output_file='', output_directory='output', php_root_directory='/var/www'):
    if not output_file:
        output_filename = "{}.sqlmap.sh".format(uuid.uuid4())
    php_root_directory = '../openemr'
    output_path = os.path.join(output_directory, output_filename)

    php_files = enumerate_php_files(php_root_directory)
    create_dir_if_not_exist(output_directory)

    files_with_query_string_params = {}
    for filename in php_files:
        try:
            filename = str(filename)
            content = Path(filename).read_text()
            parameters = find_parameters(content)
            concat_path = filename[len(php_root_directory) + 1:]
            path = os.path.join(web_prefix, concat_path)
            path = os.path.normpath(path)
            path = path.replace(os.sep, '/')

            if len(parameters) > 0:
                files_with_query_string_params[path] = parameters
        except:
            print("Examine error: {}".format(filename))

    urls = []
    for path, params in files_with_query_string_params.items():
        query_string_params = {}
        for p in params:
            # All are set to 1 so sqlmap can do its magic
            query_string_params[p] = '1'
        param_string = urlencode(query_string_params)
        urls.append(urlunparse((scheme, netloc, path, '', param_string, '')))

    sqlmap_commands = ["sqlmap -u \"{}\" --batch > {}.sqlmap.txt".format(url, str(uuid.uuid4())) for url in urls]

    f = open(output_path, "w+")
    for cmd in sqlmap_commands:
        f.write("{}\n".format(cmd))
    f.close()


def usage():
    print("Usage: {}".format(sys.argv[0]))
    print("")
    print("Generates sqlmap commands to test php applications for sql injection.")
    print("")
    print("""
    This program functions by parsing php files for query string parameters and generating urls
    containing those parameters to pass into sqlmap. This is an automated way to generate better
    guesses with sqlmap. It isn't perfect because it doesn't do any path analysis to determine sane
    values for the parameters, but is better than sqlmap by itself.
    
    -h      --help                  Display this message
    -u      --url                   A base url for the web application being tested
    -o      --output-file           The filename to output the .sh script
    -d      --output-directory      The directory to store the .sh script in
    -p      --php-root-directory    The directory where the php application sits
    """)


if __name__ == "__main__":
    scheme = 'http'
    netloc = 'localhost'
    web_prefix = ''
    output_file = ''
    output_directory = 'output'
    php_root_directory = '/var/www'

    args = sys.argv[1:]
    unix_options = "hu:o:d:p:"
    gnu_options = ['help', 'url', 'output-file', 'output-directory', 'php-root-dir']
    try:
        arguments, values = getopt.getopt(args, unix_options, gnu_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-u", "--url"):
                # parse scheme, netloc, and path
                scheme, netloc, web_prefix, a, b, c = urlparse(currentValue)
            elif currentArgument in ("-h", "--help"):
                usage()
            elif currentArgument in ("-o", "--output-file"):
                output_file = currentValue
            elif currentArgument in ("-d", "--output-directory"):
                output_directory = currentValue
            elif currentArgument in ("-p", "--php-root-dir"):
                php_root_directory = currentValue
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    main(scheme, netloc, web_prefix, output_file, output_directory, php_root_directory)
