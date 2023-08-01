import re
import os
import sys
from colorama import Fore
from os import listdir
from file_handling import open_file
from fnmatch import fnmatch

# Class interface for all applications


class Application:
    def __init__(self):
        self.u = UtilityMethods()

    def exec(self, args, output):
        pass

# Class of utility methods for applications:


class UtilityMethods:

    # If taking input from stdin,
    # return the lines in the text file as a list.
    def check_if_stdin_lines(self, args):
        try:
            os.path.isfile(args[0])
        except TypeError:
            return args[0]
        else:
            return open_file(args[0])

    # If taking input from stdin,
    # return the correct list of args.
    def check_if_stdin_file(self, args):
        try:
            os.path.isfile(args[0])
        except TypeError:
            return args[0], True
        else:
            return args, False

    # Template method for head and tail.
    def head_tail_check_args(self, args):
        num_lines = 10
        if args[0] == '-n':
            num_lines = int(args[1])
            args = args[2:]
        self.check_wrong_flag(args)
        lines = self.check_if_stdin_lines(args)
        return lines, num_lines

    # Raise an error if invalid flags are used.
    def check_wrong_flag(self, args, flags=True):
        if args[0][0] == '-':
            if flags:
                raise ValueError("Wrong flag")
            else:
                raise ValueError("this application does not accept flags.")


# Applications:


# Changes current directory to the specified directory.
class Cd(Application):
    def exec(self, args, output):
        os.chdir(args[0])


# Prints the current directory.
class Pwd(Application):
    def exec(self, args, output):
        output.append(os.getcwd())


# Prints all arguments in output.
class Echo(Application):
    def exec(self, args, output):
        for i in args:
            output.append(i + " ")


# Lists all the files in the specified directory.
class Ls(Application):
    def exec(self, args, output):
        if len(args) == 0:
            ls_dir = os.getcwd()
        else:
            ls_dir = args[0]
        # Prevents hidden folders from being outputted by ls
        for f in listdir(ls_dir):
            if not f.startswith("."):
                output.append(f + "\n")


# Prints the contents of a file to output
class Cat(Application):
    def exec(self, args, output):
        for a in args:
            try:
                lines = open_file(a)
                output.extend(lines)
            # Getting args from stdin instead.
            except TypeError:
                output.extend(args[0])


# Gives first n number of lines from a text file
class Head(Application):
    def exec(self, args, output):
        lines, num_lines = self.u.head_tail_check_args(args)

        # If num_lines > the number of lines in the file,
        # then output all lines.
        for i in range(0, min(len(lines), num_lines)):
            output.append(lines[i])


# Gives first n number of lines from a text file
class Tail(Application):
    def exec(self, args, output):
        lines, num_lines = self.u.head_tail_check_args(args)

        # If num_lines > the number of lines in the file,
        # then output all lines.
        display_length = min(len(lines), num_lines)
        for i in range(0, display_length):
            output.append(lines[len(lines) - display_length + i])


# Finds all instances of a pattern in a file and outputs them
class Grep(Application):
    def exec(self, args, output):
        # Grep doesn't accept any flags
        self.u.check_wrong_flag(args, False)

        pattern = args.pop(0)
        files, stdin = self.u.check_if_stdin_file(args)

        for file in files:
            if not stdin:
                lines = open_file(file)
                for line in lines:
                    line = self.match_pattern(pattern, line)
                    if len(files) > 1 and line:
                        output.append(f"{file}:{line}")
                    elif line:
                        output.append(line)
            else:
                line = self.match_pattern(pattern, file)
                if line:
                    output.append(line)

    def match_pattern(self, pattern, line):
        if re.match(pattern, line):
            # Highlight the pattern in each line in cyan except for
            # when testing to avoid test failures.
            if sys.stdout.isatty():
                return self.highlight(pattern, line)
            else:
                return line

    # Highlights the searched for substring when outputting to terminal
    def highlight(self, pattern, line):
        line = line.replace(pattern, Fore.LIGHTCYAN_EX + pattern + Fore.RESET)
        return line


# Outputs a file after removing duplicate lines
class Uniq(Application):
    def exec(self, args, output):
        case = False
        if args[0] == '-i':
            args.pop(0)
            case = True
        self.u.check_wrong_flag(args)

        lines = self.u.check_if_stdin_lines(args)

        output.append(lines[0])
        # Checks if last 2 searched lines are equal to remove duplicates.
        for i in range(1, len(lines)):
            if not self.compare(lines[i - 1], lines[i], case):
                output.append(lines[i])

    # Checks equality based on whether ignore case flag was used or not.
    def compare(self, a, b, ignore):
        if ignore:
            if a.lower().strip() == b.lower().strip():
                return True
        elif not ignore:
            if a.strip() == b.strip():
                return True
        else:
            return False


# Sort lines of text files in alphabetical or reversed order
class Sort(Application):
    def exec(self, args, output):
        rev = False
        if args[0] == '-r':
            rev = True
            args.pop(0)

        self.u.check_wrong_flag(args)

        lines = self.u.check_if_stdin_lines(args)

        sorted_lines = sorted(lines, reverse=rev)
        for line in sorted_lines:
            output.append(line)


# Removes section from each line in a file
class Cut(Application):
    def exec(self, args, output):
        if args[0] == "-b":
            args.pop(0)
            self.cut_b(args, output)
        else:
            raise ValueError("Wrong flags")

    def cut_b(self, args, out):
        index = list(args[0])
        args.pop(0)
        n, index_list, open_i = self.find_range(index)

        lines = self.u.check_if_stdin_lines(args)

        for line in lines:
            new_line = ""
            for j in index_list:
                if open_i and len(n) > 0:
                    # Ensures characters are not repeated for open intervals.
                    if j >= n[0] + 1:
                        continue
                else:
                    new_line += line[j]
            # If interval is open then, add all characters from n til the end.
            if open_i:
                new_line += line[n[0]: len(line)]
                out.append(new_line)
            else:
                out.append(new_line + "\n")

    # Returns a list of indices of characters that should be
    # included of each line in the text file.
    def find_range(self, arr):
        index_list = []
        prev = -1
        open_i = False
        neg = False
        n = []
        for i in arr:
            peek = True
            if i == "-":
                if prev == -1:
                    # If no number before, then this is a negative number.
                    neg = True
                else:
                    # Otherwise, this is an open interval.
                    n.append(prev)
                    open_i = True
            # If comma, then we start to look at another set of indices.
            elif i == ",":
                prev = -1
                peek = False
            # If neither a comma nor a dash, then it's a number.
            elif i != "-" or i != ",":
                # The interval is closed.
                open_i = False
                # if the index, n, is negative we want all the characters
                # from 0 to n.
                if neg:
                    index_list.extend(range(0, int(i)))
                    neg = False
                # Set new value for the previous index in the list.
                elif peek:
                    if len(index_list) == 0:
                        prev = int(i) - 1
                    else:
                        prev = index_list[-1]
                else:
                    prev = int(i) - 1
                # Add all the numbers in the index interval.
                index_list.extend(range(prev, int(i)))
        # Remove any negative indices.
        index_list = [i for i in index_list if i >= 0]
        # Remove any repeated indices.
        index_list = list(set(index_list))
        return n, index_list, open_i


# Finds all files that match a pattern in a specified path
class Find(Application):
    def exec(self, args, output):
        # Sets default values for path and pattern if not provided
        path = "." if args[0] == "-name" else args[0]
        pattern = args[-1] if "-name" in args else "*"
        # Walks through files recursively and outputs filenames that match
        for root, dirs, files in os.walk(path, topdown=True):
            for name in files:
                if fnmatch(name, pattern):
                    output.append(os.path.join(root, name) + "\n")


# Checks if directory already exists and if not creates it
class Mkdir(Application):
    def exec(self, args, output):
        self.u.check_wrong_flag(args, False)
        args, stdin = self.u.check_if_stdin_file(args)

        for dir in args:
            if not os.path.isdir(dir.strip()):
                os.makedirs(dir.strip())
            else:
                raise OSError(dir + " already exists. Command Unsuccessful")


# Checks if file exists and if it does delete it
class Rm(Application):
    def exec(self, args, output):
        self.u.check_wrong_flag(args, False)
        args, stdin = self.u.check_if_stdin_file(args)

        for file in args:
            if os.path.isfile(file.strip()):
                os.remove(file.strip())
            else:
                raise OSError(file + " is not a valid file path.")


# Counts the no. of lines, words and bytes in a file(s)
class Wc(Application):
    def exec(self, args, output):
        self.u.check_wrong_flag(args, False)
        args, stdin = self.u.check_if_stdin_file(args)

        if not stdin:
            for file in args:
                lines = open_file(file)
                line_count, word_count, byte_count = self.wc_counter(lines)
                output.append(f"{file}:{line_count}:{word_count}:{byte_count}")
        else:
            line_count, word_count, byte_count = self.wc_counter(args)
            output.append(f"{line_count}:{word_count}:{byte_count}")

    def word_count(self, lines):
        count = 0
        for i in lines:
            count += len(i.split())
        return count

    def wc_counter(self, lines):
        line_count = len(lines)
        word_count = self.word_count(lines)
        byte_count = sum(len(i) for i in lines)
        return line_count, word_count, byte_count
