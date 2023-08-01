from antlr4 import InputStream, CommonTokenStream
from grammar.ShellLexer import ShellLexer
from grammar.ShellParser import ShellParser
from collections import deque


# Create a parse tree. Using visitors to traverse the tree.
def parse(s, output, visitor):

    input_stream = InputStream(s)
    lexer = ShellLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ShellParser(stream)
    tree = parser.command()

    # Visitors return the Command object.
    try:
        command = tree.accept(visitor)
    except IndexError:
        raise ValueError("unsupported application: "
                         "could not parse command line")

    input = deque()

    # Call eval() of corresponding Command object.
    final_output = deque()
    for cmd in command:
        cmd.eval(input, final_output)
        output.extend(final_output)
