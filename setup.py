from setuptools import setup, find_packages


with open('requirements/requirements.txt') as f:
    requirements = f.read().splitlines()


with open('requirements/requirements-test.txt') as f:
    test_requirements = f.read().splitlines()


setup(
    name='monstermash',
    author='Mitchell Lisle',
    author_email='m.lisle90@gmail.com',
    description="A Python Encryption Helper Library",
    install_requires=requirements,
    packages=find_packages(),
    setup_requires=[],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
            'console_scripts': [
                'monstermash=monstermash.__main__:main',
            ],
        },
    url='https://github.com/mitchelllisle/monstermash',
    version='0.1.0',
    zip_safe=False,
)
