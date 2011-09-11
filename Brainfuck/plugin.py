###
# Copyright (c) 2011, Valentin Lorentz
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import time

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Brainfuck')

class BrainfuckSyntaxError(Exception):
    pass

class BrainfuckTimeout(Exception):
    pass

class BrainfuckProcessor:
    def __init__(self):
        self.memory = [0]
        self.memoryPointer = 0

    def checkSyntax(self, program):
        nesting = 0
        for char in program:
            if char == '[':
                nesting += 1
            elif char == ']':
                nesting -= 1
                if nesting < 0:
                    return False
        return nesting == 0

    def execute(self, program, timeLimit=5, checkSyntax=True):
        if checkSyntax:
            if not self.checkSyntax(program):
                raise BrainfuckSyntaxError()
        programPointer = 0
        output = ''
        programLength = len(program)
        loopStack = []
        timeout = time.time() + timeLimit
        while programPointer < programLength:
            char = program[programPointer]
            if char == '>':
                self.memoryPointer += 1
                if len(self.memory) <= self.memoryPointer:
                    self.memory.append(0)
            elif char == '<':
                self.memoryPointer -= 1
            elif char == '+':
                self.memory[self.memoryPointer] += 1
            elif char == '-':
                self.memory[self.memoryPointer] -= 1
            elif char == '.':
                output += chr(self.memory[self.memoryPointer])
            elif char == ',':
                raise NotImplemented()
            elif char == '[':
                if not self.memory[self.memoryPointer]:
                    nesting = 0
                    while programPointer < programLength:
                        if program[programPointer] == '[':
                            nesting += 1
                        elif program[programPointer] == ']':
                            nesting -= 1
                            if nesting == 0:
                                break
                        programPointer += 1
                else:
                    loopStack.append(programPointer)
            elif char == ']':
                programPointer = loopStack.pop() - 1
            programPointer += 1
            if timeout < time.time():
                raise BrainfuckTimeout()
        return output
                    

@internationalizeDocstring
class Brainfuck(callbacks.Plugin):
    """Add the help for "@plugin help Brainfuck" here
    This should describe *how* to use this plugin."""
    threaded = True

    @internationalizeDocstring
    def brainfuck(self, irc, msg, args, opts, code):
        """[--input <characters>] <command>

        Interprets the given Brainfuck code. You should quote the code if you
        use brackets, because Supybot would interpret it as nested commands.
        The code will be fed the <characters> when it asks for input."""
        opts = dict(opts)
        processor = BrainfuckProcessor()
        try:
            output = processor.execute(code)
        except BrainfuckSyntaxError:
            irc.error(_('There was an error in your brainfuck syntax'))
        except BrainfuckTimeout:
            irc.error(_('Brainfuck processor timed out.'))
        irc.reply(output)
    brainfuck = wrap(brainfuck, [getopts({'input': 'something'}), 'text'])



Class = Brainfuck


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: