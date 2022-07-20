from setuptools import setup

setup(
    name="pydlfmt",
    packages=["pydlfmt"],
    version="v0.0.3",  # Ideally should be same as your GitHub release tag varsion
    description="pydlfmt will take a list of objects, dicts, etc and output them to a PDF or XLSX",
    author="Jim Steil",
    author_email="jim@steilonline.com",
    url="https://github.com/jpsteil/pydlfmt/tree/v0.0.1",
    download_url="https://github.com/jpsteil/pydlfmt/archive/refs/tags/v0.0.1.tar.gz",
    keywords=["tag1", "tag2"],
    classifiers=[],
    install_requires=["pytest", "reportlab", "xlsxwriter"],
    zip_safe=False,
)
