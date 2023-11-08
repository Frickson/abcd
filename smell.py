def read_file(file_path):
    file = open(file_path, 'r')
    contents = file.read()
    # File not closed
    return contents

file_content = read_file('example.txt')
print(file_content)