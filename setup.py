from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os
import sys
import platform
import errno
import shutil

version = '0.4.52'
dllversion = '0.4.27'


def force_symlink(target, link_name):
    try:
        print('creating sim link from ' + link_name + ' ->' + target)
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            try:
                os.remove(link_name)
                os.symlink(target, link_name)
            except OSError as e:
                print('deleted could not create simlink ' + link_name + ' ->' + target)
        else:
            print('could not create simlink ' + link_name + ' ->' + target)
            raise e


def force_move(og_name, target):
    try:
        print('moveing file from ' + og_name + ' ->' + target)
        shutil.move(og_name, target)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(target)
            shutil.move(og_name, target)
        else:
            print('could not move file ' + og_name + ' ->' + target)
            raise e


def force_remove(target):
    try:
        print('removing file ' + target)
        os.remove(target)
    except OSError as e:
        print('could not remove file ' + target)
        raise e


def get_datafileioLib_for_platform():
    global dllversion
    py_major = sys.version_info[0]
    py_minor = sys.version_info[1]

    if py_major is not 3:
        raise "this module is a python 3 module only"

    print("seting up for " + platform.system() + " " + platform.architecture()[0] + " platform")
    if py_minor is 7:
        if platform.system() == 'Windows' and platform.architecture()[0] == '32bit':
            return "_DataFileIOLibraryInterface-py3.7-v" + dllversion + "-32.pyd"
        elif platform.system() == 'Windows' and platform.architecture()[0] == '64bit':
            return "_DataFileIOLibraryInterface-py3.7-v" + dllversion + "-64.pyd"
        elif platform.system() == 'Linux' and platform.architecture()[0] == '64bit':
            return "_DataFileIOLibraryInterface-py3.7-v" + dllversion + "-64.so"
        else:
            raise "Platform or python version is not supported"
    elif py_minor is 6:
        if platform.system() == 'Windows' and platform.architecture()[0] == '32bit':
            return "_DataFileIOLibraryInterface-py3.6-v" + dllversion + "-32.pyd"
        elif platform.system() == 'Windows' and platform.architecture()[0] == '64bit':
            return "_DataFileIOLibraryInterface-py3.6-v" + dllversion + "-64.pyd"
        elif platform.system() == 'Linux' and platform.architecture()[0] == '64bit':
            return "_DataFileIOLibraryInterface-py3.6-v" + dllversion + "-64.so"
        else:
            raise "Platform or python version is not supported"
    elif py_minor is 5:
        if platform.system() == 'Linux' and platform.architecture()[0] == '64bit':
            return "_DataFileIOLibraryInterface-py3.5-v" + dllversion + "-64.so"
        else:
            raise "Platform or python version is not supported"
    elif py_minor is 4:
        if platform.system() == 'Linux' and platform.architecture()[0] == '64bit':
            return "_DataFileIOLibraryInterface-py3.4-v" + dllversion + "-64.so"
        else:
            raise "Platform or python version is not supported"
    else:
        raise "python version is not supported"


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        print('starting post install')
        datafile = get_datafileioLib_for_platform()
        for script in self.get_outputs():
            if os.path.basename(script).startswith("_DataFileIOLibraryInterface-"):
                if (script.endswith(datafile)):
                    if platform.system() == 'Windows':
                        force_move(script, os.path.join(os.path.dirname(script), "_DataFileIOLibraryInterface.pyd"))
                    else:
                        force_move(script, os.path.join(os.path.dirname(script), "_DataFileIOLibraryInterface.so"))
                else:
                    force_remove(script) 


class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        print('starting post develop')
        file = os.path.join(os.getcwd(), "ICS_IPA", get_datafileioLib_for_platform())
        #if platform.system() == 'Windows':
        #    force_symlink(file, os.path.join(os.getcwd(), "ICS_IPA", "_DataFileIOLibraryInterface.pyd"))
        #else:
        #    force_symlink(file, os.path.join(os.getcwd(), "ICS_IPA", "_DataFileIOLibraryInterface.so"))


setup(
    name='ICS_IPA',
    packages=['ICS_IPA'],
    version=version,
    description=platform.architecture()[0] + ' API used for DataMining mdf data files using DataSpy',
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
    package_data={'ICS_IPA':
                  ['_DataFileIOLibraryInterface*.[pyd|so]']},
    include_package_data=True,
    #classifiers=['Operating System :: Microsoft :: Windows',
    #             'Programming Language :: Python',
    #             'Programming Language :: Python :: 3.6'],
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    }
)
