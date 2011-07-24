
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
    test_requirements=['django', 'mock', 'django-debug-toolbar'],
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