
from setuptools import setup, find_packages


from blogger import VERSION

setup(
    name="django-blogger",
    description="A clone of a Blogger blog",
    version = VERSION,
    author="aaron madison",
    author_email="aaron.l.madison@gmail.com",

    long_description=open("README.txt", 'r').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements/requirements.txt').read().split('\n'),
    tests_require=open('requirements/test.txt').read().split('\n'),
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
