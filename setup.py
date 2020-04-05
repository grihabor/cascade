from setuptools import setup, find_packages

setup(
    name='cascade',
    version='0.0.1',
    author='Borodin Gregory',
    author_email='grihabor@gmail.com',
    install_requires=[
        'pygame==1.9.6',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'cascade = cascade.main:main'
        ]
    }
)