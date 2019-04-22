from setuptools import setup
from setuptools.command.install import install
import os
import sys
import platform
import errno

version = '0.4.18'

def symlink_force(target, link_name):
    try:
        target = os.path.abspath(target)
        link_name = os.path.abspath(link_name)
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e

class CustomInstall(install):
    def run (self):
        install.run(self)

        print("post install")
        py_major = sys.version_info[0]
        py_minor = sys.version_info[1]

        if py_major is not 3:
            raise "this module is a python 3 module only"

        print("seting up for " + platform.system() + " " + platform.architecture()[0] + " platform")
        if py_minor is 7:
            if platform.system() == 'Windows' and platform.architecture()[0] == '32bit':
                symlink_force("./ICS_IPA/_DataFileIOLibraryInterface-py3.7-v4.12-32.pyd", "./ICS_IPA/_DataFileIOLibraryInterface.pyd")
            elif platform.system() == 'Windows' and platform.architecture()[0] == '64bit':
                symlink_force("./ICS_IPA/_DataFileIOLibraryInterface-py3.7-v4.12-64.pyd", "./ICS_IPA/_DataFileIOLibraryInterface.pyd")
            else:
                raise "Platform or python version is not supported"
        elif py_minor is 6:
            if platform.system() == 'Windows' and platform.architecture()[0] == '32bit':
                symlink_force("./ICS_IPA/_DataFileIOLibraryInterface-py3.6-v4.12-32.pyd", "./ICS_IPA/_DataFileIOLibraryInterface.pyd")
            elif platform.system() == 'Windows' and platform.architecture()[0] == '64bit':
                symlink_force("./ICS_IPA/_DataFileIOLibraryInterface-py3.6-v4.12-64.pyd", "./ICS_IPA/_DataFileIOLibraryInterface.pyd")
            elif platform.system() == 'Linux' and platform.architecture()[0] == '64bit':
                symlink_force("./ICS_IPA/_DataFileIOLibraryInterface-py3.6-v4.12-64.so", "./ICS_IPA/_DataFileIOLibraryInterface.so")
            else:
                raise "Platform or python version is not supported"
        elif py_minor is 4:
            if platform.system() == 'Linux' and platform.architecture()[0] == '64bit':
                symlink_force("./ICS_IPA/_DataFileIOLibraryInterface-py3.4-v4.12-64.so", "./ICS_IPA/_DataFileIOLibraryInterface.so")
            else:
                raise "Platform or python version is not supported"
        else:
            raise "python version is not supported"

setup(
    name='ICS_IPA',
    packages=['ICS_IPA'],
    version=version,
    description='API used for DataMining mdf data files using DataSpy',
    long_description='This repo is designed to manage the library functions used \
                      for DataMining through mdf data files using the DataSpy \
                      product made by Intrepid Control System. The library \
                      contains a bunch of File I/O functions in a dll that \
                      allow users to parse through mdf data files using their \
                      own applications like Python, Excel, Matlab, C# etc. \
                      This library of functions is duplicated on Intrepids \
                      wireless data server (Wireless NeoVI) allowing users to \
                      develop scripts on their PC and then run those scripts \
                      on the Wireless Neo VI data server without requiring \
                      the data to be downloaded.',
    maintainer='Zaid Nackasha',
    maintainer_email='ZNackasha@intrepidcs.com',
    url='https://github.com/intrepidcs/ICS_IPA',
    download_url='https://github.com/intrepidcs/ICS_IPA/archive/' +
                 version + '.tar.gz',
    package=['DataFileIOLibrary'],
    package_data={'DataFileIOLibrary':
                  ['ICS_IPA/_DataFileIOLibraryInterface-py3.6-v4.12-32.pyd',
                   'ICS_IPA/_DataFileIOLibraryInterface-py3.6-v4.12-64.pyd',
                   'ICS_IPA/_DataFileIOLibraryInterface-py3.6-v4.12-64.so',
                   'ICS_IPA/_DataFileIOLibraryInterface-py3.7-v4.12-32.pyd',
                   'ICS_IPA/_DataFileIOLibraryInterface-py3.7-v4.12-64.pyd',
                   'ICS_IPA/_DataFileIOLibraryInterface-py3.4-v4.12-64.so']},
    include_package_data=True,
    classifiers=['Operating System :: Microsoft :: Windows',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3.6'],
    cmdclass={
        'install': CustomInstall,
    }
)
