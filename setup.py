import setuptools

setuptools.setup(
    name="multiSMASH",
    version="0.4.0",
    description="A snakemake-based antiSMASH wrapper for large-scale analyses",
    author="Zachary L. Reitz",
    author_email="zlreitz@gmail.com",
    url='https://github.com/zreitz/multismash',
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    install_requires=[
        "pulp<2.8.0",
        "snakemake>=7.32.3"
    ],
    python_requires=">=3.9",
    package_dir={"": "multismash"},
    entry_points={"console_scripts": [
        "multismash = multismash:main",
        "multismash-config = multismash_config:main"
        ]}
)
