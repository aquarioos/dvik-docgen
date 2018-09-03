from setuptools import setup

setup(
    name='dvik-docgen',
    version='0.2',
    description='Moduł do generowania dokumentacji w formacie RST.',
    url='https://github.com/aquarioos/dvik-docgen',
    author='Daniel Taranta',
    author_email='aquarioos@yandex.com',
    license='MIT',
    packages=['dvik_docgen', 'dvik_file2docs'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'dvik-file2docs = dvik_file2docs.cli:run',
        ],
        # 'console_scripts': ['dvik-forecast = dvik_forecast.command_line:main',
        #                     'dvik-forecast-tools = tools.command_line:main'],
    },
)
