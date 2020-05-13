import hashlib
import random

# collision tests for my identifier solution


def get_identifier(s):
    m2 = hashlib.md5()
    m2.update(s.encode('utf-8'))
    digest = m2.hexdigest()[-4:]
    return digest


def pick_random_text(lines, num):
    length = len(text_lines)
    s = ''
    for i in range(num):
        s += lines[random.randint(0, num)]

    return s


def get_text_lines_from_file(file_path):
    lines = []
    with open(file_path, encoding='utf8') as f:
        for line in f.readlines():
            if (line.strip() != ''):
                lines.append(line)

    return lines


if __name__ == "__main__":
    text_lines = get_text_lines_from_file('./sample/Wonderland.txt')
    total_sample_count = 100
    sample_size = 8
    test_times = 100
    collision_counts = []
    for i in range(test_times):
        collision_count = 0
        digest_set = set()
        for j in range(total_sample_count):
            digest = get_identifier(pick_random_text(text_lines, sample_size))
            if digest in digest_set:
                collision_count += 1
            else:
                digest_set.add(digest)

        collision_counts.append(collision_count)

    avg_collision_count = sum(collision_counts) / test_times
    print('average collision happened count: ' + str(avg_collision_count))
    print('collision rate: ' +
          str(100 * (avg_collision_count / total_sample_count)) + '%')
