from string import ascii_letters
from random import choices


def make_test_file(name, num_lines, num_chars):
    with open(f'testdata/{name}', 'x') as file:
        for i in range(num_lines):
            file.write(''.join(choices(ascii_letters + ' ', k=num_chars))+'\n')

            if i % (num_lines // 10) == 0:
                print(f"{i / num_lines:.0%} done")


if __name__ == '__main__':
    make_test_file('small.txt', num_lines=1_000, num_chars=100)
    make_test_file('medium.txt', num_lines=10_000, num_chars=1_000)
    make_test_file('big.txt', num_lines=100_000, num_chars=1_000)
    make_test_file('huge.txt', num_lines=100_000, num_chars=10_000)