from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chordspy',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'chordspy=chordspy.app:main',
        ],
    },
    author='Upside Down Labs',
    author_email='support@upsidedownlabs.tech',
    description='An open source bag of tools for recording and visualizing Bio-potential signals like EEG, ECG, EMG , or EOG.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/upsidedownlabs/Chords-Python',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_data={
        'chordspy': [
            'config/*.yaml',
            'static/*',
            'templates/*',
            'apps/*.py'
        ],
    },
    python_requires='>=3.9',
)