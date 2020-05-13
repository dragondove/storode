import sys
import os
import hashlib

from pathlib import Path
from enum import Enum


# function for calculating relative paths of path a to path b
def calculate_relative_path(a, b):
    file_name = b[b.rindex('/') + 1:]
    a, b = a[:a.rindex('/')], b[:b.rindex('/')]
    a, b = a.split('/'), b.split('/')

    intersection = 0

    for index in range(min(len(a), len(b))):
        m, n = a[index], b[index]
        if m != n:
            intersection = index
            break

    def backward():
        return (len(a) - intersection - 1) * '../'

    def forward():
        return '/'.join(b[intersection:])

    out = backward() + forward() + '/' + file_name
    return out


# transfer whitespaces in string to html string
def transfer_str_to_html(s):
    return s.replace(
        ' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;').replace('\n', '<br />')


class ReadState(Enum):
    FRONT_OF_CARD = 0
    BACK_OF_CARD = 1
    CREATE = 2
    UPDATE = 3


class Requirement:
    def __init__(self):
        self.state = ReadState.FRONT_OF_CARD
        self.identifier = ''
        self.front_of_card = ''
        self.front_lines = 0
        self.back_lines = 0
        self.back_of_card = ''
        self.create_info = ''
        self.update_info = ''
        self.code_links = {}

    def generate_identifier(self, exclusion=[]):
        m2 = hashlib.md5()
        m2.update((self.front_of_card + self.back_of_card).encode('utf-8'))
        digest = m2.hexdigest()[-4:]
        loop = 0
        while digest in exclusion:
            last = digest[-1]
            if loop > 16:
                raise Exception('Too many collision')
            loop += 1
            if last > 'f':
                last = '0'
            else:
                digest = digest[:-1] + chr(ord(digest[-1]) + 1)
        self.identifier = digest
        collision.append(digest)

    def text_append(self, line):
        if self.state == ReadState.FRONT_OF_CARD:
            if line.strip() != '':
                self.front_lines += 1
            self.front_of_card += line
        elif self.state == ReadState.BACK_OF_CARD:
            if line.strip() != '':
                self.back_lines += 1
            self.back_of_card += line
        elif self.state == ReadState.CREATE:
            self.create_info += line
        elif self.state == ReadState.UPDATE:
            self.update_info += line

    def generate_line_number(self):
        fronts = self.front_of_card.split('\n')
        backs = self.back_of_card.split('\n')

        def get_line_number(strings):
            line_number = 1
            ret = ''
            for string in strings:
                if string.strip() == '':
                    ret += string + '\n'
                else:
                    ret += str(line_number) + ' ' + string + '\n'
                    line_number += 1
            return ret

        self.front_of_card = get_line_number(fronts)
        self.back_of_card = get_line_number(backs)

    def process_str(self, line):
        if line == '\n':
            return
        if 'back of card' in line.lower():
            self.line_number = 1
            self.state = ReadState.BACK_OF_CARD
        elif 'created by' in line.lower():
            self.state = ReadState.CREATE
            self.text_append(line)
        elif 'updated by' in line.lower():
            self.state = ReadState.UPDATE
            self.text_append(line)
        else:
            self.text_append(line)


class CodeFile:
    def __init__(self):
        self.filename = ''
        self.filepath = ''
        self.lines = []

    def find_next_code_signature(self, from_line):
        length = len(self.lines)
        index = from_line
        while index < length:
            line = self.lines[index].strip()
            if line == '' or line[0] == '#':
                index += 1
                continue
            if line.startswith('def ') or line.startswith('class '):
                return index, line.split()[1][:-1]
            # delete end comments
            if '#' in line:
                line = line[:line.index('#')].strip()
            if '=' in line and '==' not in line:
                return index, line[:line.index('=')].strip()
            if line.startswith('if '):
                return index, line[3:-1]
            return index, line
        return None, None


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 2 and argc != 3:
        print('Usage:')
        print('"python storode.py ./srs.txt" to get a srs file with id')
        print('"python storode.py ./srs_id.txt ./src" to generate web pages for crossing reference')
        exit()

    need_identifier = True if argc == 2 else False

    # Read requirements
    requirements = {}

    problems = []

    code_files = []

    # root dir for out pages
    out_dir = './doc'

    srs_file = sys.argv[1]
    if not need_identifier:
        src_path = sys.argv[2]

    # Read requirements from file
    with open(srs_file) as srs:
        last_line = ''
        requirement = None
        lines = srs.readlines()
        collision = []
        for i in range(len(lines)):
            line = lines[i]
            if 'front of card' in line.lower():
                if need_identifier:
                    if requirement != None:
                        requirement.generate_identifier(collision)
                        requirements[requirement.identifier] = requirement
                    requirement = Requirement()
                else:
                    requirement = Requirement()
                    requirement.identifier = last_line.replace('\n', '')
                    requirements[requirement.identifier] = requirement
            elif requirement != None:
                requirement.process_str(line)
            last_line = line
            if i == len(lines) - 1:
                if need_identifier:
                    if requirement != None:
                        requirement.generate_identifier(collision)
                        requirements[requirement.identifier] = requirement

    # Write srs with id file to disk
    if need_identifier:
        with open(srs_file[:srs_file.rindex('.')] + '_with_id.txt', 'w') as srs:
            for _, requirement in requirements.items():
                requirement.generate_line_number()
                srs.write(requirement.identifier + '\n')
                srs.write('FRONT OF CARD\n')
                srs.write(requirement.front_of_card)
                srs.write('BACK OF CARD\n')
                srs.write(requirement.back_of_card)
                srs.write(requirement.create_info)
                srs.write(requirement.update_info)
                srs.write('\n\n')
        exit(0)

    src_path = Path(src_path)

    requirement_out_file = out_dir + '/' + \
        srs_file[srs_file.rindex('/') + 1:srs_file.rindex('.')] + '.html'

    # Read source code
    python_files = []

    # Add python paths recursively
    def recursion_view_path(path):
        if path.is_dir():
            for single_path in path.iterdir():
                recursion_view_path(single_path)
        else:
            if path.match('*.py'):
                python_files.append(path)

    recursion_view_path(src_path)

    for python_file in python_files:
        code_file = CodeFile()
        code_files.append(code_file)
        code_file.filename = python_file.name
        code_file.filepath = str(python_file.parent).replace('\\', '/')
        with open(python_file) as file:
            for line in file.readlines():
                code_file.lines.append(line)

    # generate pages for code
    for code_file in code_files:
        out_path = out_dir + '/' + code_file.filepath
        code_out_file = out_path + '/' + code_file.filename + '.html'
        relative_requirement_file = calculate_relative_path(
            code_out_file, requirement_out_file)
        relative_code_file = calculate_relative_path(
            requirement_out_file, code_out_file)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        with open(code_out_file, 'w') as out_file:
            out_file.write('<style>:target{background-color:#ffff00;}</style>')
            len_of_code = len(code_file.lines)
            former_superlink = None
            superlink_line = None
            infect_lines = None
            for i in range(len_of_code):
                line = code_file.lines[i]
                insertion_line = transfer_str_to_html(line)
                if '#' in line:
                    code = line[:line.index('#')] + '\n'
                    comment = line[line.index('#'):]
                    # make sure this commet is for linking requirements
                    if '@req ' in comment:
                        requirement_identifier = comment[comment.index(
                            '@req') + 5:].strip()
                        requirement_split = requirement_identifier.split()
                        requirement_identifier = requirement_split[
                            0]
                        if len(requirement_split) > 1:
                            infect_lines = requirement_split[1]
                        else:
                            infect_lines = None

                        card_line = None
                        is_front = True
                        requirement_link = requirement_identifier[:]
                        if ':' in requirement_identifier:
                            requirement_identifier, card_line = requirement_identifier.split(
                                ':')
                            if card_line.lower().startswith('front'):
                                card_line = card_line[5:]
                            elif card_line.lower().startswith('back'):
                                is_front = False
                                card_line = card_line[4:]

                        if i + 1 < len_of_code and requirements.__contains__(requirement_identifier):
                            requirement = requirements[requirement_identifier]
                            if card_line != None:
                                card_line = int(card_line)
                                if is_front:
                                    if requirement.front_lines < card_line:
                                        problems.append('WARNING: ' + '<a href="' + relative_code_file + '#line' + str(i) + '">' + code_out_file + ':' + str(
                                            i) + '</a>' + ' requirement identifier: [' + requirement_link + '] not found')
                                    else:
                                        superlink_line, signature = code_file.find_next_code_signature(
                                            i)
                                        former_superlink = relative_requirement_file + '#' + requirement_link
                                        requirement.code_links[signature] = relative_code_file + \
                                            '#line' + str(superlink_line)
                                        insertion_line = transfer_str_to_html(
                                            code)
                                else:
                                    if requirement.back_lines < card_line:
                                        problems.append('WARNING: ' + '<a href="' + relative_code_file + '#line' + str(i) + '">' + code_out_file + ':' + str(
                                            i) + '</a>' + ' requirement identifier: [' + requirement_link + '] not found')
                                    else:
                                        superlink_line, signature = code_file.find_next_code_signature(
                                            i)
                                        former_superlink = relative_requirement_file + '#' + requirement_link
                                        requirement.code_links[signature] = relative_code_file + \
                                            '#line' + str(superlink_line)
                                        insertion_line = transfer_str_to_html(
                                            code)
                            else:
                                superlink_line, signature = code_file.find_next_code_signature(
                                    i)
                                former_superlink = relative_requirement_file + '#' + requirement_link
                                requirement.code_links[signature] = relative_code_file + \
                                    '#line' + str(superlink_line)
                                insertion_line = transfer_str_to_html(code)
                        else:
                            problems.append('WARNING: ' + '<a href="' + relative_code_file + '#line' + str(i) + '">' + code_out_file + ':' + str(
                                i) + '</a>' + ' requirement identifier: [' + requirement_identifier + '] not found')
                if i == superlink_line:
                    insertion_line = '<a title="' + ('+' + infect_lines if infect_lines != None else '') + '" href="' + \
                        former_superlink + '">' + insertion_line + "</a>"
                line_number = str(i)
                while len(line_number) < 4:
                    line_number = ' ' + line_number
                insertion_line = '<span id="line' + str(i) + '" style="user-select:none;font-family:serif;font-weight: bold;white-space: pre;">' + \
                    line_number + '</span>' + '<span style="padding-left: 12px;">' + \
                    insertion_line + '</span>'
                out_file.write(insertion_line)

    # generate the page for requirements
    with open(requirement_out_file, 'w') as out_file:
        out_file.write(
            '<style>:target{background-color:#ffff00;}th{overflow: hidden;text-overflow:ellipsis;}td{overflow:hidden;text-overflow:ellipsis;}</style><table border="1" width="94%" style="word-break:break-all;margin:0 auto;"><tr><th>Identifier</th><th>Front Card</th><th>Back Card</th><th>Date</th><th>Links</th></tr><tbody>')
        total_req_count = len(requirements)
        finished_count = 0
        for _, requirement in requirements.items():
            link_str = ''
            for key, value in requirement.code_links.items():
                link_str += '<a href="' + value + '">' + key + '</a><br />'

            if link_str != '':
                finished_count += 1

            fronts = ''
            for card_line in requirement.front_of_card.split('\n'):
                if card_line.strip() != '':
                    fronts += '<span id="' + requirement.identifier + ':FRONT' + \
                        card_line.split()[0] + '">' + \
                        transfer_str_to_html(card_line) + '</span><br />'

            backs = ''
            for card_line in requirement.front_of_card.split('\n'):
                if card_line.strip() != '':
                    backs += '<span id="' + requirement.identifier + ':BACK' + \
                        card_line.split()[0] + '">' + \
                        transfer_str_to_html(card_line) + '</span><br />'

            out_file.write('<tr><td id="' + requirement.identifier + '">' + requirement.identifier + '</td><td>'
                           + fronts + '</td><td>'
                           + backs + '</td><td>'
                           + transfer_str_to_html(requirement.create_info) +
                           transfer_str_to_html(requirement.update_info)
                           + '</td><td>' + link_str + '</td></tr>')
        out_file.write('</tbody></table><br />')
        problems.append('Conclusion: Total Requirements Count: ' + str(total_req_count) + ', Finished Requirements: ' +
                        str(finished_count) + ', Completion Rate: ' + str(100 * round(finished_count / total_req_count, 4)) + '%.')
        for problem in problems:
            out_file.write(problem + '<br />')
