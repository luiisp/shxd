import sys
import argparse
from .parser import default_parser
from .utils import colors

def main():

    parser = default_parser
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to be processed by the CLI.')

    args = parser.parse_args()

    
    if not args.args:
        sys.stdout.write(colors.yellow + 'No args!' + colors.reset + '\n')
        return
    sys.stdout.write('Arguments received: ' + ' '.join(args.args) + '\n')

        