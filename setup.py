import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lansync",
    version="0.0.1",
    author="Viktor Barzin",
    author_email="vbarzin@gmail.com",
    description="Make file sharing easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ViktorBarzin/lansync",
    scripts=['bin/lansync'],
    packages=setuptools.find_packages(),
    install_requires=[
        'sshpubkeys'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
