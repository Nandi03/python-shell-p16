# Generated from Shell.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ShellParser import ShellParser
else:
    from ShellParser import ShellParser

# This class defines a complete generic visitor for a parse tree produced by ShellParser.

class ShellVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ShellParser#line.
    def visitLine(self, ctx:ShellParser.LineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#command.
    def visitCommand(self, ctx:ShellParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#pipe.
    def visitPipe(self, ctx:ShellParser.PipeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#call.
    def visitCall(self, ctx:ShellParser.CallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#atom.
    def visitAtom(self, ctx:ShellParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#argument.
    def visitArgument(self, ctx:ShellParser.ArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#redirection.
    def visitRedirection(self, ctx:ShellParser.RedirectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#unquoted.
    def visitUnquoted(self, ctx:ShellParser.UnquotedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#quoted.
    def visitQuoted(self, ctx:ShellParser.QuotedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#single_quoted.
    def visitSingle_quoted(self, ctx:ShellParser.Single_quotedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#backquoted.
    def visitBackquoted(self, ctx:ShellParser.BackquotedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ShellParser#double_quoted.
    def visitDouble_quoted(self, ctx:ShellParser.Double_quotedContext):
        return self.visitChildren(ctx)



del ShellParser