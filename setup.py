from setuptools import setup

setup(
    name='Textfile Harvesting Agent',
    version='0.1',
    description='An agent that harvests satellite text data files',
    url='',
    author='Mike Metcalfe',
    author_email='mike@webtide.co.za',
    license='MIT',
    packages=['agent'],
    install_requires=[
        'requests',
        'cherrypy',
        'mako',
    ],
    python_requires='>=3',
)
