#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A monkey patch to fix auto complete failed when inputs contains unicode words in zsh
See https://github.com/kislyuk/argcomplete/issues/228 for the discussions
"""
import argcomplete
from argcomplete import *


def hacked_call(self, argument_parser, always_complete_options=True, exit_method=os._exit, output_stream=None,
                exclude=None, validator=None, print_suppressed=False, append_space=None,
                default_completer=FilesCompleter()):
    self.__init__(argument_parser, always_complete_options=always_complete_options, exclude=exclude,
                  validator=validator, print_suppressed=print_suppressed, append_space=append_space,
                  default_completer=default_completer)

    if "_ARGCOMPLETE" not in os.environ:
        # not an argument completion invocation
        return

    global debug_stream
    try:
        debug_stream = os.fdopen(9, "w")
    except:
        debug_stream = sys.stderr

    if output_stream is None:
        try:
            output_stream = os.fdopen(8, "wb")
        except:
            debug("Unable to open fd 8 for writing, quitting")
            exit_method(1)

    # print("", stream=debug_stream)
    # for v in "COMP_CWORD COMP_LINE COMP_POINT COMP_TYPE COMP_KEY _ARGCOMPLETE_COMP_WORDBREAKS COMP_WORDS".split():
    #     print(v, os.environ[v], stream=debug_stream)

    ifs = os.environ.get("_ARGCOMPLETE_IFS", "\013")
    if len(ifs) != 1:
        debug("Invalid value for IFS, quitting [{v}]".format(v=ifs))
        exit_method(1)

    comp_line = os.environ["COMP_LINE"]
    comp_point = int(os.environ["COMP_POINT"])

    # Adjust comp_point for wide chars
    if USING_PYTHON2:
        # fixme: the hack is here
        try:
            comp_point = len(comp_line[:comp_point].decode(sys_encoding))
        except UnicodeDecodeError:
            comp_point = len(comp_line[:comp_point])
    else:
        comp_point = len(comp_line.encode(sys_encoding)[:comp_point].decode(sys_encoding))

    comp_line = ensure_str(comp_line)
    cword_prequote, cword_prefix, cword_suffix, comp_words, last_wordbreak_pos = split_line(comp_line, comp_point)

    # _ARGCOMPLETE is set by the shell script to tell us where comp_words
    # should start, based on what we're completing.
    # 1: <script> [args]
    # 2: python <script> [args]
    # 3: python -m <module> [args]
    start = int(os.environ["_ARGCOMPLETE"]) - 1
    comp_words = comp_words[start:]

    debug(
        "\nLINE: '{l}'\nPREQUOTE: '{pq}'\nPREFIX: '{p}'".format(l=comp_line, pq=cword_prequote, p=cword_prefix).encode(
            'utf-8'),
        "\nSUFFIX: '{s}'".format(s=cword_suffix).encode('utf-8'),
        "\nWORDS:", comp_words)

    completions = self._get_completions(comp_words, cword_prefix, cword_prequote, last_wordbreak_pos)

    debug("\nReturning completions:", completions)
    output_stream.write(ifs.join(completions).encode(sys_encoding))
    output_stream.flush()
    debug_stream.flush()
    exit_method(0)


argcomplete.CompletionFinder.__call__ = hacked_call
