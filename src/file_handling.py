
# Open and read the file. Return the lines as a list.
def open_file(file):
    try:
        f = open(file, "r")
    except FileNotFoundError:
        raise FileNotFoundError
    else:
        f.seek(0)
        lines = f.readlines()
        f.close()
        return lines


# Create a new file and write to the file the list of lines.
def make_file(file, lines=None):
    f = open(file, "w")
    if lines:
        f.writelines(lines)
    f.seek(0)
    f.close()
