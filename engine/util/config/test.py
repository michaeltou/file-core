
import os

if __name__ == '__main__':
    current_directory = '/home/phfund/software/file-gateway'
    print('current_directory:', current_directory)
    if 'file-core' not in current_directory:
        current_directory = '/home/phfund/software/file-core'
        print('非file-core目录：'+current_directory)
    else:
        print('是file-core目录')