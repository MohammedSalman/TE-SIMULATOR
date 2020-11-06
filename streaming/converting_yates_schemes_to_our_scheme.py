import re
from config import YATES_SCHEME_FILE_PATH

new_scheme = {}
f = open(YATES_SCHEME_FILE_PATH, 'r')
for line in f:
    if '->' in line:
        path_n = 0
        temp = re.findall(r'\d+', line)
        # print(temp)
        res = list(map(int, temp))
        s = res[0]
        d = res[1]
        pair = (s, d)
        # print(res)
        # print(line, line.replace(" ", "").replace(":\n", "").replace("->", ""))  # line.split('->'))
        new_scheme[(s, d)] = {}
        #new_line = f.readline()
        #assert ('->' not in new_line)
    if '@' in line:
        line_list = line.strip().split('@')
        unprocessed_path = line_list[0]
        ratio = float(line_list[1])
        numbers = re.findall(r'\d+', unprocessed_path)

        path = []
        [path.append(x) for x in numbers if x not in path]
        variableName = 'x' + "_Index_" + str(path_n) + '_s' + str(s) + '_d' + str(d)
        new_scheme[pair][variableName] = {}
        new_scheme[pair][variableName]['path'] = path
        new_scheme[pair][variableName]['ratio'] = ratio
        path_n += 1


print(new_scheme)
