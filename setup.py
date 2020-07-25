import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tsprocess", 
    version="0.0.1",
    author="Naeem Khoshnevis",
    author_email="khoshnevis.naeem@gmail.com",
    maintainer="Naeem Khoshnevis, Fabio Silva, Ricardo Taborda, Christine Goulet",
    maintainer_email = "khoshnevis.naeem@gmail.com,fsilva@usc.edu, rtaborda@eafit.edu.co,cgoulet@usc.edu",
    description="Ground motion time series processing tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Naeemkh/ts-process",
    license="BSD 3-Clause",
    packages=setuptools.find_packages(exclude=['docs*', 'tests*']),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    python_requires='>=3.7',
)