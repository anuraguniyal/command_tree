import argparse

class CommandTree(object):
    """
    CommandTree takes a nest dictionary and convers it into a parser
    which allows you to create tree like command structure
    """
    ROOT_NAME = 'root'

    def __init__(self, tree):
        # map of full command name to its callback function
        self.tree = tree
        self._callback_map = {}

    def run(self):
        parser = self.create_parser()
        args = parser.parse_args()
        self.call_command_callback(args)

    def create_parser(self):
        return self._create_parser(self.tree)

    def _create_parser(self, tree, parser=None, depth=0, fullname=None):
        # create root parser
        if parser is None:
            parser = argparse.ArgumentParser(**tree['meta_opts'])

        if fullname is None:
            fullname = self.ROOT_NAME

        # add any arguments at this level
        if 'args' in tree:
            for argname, argopts in tree['args'].items():
                 parser.add_argument(argname, **argopts)

        # register callabck
        if 'callback' in tree:
            self._callback_map[fullname] = tree['callback']

        if 'sub_commands' not in tree:
            return parser

        subparsers = parser.add_subparsers(dest='__tree'+str(depth), help='sub-command help')

        for name, subtree in tree['sub_commands'].items():
            subparser = subparsers.add_parser(name, **subtree['meta_opts'])
            self._create_parser(subtree, subparser, depth+1, fullname + '.' + name)

        return parser

    def get_command_fullname(self, args):
        d = vars(args)
        names = [n for n in d if n.startswith('__tree')]
        names.sort()
        values = [d[n] for n in names if d[n] is not None]
        return '.'.join([self.ROOT_NAME]+values)

    def call_command_callback(self, args):
        fullname = self.get_command_fullname(args)
        if fullname not in self._callback_map:
            print("Nothing to do here.")
            return
        return self._callback_map[fullname](args)

