# @req 43b6
def get_student_number(fname):
    f = open(fname, encoding='utf8')
    lines = f.readlines()
    f.close()
    numbers = []
    for line in lines:
        line = line.strip()
        line = line.replace('\t', ' ')
        lst = line.split(' ')
        for x in lst:
            if len(x) == 12 and x[0] == '2':  # @req 43b6:BACK3
                numbers.append(x)
    return list(set(numbers))
