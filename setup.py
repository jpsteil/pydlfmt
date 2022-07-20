from setuptools import setup

setup(
    name="pydlfmt",
    version="0.1",
    description="Datalist Formatter",
    url="https://pydlfmt.com",
    author="Jim Steil",
    author_email="jim@qlf.com",
    license="MIT",
    packages=["pydlfmt"],
    include_package_data=True,
    install_requires=["reportlab", "xlsxwriter"],
    zip_safe=False,
)


from distutils.core import setup

setup(
    name="pydlfmt",
    packages=["pydlfmt"],
    version="v0.0.1",  # Ideally should be same as your GitHub release tag varsion
    description="pydlfmt will take a list of objects, dicts, etc and output them to a PDF or XLSX",
    author="Jim Steil",
    author_email="jim@steilonline.com",
    url="github package source url",
    download_url="download link you saved",
    keywords=["tag1", "tag2"],
    classifiers=[],
)
