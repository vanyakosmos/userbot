import argparse


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


class HelpAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, nargs=0)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, parser.format_help())


class MergeAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, type=str)

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, (tuple, list)):
            values = ' '.join(values)
        setattr(namespace, self.dest, values)
