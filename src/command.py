from application import Echo, Cd, Pwd, Ls, Cat, Head, Tail, Grep, \
    Uniq, Sort, Cut, Find, Rm, Mkdir, Wc
from glob import glob
from unsafe_decorator import UnsafeDecorator
from file_handling import open_file, make_file

app = [
    "echo", "pwd", "cd", "ls", "cat", "head", "tail",
    "grep", "uniq", "cut", "sort", "find", "rm", "mkdir", "wc",
    "_echo", "_pwd", "_cd", "_ls", "_cat", "_head", "_tail",
    "_grep", "_uniq", "_cut", "_sort", "_find", "_rm", "_mkdir", "_wc"
]


# Class interface for each Command. A command is either a Pipe, Seq or Call.
class Command:

    def __init__(self, command):
        self.command = command

    def __eq__(self, other):
        return self.command == other.command

    # All commands would require an eval function
    def eval(self, input, output):
        pass

    # If arguments require globbing replace the arguments
    # with the matching list of files found.
    def globbing(self):
        cmd = self.command[0]
        for i in range(len(cmd)):
            if '*' in cmd[i]:
                globbing = glob(cmd[i])
                if globbing:
                    self.command[0].pop(i)
                    self.command[0].extend(globbing)

    # Iterate through the command and append arguments in
    # the stdin to the input deque.
    def input_redir(self, input):
        num_of_files = 0
        index_of_file = 0
        input_redir = False
        for i in range(len(self.command)):
            if self.command[i][0] == "<":
                if len(self.command[i]) == 2 and num_of_files == 0:
                    input.append(open_file(self.command[i][1]))
                    num_of_files += 1
                    index_of_file = i
                    input_redir = True
                else:
                    raise ValueError("Several files cannot be specified "
                                     "for input redirection.")
        if input_redir is True:
            self.command.pop(index_of_file)

    # Write the output to the specified file.
    def output_redir(self, file, output, append=False):
        lines = list(output)
        lines = [line + "\n" for line in lines]
        if append:
            f = open(file, "a+")
            f.writelines(lines)
            f.close()
        else:
            make_file(file, lines)
        output.clear()

# Classes for each command:


class Pipe(Command):

    def __init__(self, command):
        super().__init__(command)

    def eval(self, input, output):
        prev_cmd = 0
        # Iterate through the list of commands.
        for i in range(1, len(self.command)):

            if self.command[i][0] in app:
                output.clear()

                # Create a Call object for each Call command in the list
                # and execute it.
                c = Call(self.command[prev_cmd: i])
                c.eval([list(input)], output)

                prev_cmd = i

                # Copy the output into the input for the next command.
                input = output.copy()

        # Finally, execute the last command not included in the loop.
        c = Call(self.command[prev_cmd:])
        output.clear()
        c.eval([list(input)], output)


class Seq(Command):

    def __init__(self, command):
        super().__init__(command)

    def eval(self, input, output):
        prev_cmd = 0

        for i in range(1, len(self.command)):

            # Iterate through the list of commands.
            if self.command[i][0] in app:

                # Create a Call object for each Call command in the list
                # and execute it.
                c = Call(self.command[prev_cmd: i])
                c.eval(input, output)
                prev_cmd = i

        c = Call(self.command[prev_cmd:])
        c.eval(input, output)


class Call(Command):

    def __init__(self, command):
        super().__init__(command)
        self.app = None
        self.args = None
        self.out = None

    def eval(self, input, output):
        self.input_redir(input)
        self.globbing()
        safe = True
        self.app = self.command[0][0]
        self.args = self.command[0][1:]
        self.input = list(input)
        self.out = output
        self.application = None

        if len(self.input) != 0:
            if len(self.input[0]) != 0:
                self.args.extend(self.input)

        for i in range(len(self.args)):
            if ("'" in self.args[i] or '"' in self.args[i]) \
                    and self.args[i] != "''":
                self.args[i] = self.args[i][1:-1]

        # Check if this is an unsafe application.
        if self.app[0] == '_':
            safe = False
            self.app = self.app[1:]

        # Factory pattern implemented.
        # Each function returns the Application object.
        func = {
            "head": self.run_head,
            "tail": self.run_tail,
            "uniq": self.run_uniq,
            "pwd": self.run_pwd,
            "cd": self.run_cd,
            "ls": self.run_ls,
            "cat": self.run_cat,
            "grep": self.run_grep,
            "sort": self.run_sort,
            "cut": self.run_cut,
            "echo": self.run_echo,
            "find": self.run_find,
            "rm": self.run_rm,
            "mkdir": self.run_mkdir,
            "wc": self.run_wc
        }

        self.application = func[self.app]()
        if self.application is not None:
            if safe:
                self.application.exec(self.args, self.out)
            else:
                decorator = UnsafeDecorator(self.application)
                decorator.exec(self.args, self.out)
        else:
            raise ValueError(f"unsupported application {self.app}")

        if len(self.command) > 1 and (self.command[1][0] == ">"
                                      or self.command[1][0] == ">>"):
            if len(self.command[1]) > 2:
                raise ValueError("Several files cannot be specified "
                                 "for output redirection.")
            append = True if self.command[1][0] == ">>" else False
            self.output_redir(str(self.command[1][1]), self.out, append)

    # Checks if the correct amount of arguments has been provided to an app
    # Considers if the application is allowed unlimited args.
    def check_arguments(self, num_of_arguments, app, limited_args=True):
        if ((len(self.args) in num_of_arguments and not limited_args)
                or (len(self.args) not in num_of_arguments and limited_args)):
            raise ValueError("wrong number of command line arguments")
        else:
            return app()

    def run_head(self):
        return self.check_arguments([1, 3], Head)

    def run_tail(self):
        return self.check_arguments([1, 3], Tail)

    def run_uniq(self):
        return self.check_arguments([1, 2], Uniq)

    def run_sort(self):
        return self.check_arguments([1, 2], Sort)

    def run_pwd(self):
        return Pwd()

    def run_cd(self):
        return self.check_arguments([1], Cd)

    def run_echo(self):
        return Echo()

    def run_ls(self):
        return self.check_arguments([0, 1], Ls)

    def run_cat(self):
        return Cat()

    def run_grep(self):
        return self.check_arguments([0, 1], Grep, False)

    def run_cut(self):
        return self.check_arguments([3], Cut)

    def run_rm(self):
        return self.check_arguments([0], Rm, False)

    def run_mkdir(self):
        return self.check_arguments([0], Mkdir, False)

    def run_wc(self):
        return self.check_arguments([0], Wc, False)

    def run_find(self):
        for i in self.args:
            if i[0] == '-' and i != '-name':
                raise ValueError("wrong flag used")
        if "-name" in self.args and self.args[-1] == "-name":
            raise ValueError("missing argument to '-name'")
        elif "-name" in self.args and self.args[-2] != "-name":
            raise ValueError("paths must precede expression")
        elif len(self.args) == 0:
            self.args = ["."]
        return Find()
