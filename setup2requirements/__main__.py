# -*- coding: utf-8 -*-
"""
Generates a requirements.txt from any packages
in the current working directory.
"""

from __future__ import print_function

import os
import contextlib
import functools
import argparse
import setuptools
import pkg_resources
from collections import defaultdict


class UnspecifiedRequirementError(AssertionError):
    pass


def _assert_requirement_pinned(name, requirement):
    if not requirement.specifier:
        raise UnspecifiedRequirementError(
            'Missing version specifier for requirement {!r} in {!r}'.format(
                requirement.name, name
            )
        )
    return True


def _filter_requirements(
        predicate,
        output,
        name=None,
        install_requires=None,
        extras_require=None,
        dependency_links=None,
        *_args, **_kwargs
):
    if install_requires:
        output[name].update(
            str(requirement) for requirement in
            pkg_resources.parse_requirements(install_requires)
            if predicate(name, requirement, extra=None)
        )

    if dependency_links:
        output[name].update(dependency_links)

    if extras_require:
        for extra, requirements in extras_require.items():
            output[name].update(
                str(requirement) for requirement in
                pkg_resources.parse_requirements(requirements)
                if predicate(name, requirement, extra=extra)
            )


@contextlib.contextmanager
def patch(target, attr, fn):
    """
    Replace a function for the duration of the context manager
    """
    original = getattr(target, attr)
    try:
        setattr(target, attr, fn)
        yield
    finally:
        setattr(target, attr, original)


def find_requirements(predicate, *paths):
    """
    Return the list of requirements for a setup.py
    """
    requirements = defaultdict(set)

    setup = functools.partial(
        _filter_requirements, predicate, requirements
    )

    for path in paths:
        with patch(setuptools, 'setup', setup):
            with open(path, 'r') as handle:
                exec(
                    handle.read(),
                    {'__file__': os.path.realpath(path)},
                    None
                )

    return dict(requirements)


def main():
    """
    Print a requirements.txt based on the
    install_requires and dependency_links of our setup.py files
    """

    parser = argparse.ArgumentParser(
        description='Generate a requirements.txt from setup.pys'
    )
    parser.add_argument(
        '--extras',
        help='Generate a requirements.txt that includes extras',
        action='append',
    )
    parser.add_argument(
        '--only-extras',
        help='Generate a requirements.txt that only includes extras',
        action='store_true'
    )
    parser.add_argument(
        '--not-strict',
        action='store_true',
        help='Do not force every dependency to have a pinned version number.'
    )
    parser.add_argument(
        'setups',
        metavar='path/to/setup.py',
        nargs='+',
        help='Target setup.py files to scan for requirements'
    )
    args = parser.parse_args()

    def predicate(path, requirement, extra):
        return (
            (args.not_strict or _assert_requirement_pinned(path, requirement)) and (
                (not extra or args.extras) and
                (not args.only_extras or extra in args.extras)
            )
        )

    requirements = find_requirements(
        predicate,
        *args.setups
    )

    dependencies = sorted(
        {
            dependency
            for dependencies in requirements.values()
            for dependency in dependencies
        },
        key=str.lower
    )

    if not dependencies:
        raise AssertionError('No dependencies found.')

    print("""#
# autogenerated by setup2requirements
#
# from:
#
#  {}
#
""".format('\n#  '.join('* {}'.format(name) for name in requirements)))
    for requirement in dependencies:
        print(requirement)


if __name__ == '__main__':
    main()