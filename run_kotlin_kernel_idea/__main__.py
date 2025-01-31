import sys
from run_kotlin_kernel_idea.run_kernel_idea import run_kernel_idea


def main(args):
    run_kernel_idea(*args[1:])


if __name__ == '__main__':
    main(sys.argv)
