from setuptools import find_packages, setup


setup(
    version='0.10.1',
    name='forkit-django',
    author='Virtualstock',
    author_email='dev.admin@virtualstock.com',
    description='Utility functions for forking, resetting and diffing model objects',
    license='BSD',
    keywords='fork deepcopy model abstract diff',
    packages=find_packages(exclude=['forkit.tests']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    url='https://github.com/Virtualstock/forkit-django/',
)
