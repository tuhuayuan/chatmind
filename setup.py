from setuptools import setup

version = '0.1.0'

setup(
    name='chatmind',
    version=version,
    description="web app build on tornado",
    keywords='tornado wechat yinxin',
    author='tuhuayuan',
    author_email='tuhuayuan@gmail.com',
    url='http://chatmind.webrfs.im',
    license='MIT',
    packages=['chatmind'],
    scripts=[],
    install_requires=[
        "twisted",
        "zope.interface",
        "DBUtils",
        "affinity",
        "python-memcached",
        "MySQL-python"
    ],
    entry_points="""
        # -*- Entry points: -*-
    """
)
