from setuptools import setup
import subprocess
import os

# pydlfmt_version = (
#     subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
#     .stdout.decode("utf-8")
#     .strip()
# )
# assert "." in pydlfmt_version
#
# assert os.path.isfile("pydlfmt/version.py")
# with open("pydlfmt/VERSION", "w", encoding="utf-8") as fh:
#     fh.write(f"{pydlfmt_version}\n")
#
# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setup(
    name="pydlfmt",
    # package_dir={"": ""},
    packages=["pydlfmt"],
    version="v0.0.4",  # Ideally should be same as your GitHub release tag varsion
    description="pydlfmt will take a list of objects, dicts, etc and output them to a PDF or XLSX",
    author="Jim Steil",
    author_email="jim@steilonline.com",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpsteil/pydlfmt",
    #     download_url="https://github.com/jpsteil/pydlfmt/archive/refs/tags/v0.0.1.tar.gz",
    keywords=[],
    classifiers=[],
    install_requires=["pytest", "reportlab", "xlsxwriter"],
    zip_safe=False,
)
