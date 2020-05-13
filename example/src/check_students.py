# @req 0e96
import operator
from myutil.get_student_number import get_student_number

# main

# @req 0e96 37
student_no = [
    '201532120139',
    '201632120134',
    '201632120140',
    '201632120149',
    '201632120150',
    '201632120152',
    '201632120161',
    '201730210234',
    '201732120133',
    '201732120134',
    '201732120135',
    '201732120136',
    '201732120137',
    '201732120140',
    '201732120141',
    '201732120142',
    '201732120143',
    '201732120146',
    '201732120147',
    '201732120151',
    '201732120152',
    '201732120157',
    '201732120159',
    '201732120161',
    '201732120164',
    '201732120165',
    '201732120166',
    '201732120167',
    '201732120168',
    '201732120170',
    '201732120173',
    '201732120174',
    '201732120175',
]


assignments = ['assignment-submissions.txt', 'assignment-submissions2.txt']

result = []  # @req unkw
for n in student_no:
    count = 0
    for fname in assignments:
        lst = get_student_number(fname)
        if n in lst:
            count += 1

    result.append((n, count))

for t in sorted(result, key=operator.itemgetter(1)):
    n = t[0]
    count = t[1]
    print('%s\t%d' % (n, count))
