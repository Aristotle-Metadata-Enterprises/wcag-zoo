import click
from lxml import etree
from ast import literal_eval
import sys
import os
from utils import get_wcag_class
from wcag_zoo.utils import make_flat


class ValidationError(Exception):
    def __init__(self, message, *args):
        self.message = message  # without this you may get DeprecationWarning
        super(ValidationError, self).__init__(message, *args)


def test_file(filename):
    parser = etree.HTMLParser()
    path = os.path.dirname(filename)
    tree = etree.parse(filename, parser)
    root = tree.xpath("/html")[0]

    command = root.get('data-wcag-test-command')

    kwargs = dict(
        (arg.lstrip('data-wcag-arg-'), literal_eval(val))
        for arg, val in root.items()
        if arg.startswith('data-wcag-arg-')
    )

    test_cls = get_wcag_class(command)
    staticpath = kwargs.pop('staticpath', None)
    if staticpath:
        kwargs['staticpath'] = os.path.join(path, staticpath)
    instance = test_cls(**kwargs)

    with open(filename, "rb") as file:
        html = file.read()
        results = instance.validate_document(html)
        test_failures = []
        for level in ['failure', 'warning']:
            level_plural = level + "s"
            error_attr = "data-wcag-%s-code" % level

            # Test the nodes that we're told fail, are expected to fail
            _results = make_flat(results[level_plural])
            for result in _results:
                # print(result)
                err_code = tree.xpath(result['xpath'])[0].get(error_attr, "not given")
                if result['error_code'] != err_code:
                    test_failures.append(
                        (
                            "Validation failured for node [{xpath}], expected {level} but no error code was found\n"
                            "    Expected error code was [{error_code}], stated error was [{err_code}]: \n{message}"
                        ).format(
                            xpath=result['xpath'],
                            level=level,
                            error_code=result['error_code'],
                            message=result['message'],
                            err_code=err_code
                        )
                    )

            for node in tree.xpath("//*[@%s]" % error_attr):
                this_path = node.getroottree().getpath(node)
                failed_paths = dict([(result['xpath'], result) for result in _results])

                error_code = node.get(error_attr, "")
                if this_path not in failed_paths.keys():
                    test_failures.append(
                        (
                            "Test HTML states expected {level} for node [{xpath}], but the node did not fail as expected\n"
                            "    This node did not fail at all!"
                        ).format(
                            xpath=this_path,
                            level=level,
                        )
                    )
                elif failed_paths[this_path].get('error_code') != error_code:
                    test_failures.append(
                        (
                            "Test HTML states expected {level} for node [{xpath}], but the node did not fail as expected\n"
                            "    Expected error is was: {error}"
                        ).format(
                            xpath=this_path,
                            level=level,
                            error=failed_paths[this_path]
                        )
                    )
        if test_failures:
            raise ValidationError("\n  ".join(test_failures))


def test_files(filenames):
    failed = 0
    for f in filenames:
        print("Testing %s ... " % f, end="")
        try:
            test_file(f)
            print('\x1b[1;32m' + 'ok' + '\x1b[0m')
        except ValidationError as v:
            failed += 1
            print('\x1b[1;31m' + 'failed' + '\x1b[0m')
            print(" ", v.message)
        except:
            raise
            failed += 1
            print('\x1b[1;31m' + 'error!' + '\x1b[0m')
            if len(filenames) == 1:
                raise
    return failed == 0


def test_command_lines(filenames):
    """
    These tests are much let thorough and just assert the command runs, and has the right number of errors.
    """

    import subprocess
    failed = 0
    for filename in filenames:
        print("Testing %s from command line ... " % filename, end="")

        parser = etree.HTMLParser()
        path = os.path.dirname(filename)
        tree = etree.parse(filename, parser)
        root = tree.xpath("/html")[0]

        command = root.get('data-wcag-test-command')

        kwargs = dict(
            (arg.lstrip('data-wcag-arg-'), literal_eval(val))
            for arg, val in root.items()
            if arg.startswith('data-wcag-arg-')
        )

        staticpath = kwargs.pop('staticpath', None)
        if staticpath:
            kwargs['staticpath'] = os.path.join(path, staticpath)

        args = []
        for arg, val in kwargs.items():
            if val is True:
                # a flag
                args.append("--%s" % arg)
            elif type(val) is list:
                for v in val:
                    args.append("--%s=%s" % (arg, v))
            else:
                args.append("--%s=%s" % (arg, val))

        process = subprocess.Popen(
            ["zookeeper", command, filename] + args,
            stdout=subprocess.PIPE
        )

        results = process.communicate()[0].decode('utf-8')

        try:
            assert(
                "{num_fails} errors, {num_warns} warnings".format(
                    num_fails=len(tree.xpath("//*[@data-wcag-failure-code]")),
                    num_warns=len(tree.xpath("//*[@data-wcag-warning-code]")),
                ) in results
            )
            print('\x1b[1;32m' + 'ok' + '\x1b[0m')
        except ValidationError as v:
            failed += 1
            print('\x1b[1;31m' + 'failed' + '\x1b[0m')
            print(" ", v.message)
        except:
            failed += 1
            print('\x1b[1;31m' + 'error!' + '\x1b[0m')
            if len(filenames) == 1:
                raise
    return failed == 0


@click.command()
@click.argument('filenames', required=True, nargs=-1)
def runner(filenames):
    if len(filenames) == 1 and os.path.isdir(filenames[0]):
        dir_name = filenames[0]
        filenames = [
            os.path.join(os.path.abspath(dir_name), f)
            for f in os.listdir(dir_name)
            if os.path.isfile(os.path.join(dir_name, f))
        ]
    all_good = all([
        test_files(filenames),
        # test_command_lines(filenames)
    ])

    if not all_good:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    runner()
