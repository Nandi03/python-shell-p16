import unittest

from src.parse import parse
from collections import deque
from src.converter import Converter
from src.file_handling import *
from src.application import *
import os


class TestEcho(unittest.TestCase):
    def setUp(self):
        self.out = deque()

    # after each test assert that self.out is empty to insure that every word in the command was tested
    def tearDown(self):
        self.assertEqual(len(self.out), 0)

    def test_simple_echo_command(self):
        parse("echo foo", self.out, Converter())
        self.assertEqual(self.out.popleft(), "foo ")

    def test_echo_multiple_words(self):
        parse("echo hello world", self.out, Converter())
        self.assertEqual(self.out.popleft(), "hello ")
        self.assertEqual(len(self.out), 1)
        self.assertEqual(self.out.popleft(), "world ")

    def test_echo_with_single_quotes(self):
        parse("echo 'hello world'", self.out, Converter())
        self.assertEqual(self.out.popleft(), "hello world ")

    def test_echo_with_double_quotes(self):
        parse('echo "hello world"', self.out, Converter())
        self.assertEqual(self.out.popleft(), "hello world ")

    def test_echo_and_output_redirection_with_nonexisting_file(self):
        parse("echo AAA > file.txt", self.out, Converter())
        

    def test_echo_with_command_substitution(self):
        parse("echo `echo hello world`", self.out, Converter())
        self.assertEqual(self.out.popleft(), "hello world ")

    def test_echo_with_nested_backquotes(self):
        parse('echo "`echo hello` world"', self.out, Converter())
        self.assertEqual(self.out.popleft(), "hello world ")


class TestPwd(unittest.TestCase):
    def setUp(self):
        self.out = deque()

    def test_pwd(self):
        parse("pwd", self.out, Converter())
        self.assertEqual(self.out.popleft(), "/comp0010")

    def test_pwd_with_command_substitution(self):
        parse("`echo pwd`", self.out, Converter())
        self.assertEqual(self.out.popleft(), "/comp0010")


class TestLs(unittest.TestCase):
    # makes a new directory to allow us to compute extra ls tests
    def setUp(self) -> None:
        self.out = deque()
        os.makedirs("newdir", exist_ok=True)
        make_file("newdir/new_file.txt")

    def test_ls(self):
        parse("ls", self.out, Converter())
        self.assertTrue('src\n' in self.out)

    def test_ls_with_args(self):
        parse("ls newdir", self.out, Converter())
        self.assertEqual(['new_file.txt\n'], list(self.out))

    def test_ls_with_wrong_number_args_error(self):
        self.assertRaises(ValueError, parse, "ls newdir dir1", self.out, Converter())

    def test_ls_with_command_substitution(self):
        parse("ls `echo newdir`", self.out, Converter())
        self.assertEqual(['new_file.txt\n'], list(self.out))

    def test_ls_with_command_substitution_and_invalid_file(self):
        self.assertRaises(FileNotFoundError, parse, "ls `echo newdi`", self.out, Converter())


class TestCat(unittest.TestCase):
    def setUp(self) -> None:
        self.lines = ["This\n", "Is\n", "A\n", "Test"]
        make_file("test_cat.txt", self.lines)
        self.out = deque()

    def test_simple_cat_command(self):
        parse("cat test_cat.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines)

    def test_cat_input_redirection(self):
        parse("cat < test_cat.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines)

    def test_cat_several_files_for_input_redirection_raise_error(self):
        self.assertRaises(ValueError, parse, "cat < test_cat.txt < test_cat2.txt", self.out,
                          Converter())  

    def test_cat_with_output_redirection_in_append_mode_and_sequence(self):
        parse("echo ! >> test_cat.txt; cat test_cat.txt", self.out, Converter())
        self.lines = ["This\n", "Is\n", "A\n", "Test! \n"]
        self.assertEqual(list(self.out), self.lines)

class TestHead(unittest.TestCase):

    def setUp(self) -> None:
        self.lines = ["Hello\n", "my\n", "name\n", "is\n", "Tommy\n", "I\n", "am\n", "writing\n", "to\n", "a\n",
                      "file\n"]
        make_file("test_head.txt", self.lines)
        self.out = deque()

    def test_simple_head_command(self):
        parse("head test_head.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[:10])

    def test_head_command_with_n_flag(self):
        parse("head -n 5 test_head.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[:5])

    def test_head_command_with_io_redirection(self):
        parse("head < test_head.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[:10])

    def test_head_command_with_n_flag_and_input_redirection(self):
        parse("head -n 5 < test_head.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[:5])

    def test_head_command_with_large_n(self):
        parse("head -n 50 test_head.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines)

    def test_pipe_chain_with_cat_then_head(self):
        parse("cat test_head.txt | head -n 5", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[:5])

    def test_head_wrong_number_of_args_error(self):
        self.assertRaises(ValueError, parse, "head -n 5 test_head.txt test_tail.txt", self.out, Converter())

    def test_head_wrong_flag_used_error(self):
        self.assertRaises(ValueError, parse, "head -r 5 test_head.txt", self.out, Converter())


class TestTail(unittest.TestCase):

    def setUp(self) -> None:
        self.lines = ["Hello\n", "my\n", "name\n", "is\n", "Tommy\n", "I\n", "am\n", "writing\n", "to\n", "a\n",
                      "file\n"]
        make_file("test_tail.txt", self.lines)
        self.out = deque()

    def test_simple_tail_command(self):
        parse("tail test_tail.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[-10:])

    def test_tail_command_with_n_flag(self):
        parse("tail -n 6 test_tail.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[-6:])

    def test_tail_command_with_input_redirection(self):
        parse("tail < test_tail.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[-10:])

    def test_tail_command_with_n_flag_and_input_redirection(self):
        parse("tail -n 6 < test_tail.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines[-6:])

    def test_tail_command_with_large_n(self):
        parse("tail -n 50 test_tail.txt", self.out, Converter())
        self.assertEqual(list(self.out), self.lines)

    def test_tail_pipe_with_substituting_echo_and_cat(self):
        parse("cat `echo test_tail.txt`| tail -n 2", self.out, Converter())
        self.assertEqual(list(self.out), ["a\n", "file\n"])

    def test_tail_wrong_number_args_error(self):
        self.assertRaises(FileNotFoundError, parse, "tail 5 test_tail.txt test_tail2.txt", self.out, Converter())

    def test_tail_wrong_flag_used_error(self):
        self.assertRaises(ValueError, parse, "tail -r 5 test_head.txt", self.out, Converter())


class TestUniq(unittest.TestCase):
    def setUp(self) -> None:
        lines = ["AAA\n", "bbb\n", "aaa\n", "AAA\n", "AAA\n", "BBB\n", "bbb\n", "bbb\n"]
        make_file("test_uniq.txt", lines)
        self.out = deque()

    def test_simple_uniq_command(self):
        parse("uniq test_uniq.txt", self.out, Converter())
        self.assertEqual(list(self.out), ["AAA\n", "bbb\n", "aaa\n", "AAA\n", "BBB\n", "bbb\n"])

    def test_simple_uniq_i_command(self):
        parse("uniq -i test_uniq.txt", self.out, Converter())
        self.assertEqual(list(self.out), ["AAA\n", "bbb\n", "aaa\n", "BBB\n"])

    def test_uniq_type_file_not_found_exception(self):
        parse("uniq file.txt", self.out, Converter())
        self.assertRaises(FileNotFoundError)

    def test_uniq_pipe_with_sort(self):
        parse("uniq test_uniq.txt | sort", self.out, Converter())
        self.assertEqual(list(self.out), sorted(["AAA\n", "bbb\n", "aaa\n", "AAA\n", "BBB\n", "bbb\n"]))

    def test_uniq_i_pipe_with_cat(self):
        parse("cat test_uniq.txt | uniq -i", self.out, Converter())
        self.assertEqual(list(self.out), ["AAA\n", "bbb\n", "aaa\n", "BBB\n"])

    def test_uniq_wrong_number_args_error(self):
        self.assertRaises(ValueError, parse, "uniq -i test_uniq.txt test_uniq3.txt | uniq", self.out, Converter())

    def test_uniq_wrong_flag_error(self):
        self.assertRaises(ValueError, parse, "cat test_uniq.txt | uniq -r", self.out, Converter())


class TestCut(unittest.TestCase):
    def setUp(self) -> None:
        self.lines = ["AAA\n", "bbb\n", "aaa\n", "AAA\n", "AAA\n", "BBB\n", "bbb\n", "bbb\n"]
        make_file("test_cut.txt", self.lines)
        self.out = deque()

    def test_simple_cut_command(self):
        parse("cut -b 1 test_cut.txt", self.out, Converter())
        self.assertEqual(["A\n", "b\n", "a\n", "A\n", "A\n", "B\n", "b\n", "b\n"], list(self.out))

    def test_cut_command_negative_indices(self):
        parse("cut -b -2 test_cut.txt", self.out, Converter())
        self.assertEqual(["AA\n", "bb\n", "aa\n", "AA\n", "AA\n", "BB\n", "bb\n", "bb\n"], list(self.out))

    def test_cut_with_open_interval(self):
        parse("cut -b 2- test_cut.txt", self.out, Converter())
        self.assertEqual(["AA\n", "bb\n", "aa\n", "AA\n", "AA\n", "BB\n", "bb\n", "bb\n"], list(self.out))

    def test_cut_with_multiple_intervals(self):
        parse("cut -b 1,2-3 test_cut.txt", self.out, Converter())
        self.assertEqual(self.lines, list(self.out))

    def test_cut_wrong_number_args_error(self):
        self.assertRaises(ValueError, parse, "cut test_cut.txt", self.out, Converter())

    def test_cut_wrong_flag_error(self):
        self.assertRaises(ValueError, parse, "cut -r 1,2-3 test_cut.txt", self.out, Converter())


class TestGrep(unittest.TestCase):
    def setUp(self) -> None:
        lines = ["AA\n", "bbb\n", "aa\n", "AAA\n", "AAA\n", "BB\n", "bbb\n"]
        make_file("test_grep1.txt", lines)
        lines = ["AAA\n", "bcc\n", "pom\n", "AA\n", "AAa\n"]
        make_file("test_grep2.txt", lines)
        self.out = deque()

    def test_grep_command_with_simple_pattern(self):
        parse("grep AAA test_grep1.txt", self.out, Converter())
        self.out = remove_colour(self.out)
        self.assertEqual(self.out, ["AAA\n", "AAA\n"])

    def test_grep_with_globbing(self):
        parse("grep bcc *.txt", self.out, Converter())
        self.out = remove_colour(self.out)
        self.assertEqual(self.out, ["test_grep2.txt:bcc\n"])

    def test_grep_with_empty_result(self):
        parse("grep ZZZ test_grep1.txt", self.out, Converter())
        self.out = remove_colour(self.out)
        self.assertEqual(self.out, [])

    def test_grep_starts_with_A_and_length_of_3(self):
        parse("grep 'A..' test_grep1.txt", self.out, Converter())
        self.out = remove_colour(self.out)
        self.assertEqual(self.out, ["AAA\n", "AAA\n"])

    def test_grep_for_AA_multiple_files(self):
        parse("grep 'AA' test_grep1.txt test_grep2.txt", self.out, Converter())
        self.out = remove_colour(self.out)
        self.assertEqual(self.out,
                         ["test_grep1.txt:AA\n", "test_grep1.txt:AAA\n", "test_grep1.txt:AAA\n", "test_grep2.txt:AAA\n",
                          "test_grep2.txt:AA\n", "test_grep2.txt:AAa\n"])

    def test_grep_multiple_files(self):
        files = ["test_grep1.txt", "test_grep2.txt"]
        parse(("grep '...'" + " " + files[0] + " " + files[1]), self.out, Converter())
        final = []
        #goes through files to get the intended output in order to compare to self.out
        for file in files:
            lines = open_file(file)
            for i in range(len(lines)):
                # checking if length of line is >= 3 but use 4 as \n counts as a character
                if len(lines[i]) >= 4:
                    final.append(file + ":" + lines[i])

        self.out = remove_colour(self.out)
        self.assertEqual(self.out, final)

    def test_grep_pipe_chain_with_cat(self):
        parse("cat test_grep1.txt test_grep2.txt | grep 'A..'", self.out, Converter())
        self.out = remove_colour(self.out)
        self.assertEqual(self.out, ['AAA\n', 'AAA\n', 'AAA\n', 'AAa\n'])

    def test_grep_wrong_number_of_args(self):
        self.assertRaises(ValueError, parse, "grep test_grep.txt", self.out, Converter())

    def test_grep_with_flag_error(self):
        self.assertRaises(ValueError, parse, "grep -r test_grep.txt", self.out, Converter())

    def test_echo_sequenced_with_grep_uniq_pipe(self):
        parse("echo hello ; grep 'A.' test_grep2.txt | uniq -i", self.out, Converter())
        self.out = remove_colour(self.out)
        self.assertEqual(self.out, ["hello ", "AAA\n", "AA\n", "AAa\n"])


class TestSort(unittest.TestCase):
    def setUp(self) -> None:
        self.lines = ["This\n", "Is\n", "A\n", "Test\n"]
        make_file("sort_test.txt", self.lines)
        self.out = deque()

    def test_simple_sort_command(self):
        parse("sort sort_test.txt", self.out, Converter())
        self.assertEqual(list(self.out), sorted(self.lines))

    def test_sort_io_redirection(self):
        parse("sort < sort_test.txt", self.out, Converter())
        self.assertEqual(list(self.out), sorted(self.lines))

    def test_sort_reversed(self):
        parse("sort -r sort_test.txt", self.out, Converter())
        self.assertEqual(list(self.out), sorted(self.lines, reverse=True))

    def test_sort_wrong_number_args_error(self):
        self.assertRaises(ValueError, parse, "sort -r test_sort.txt test_sort2.txt", self.out, Converter())

    def test_sort_with_echo_sequence(self):
        parse("sort sort_test.txt; echo \"hello\"", self.out, Converter())
        self.assertEqual(['A\n', 'Is\n', 'Test\n', 'This\n', 'hello '], list(self.out))


class TestFind(unittest.TestCase):
    def setUp(self) -> None:
        make_file("test_find.txt")
        self.out = deque()

    def test_simple_find_command(self):
        parse("find -name test_find.txt", self.out, Converter())
        self.assertEqual(list(self.out), ["./test_find.txt\n"])

    def test_find_command_with_star(self):
        parse("find -name '*find.txt'", self.out, Converter())
        self.assertEqual(sorted(list(self.out)), sorted(["./test_find.txt\n"]))

    def test_find_test_shell(self):
        parse("find test -name test_shell.py", self.out, Converter())
        self.assertEqual(list(self.out), ["test/test_shell.py\n"])

    def test_find_no_file_args_error(self):
        self.assertRaises(ValueError, parse, "find -name", self.out, Converter())

    def test_find_path_not_preceding_flag(self):
        self.assertRaises(ValueError, parse, "find -name dir1 test_find.txt", self.out, Converter())

    def test_find_with_no_args(self):
        cd_out = deque()
        parse("cd system_test", cd_out, Converter())
        parse("find", self.out, Converter())
        self.assertEqual(sorted(list(self.out)), sorted(["./tests.py\n"]))
        #reset directory after test so that other tests pass
        os.chdir("../")
        self.assertTrue(os.getcwd() == "/comp0010")

    def test_find_with_wrong_flag_error(self):
        self.assertRaises(ValueError, parse, "find -n test_shell.py", self.out, Converter())


class TestCd(unittest.TestCase):
    def test_cd(self):
        out = deque()
        parse("cd src", out, Converter())
        out2 = deque()
        parse("ls", out2, Converter())
        self.assertTrue("shell.py\n" in out2)

    # def test_cd_wrong_number_of_args_error(self):
    #     out = deque()
    #     runCommand("cd src dir1", out, Converter())
    #     self.assertRaises(ValueError)

    # resets directory after test to prevent other tests from failing due to being in the wrong directory
    def tearDown(self):
        os.chdir("../")


class TestRm(unittest.TestCase):
    def setUp(self) -> None:
        self.out = deque()
        make_file("test_rm1.txt")
        make_file("test_rm2.txt")
        make_file("test_rm3.txt", ["test_rm2.txt"])

    def test_rm_with_one_file(self):
        parse("rm test_rm1.txt", self.out, Converter())
        self.assertFalse(os.path.isfile("test_rm1.txt"))

    def test_rm_with_multiple_files(self):
        parse("rm test_rm2.txt test_rm1.txt", self.out, Converter())
        self.assertFalse(os.path.isfile("test_rm1.txt") and os.path.isfile("test_rm2.txt"))

    def test_rm_raises_invalid_path_error(self):
        app = Rm()
        self.assertRaises(OSError, app.exec, ["test_rm.txt"], self.out)

    def test_rm_wrong_number_of_args_error(self):
        self.assertRaises(ValueError, parse, "rm", self.out, Converter())

    def test_rm_with_input_redir(self):
        parse("rm < test_rm3.txt", self.out, Converter())
        self.assertFalse(os.path.isfile("test_rm2.txt"))


class TestUnsafeApplications(unittest.TestCase):
    def setUp(self) -> None:
        self.out = deque()

    def test_unsafe_head_with_non_existing_file(self):
        parse("_head -n 5 test_unsafe.txt ; echo hello", self.out, Converter())
        self.assertEqual(list(self.out), ["hello "])


class TestGeneralExceptions(unittest.TestCase):
    def setUp(self) -> None:
        self.out = deque()

    def test_unsupported_application_error(self):
        self.assertRaises(ValueError, parse, "rmdir dir1", self.out, Converter())

    def test_several_files_in_input_redir_error(self):
        self.assertRaises(ValueError, parse, "cat < text_file.txt file.txt", self.out, Converter())

    def test_several_files_in_output_redir_error(self):
        self.assertRaises(ValueError, parse, "echo hello > output.txt file.txt", self.out, Converter())
        
    def test_creating_a_file_with_invalid_name(self):
        self.assertRaises(TypeError, make_file, ["hello"])


class TestMkdir(unittest.TestCase):
    def setUp(self) -> None:
        self.out = deque()
        os.makedirs("dir3", exist_ok=True)
        make_file("file.txt", ["madefolder"])

    def test_mkdir_with_one_arg(self):
        parse("mkdir dir1", self.out, Converter())
        self.assertTrue(os.path.isdir("dir1"))

    def test_mdkir_with_multiple_args(self):
        parse("mkdir dir4 dir5", self.out, Converter())
        self.assertTrue(os.path.isdir("dir4") and os.path.isdir("dir5"))

    def test_mkdir_wrong_number_of_args(self):
        self.assertRaises(ValueError, parse, "mkdir", self.out, Converter())

    def test_mkdir_directory_already_exists_error(self):
        self.assertRaises(OSError, parse, "mkdir dir3", self.out, Converter())

    def test_mkdir_with_input_redirection(self):
        parse("mkdir < file.txt", self.out, Converter())
        self.assertTrue(os.path.isdir("madefolder"))


class TestWc(unittest.TestCase):
    def setUp(self) -> None:
        lines = ["hello\n", "my\n", "name\n", "is\n", "Python\n", "And I love green\n"]
        make_file("test_wc.txt", lines)
        lines = ["And\n", "my\n", "name\n", "is\n", "Java\n"]
        make_file("test_wc2.txt", lines)

        self.out = deque()

    def test_wc_simple_command(self):
        parse("wc test_wc.txt", self.out, Converter())
        self.assertEqual(list(self.out), ["test_wc.txt:6:9:41"])

    def test_wc_with_multiple_files(self):
        parse("wc test_wc2.txt test_wc.txt", self.out, Converter())
        self.assertEqual(list(self.out), ["test_wc2.txt:5:5:20", "test_wc.txt:6:9:41"])

    def test_wc_with_input_redir(self):
        parse("wc < test_wc2.txt", self.out, Converter())
        self.assertEqual(list(self.out), ["5:5:20"])

#auxillary function used to remove the cyan colour from grep's output allowing the tests to pass
def remove_colour(output):
    list = [i.replace(Fore.LIGHTCYAN_EX, '') for i in output]
    list = [i.replace(Fore.RESET, '') for i in list]
    return list


if __name__ == "__main__":
    unittest.main()
