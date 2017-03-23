import argparse
import inspect
import re


def parse_docstring(docstring):
    """
    Parse docstring and return tuple of description string and list of params dicts.
    `:param` are supported only.
    For `:param str foo: help` this will generate dict `{'type': 'str', 'name': 'foo', 'description': 'help'}`

    :rtype: tuple[str, list[dict]]
    """
    docstring = docstring or ''
    lines = docstring.split('\n')
    description = []
    while lines:
        line = lines[0].strip()
        lines = lines[1:]
        if not line:
            continue

        if line.startswith(':'):
            lines.insert(0, line)
            break

        description.append(line)

    params = []

    while lines:
        line = lines[0].strip()
        lines = lines[1:]
        if not line:
            continue

        if not line.startswith(':') and params:
            params[-1]['description'] += '\n' + line.strip()
            continue

        match = re.match('^:param\s+(?P<type>.+?)?(?(type)\s+|)(?P<name>.+?):\s*(?P<description>.+)?', line)
        if match:
            params.append(match.groupdict())

    return '\n'.join(description), params


def _get_cls_paths(cls, path=None):
    """
    :param type|object cls:
    :param list|tuple|None path: Root path
    :rtype: dict
    """
    paths = dict()
    path = path or tuple()
    path = tuple(path)

    for member_name, member in inspect.getmembers(cls):
        if member_name.startswith('_'):
            continue
        new_path = path + (_clear_name(member_name),)
        if inspect.isclass(member):
            # paths.update(_get_cls_paths(member, path=new_path))
            continue
        elif inspect.isroutine(member):
            paths[new_path] = member

    return paths


def get_paths(cls, path=None):
    """
    Get paths for object or list of objects.

    :param list[type]|type|object cls:
    :param list|tuple|None path: Root path
    :rtype: dict
    """
    if not isinstance(cls, (list, tuple)):
        cls = [cls]

    paths = dict()
    for c in reversed(cls):
        paths.update(_get_cls_paths(c, path=path))
    return paths


def autospec(parser, func, argument_overrides=None):
    """
    Generate parser arguments from `func` signature.

    :param argparse.ArgumentParser parser: Target parser
    :param func: Function to get signature from
    :param None|dict[str, dict] argument_overrides: passed to add_argument for param
    """
    docstring = inspect.getdoc(func) or ""
    parser.description, params_docs = parse_docstring(docstring)
    argument_overrides = argument_overrides or dict()

    signature = inspect.signature(func)
    for param_name, param in signature.parameters.items():
        if param_name == 'self' or param_name == 'cls':
            # https://bitbucket.org/ned/coveragepy/issues/198/continue-marked-as-not-covered
            continue  # pragma: no cover

        kwargs = dict(
            action='store',
            help=param_name
        )

        for param_doc in params_docs:
            if param_doc['name'] == param_name:
                kwargs['help'] = param_doc['description']

        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            kwargs['nargs'] = '+'
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            kwargs['nargs'] = '*'
            if kwargs['help'] == param_name:
                kwargs['help'] = 'Optional keyword arguments. Specify them as key=value'

        if param.default is not inspect._empty:
            param_name = '--' + param_name
            kwargs['default'] = param.default

        if isinstance(param.default, bool):
            if param.default:
                kwargs['action'] = 'store_false'
            else:
                kwargs['action'] = 'store_true'

        if param_name in argument_overrides:
            kwargs.update(argument_overrides[param_name])

        parser.add_argument(param_name, **kwargs)


def get_func_arguments(func, argparse_args):
    """
    Return args and kwargs for func.

    :param callable func:
    :param argparse.Namespace|dict argparse_args: argparse Namespace or dict
    :return: args and kwargs to be passed into func
    :rtype: tuple[list, dict]
    """
    if isinstance(argparse_args, argparse.Namespace):
        argparse_args = vars(argparse_args)

    args = list()
    kwargs = dict()
    signature = inspect.signature(func)
    got_positional = False
    for param_name, param in signature.parameters.items():
        if got_positional:
            if param_name in argparse_args and param_name != 'kwargs':
                kwargs[param_name] = argparse_args[param_name]
        else:
            got_positional = param.kind == inspect.Parameter.VAR_POSITIONAL and param_name in argparse_args
            if got_positional:
                args.extend(argparse_args[param_name])
            else:
                args.append(argparse_args[param_name])

    if 'kwargs' in argparse_args:
        kwargs.update(argparse_args['kwargs'])

    return args, kwargs


def _clear_name(name):
    name = name.lower()
    while name.startswith('_'):
        name = name[1:]
    while name.endswith('_'):
        name = name[:-1]
    return name


def clear_qualname(qualname):
    return list(map(_clear_name, qualname.split('.')))


def parse_path(path):
    path = path or []
    if not isinstance(path, (list, tuple)):
        path = path.split('.')
        if len(path) == 1 and path[0]:
            path = path[0].split(' ')
        elif len(path) == 1 and not path[0]:
            path = []
    return path


class EndpointParser(argparse.ArgumentParser):
    subparsers = None
    internal_keys = {'__func__', '__endpoint__'}

    def clear_internal_keys(self, args):
        """
        Deletes all keys specified in `internal_keys` field from args (Namespace or dict)

        :param dict|argparse.Namespace args:
        :rtype: dict
        """
        if isinstance(args, argparse.Namespace):
            args = vars(args)
        for key in self.internal_keys:
            args.pop(key, None)
        kwargs_list = args.pop('kwargs', [])
        kwargs = dict()
        for item in kwargs_list:
            key, value = item.split('=')
            kwargs[key] = value
        if kwargs:
            args['kwargs'] = kwargs
        return args

    def add_subparsers(self, **kwargs):
        """
        Create subparsers action for current parser and store it at `subparsers` field

        :rtype: argparse._SubParsersAction
        """
        self.subparsers = super(EndpointParser, self).add_subparsers(**kwargs)
        return self.subparsers

    # noinspection PyProtectedMember
    def get_endpoint_parser(self, path):
        """
        Return a parser for `path`.

        :param str|list|tuple path:
        :rtype: argparse.ArgumentParser
        """
        path = parse_path(path)

        if not path:
            return self

        parser = self

        for key in path:
            if parser.subparsers is None:
                parser.add_subparsers()
            if key in parser.subparsers._name_parser_map:
                parser = parser.subparsers._name_parser_map[key]
            else:
                parser = parser.subparsers.add_parser(key)

        parser.path = path

        return parser

    def add_endpoint(self, path, func=None, autospec=True, argument_overrides=None):
        if func is None and callable(path):
            func = path
            qualname = clear_qualname(func.__qualname__)
            path = qualname[1 if len(qualname) > 1 else 0:]

        parser = self.get_endpoint_parser(path)

        if func:
            if autospec:
                globals()['autospec'](parser, func, argument_overrides=argument_overrides)
            parser.set_defaults(__func__=func)

        parser.set_defaults(__endpoint__=path)

        return parser

    def generate_endpoints(self, obj, root_path=None, endpoint_kwargs=None):
        """
        Generate endpoints from object or list of objects.

        :param list[object]|object obj:
        :param list|tuple|str root_path:
        :param dict endpoint_kwargs: passed to `add_endpoint` for specified path
        """
        endpoint_kwargs = endpoint_kwargs or {}
        root_path = parse_path(root_path)
        paths = get_paths(obj, path=root_path)
        for path, func in paths.items():
            kw = endpoint_kwargs.get(path, {}) or endpoint_kwargs.get('.'.join(path), {})
            self.add_endpoint(path, func=func, **kw)

    def parse_and_call(self, *args, **kwargs):
        """
        Shortcut function to parse args and call.
        """
        args = self.parse_args(*args, **kwargs)
        return self.call(args)

    def call(self, args):
        if not hasattr(args, '__func__'):
            self.error('Invalid endpoint')

        func = args.__func__
        args = self.clear_internal_keys(args)
        args, kwargs = get_func_arguments(func, args)
        return func(*args, **kwargs)
