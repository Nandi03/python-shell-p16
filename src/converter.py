from grammar.ShellVisitor import ShellVisitor
from grammar.ShellParser import ShellParser
from command import Pipe, Call, Seq
from parse import parse

app = [
    "echo", "pwd", "cd", "ls", "cat", "head", "tail",
    "grep", "uniq", "cut", "sort", "find", "rm", "mkdir", "wc",
    "_echo", "_pwd", "_cd", "_ls", "_cat", "_head", "_tail",
    "_grep", "_uniq", "_cut", "_sort", "_find", "_rm", "_mkdir", "_wc"
]


# Inherits from ShellVisitor.
# Utilises visitor methods to walk through the parse tree and return a
# command object.


class Converter(ShellVisitor):
    def __init__(self):
        super().__init__()
        self.command_index = -1
        self.tree = []
        self.sequences = 0
        self.command_queue = []

    # Visit a parse tree produced by ShellParser#command.
    def visitCommand(self, ctx: ShellParser.CommandContext):
        # Initialise command to be Seq, Pipe or Call object with the tree
        # generated from visiting the child nodes, and insert it to the
        # command queue and return the queue.
        if ctx.command():
            self.visit(ctx.getChild(0))
            self.visit(ctx.getChild(2))
            command = Seq(self.tree)
            if command not in self.command_queue:
                self.command_queue.insert(0, command)

        elif ctx.pipe():
            start_of_pipe = len(self.tree)
            command = Pipe(self.visitPipe(ctx)[start_of_pipe:])
            self.tree = self.tree[0:start_of_pipe]
            self.command_queue.insert(0, command)

        elif ctx.call():
            command = Call(self.visitChildren(ctx))
            return [command]

        return self.command_queue

    # Visit a parse tree produced by ShellParser#pipe.
    def visitPipe(self, ctx):
        return self.visitCall(ctx)

    # Visit a parse tree produced by ShellParser#call and returns the tree.
    def visitCall(self, ctx: ShellParser.CallContext):
        # Increment the number of sequences in the line
        self.sequences += 1
        self.visitChildren(ctx)
        return self.tree

    # Visit a parse tree produced by ShellParser#atom.
    def visitAtom(self, ctx: ShellParser.AtomContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by ShellParser#argument.
    def visitArgument(self, ctx: ShellParser.ArgumentContext):
        # Checks if the argument is an application.
        if ctx.getText() in app and len(self.tree) != self.sequences:
            # Adds a new list for the current app in the tree and updates the
            # index of the current command.
            self.tree.append([])
            self.command_index += 1
        return self.visitChildren(ctx)

    # Visit a parse tree produced by ShellParser#redirection.
    def visitRedirection(self, ctx: ShellParser.RedirectionContext):
        # Increment the number of sequences and current command index, and
        # add the redirection to the tree.
        self.sequences += 1
        if ctx.getText()[0:2] == ">>":
            self.tree.append([ctx.getText()[0:2]])
        else:
            self.tree.append([ctx.getText()[0]])
        self.command_index += 1
        return self.visitChildren(ctx)

    # Visit a parse tree produced by ShellParser#unquoted.
    def visitUnquoted(self, ctx: ShellParser.UnquotedContext):
        # Add the text from the node to the tree.
        self.tree[self.command_index].append(ctx.getText())
        return

    # Visit a parse tree produced by ShellParser#quoted.
    def visitQuoted(self, ctx: ShellParser.QuotedContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by ShellParser#single_quoted.
    def visitSingle_quoted(self, ctx: ShellParser.Single_quotedContext):
        # Add the text from the node to the tree.
        self.tree[self.command_index].append(ctx.getText())
        return

    # Completes command substitution on backquoted text
    def eval_nested_backquotes(self, text):
        # Find the indexes of the backquotes in the string.
        backquotes_index = [pos for pos, char in enumerate(text)
                            if char == "`"]

        # Isolate the command in backquotes.
        command = text[backquotes_index[0] + 1: backquotes_index[1]]

        # Adds the text on either side of the backquotes and the parsed command
        # to the output.
        out = [text[: backquotes_index[0]]]
        parse(command, out, Converter())
        out[-1] = out[-1][:-1]
        out.append(text[backquotes_index[1] + 1:])

        # Add a list for the command to the tree if necessary.
        if len(self.tree) == 0:
            self.tree.append([])
            self.command_index += 1

        # Adds the output to the tree.
        self.tree[self.command_index].append("".join(out))

    # Visit a parse tree produced by ShellParser#backquoted.
    def visitBackquoted(self, ctx: ShellParser.BackquotedContext):
        self.eval_nested_backquotes(ctx.getText())
        return

    # Visit a parse tree produced by ShellParser#double_quoted.
    def visitDouble_quoted(self, ctx: ShellParser.Double_quotedContext):
        # Check for and evaluate nested backquotes.
        if "`" in ctx.getText():
            self.eval_nested_backquotes(ctx.getText())

        # Add the double quoted text to the tree.
        else:
            self.tree[self.command_index].append(ctx.getText()
                                                 .replace('"', ""))
        return

    def visitTerminal(self, ctx):
        return self.tree
