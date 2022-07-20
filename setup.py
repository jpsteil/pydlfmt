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
