from setuptools import find_packages, setup

long_description = "Streamlit-based workflow builder for AltScore"

setup(
    name="altscore-workflow-builder",
    version="0.0.22",
    description="Streamlit-based workflow builder for AltScore",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/altscore/altscore-python",
    author="AltScore",
    author_email="developers@altscore.ai",
    license="MIT",
    entry_points={
        "console_scripts": [
            "run-workflow-builder = altscore_workflow_builder.launch_app:launch_streamlit_app",
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "python-dotenv",
        "loguru",
        "click",
        "requests",
        "pydantic<=1.10.12",
        "httpx",
        "stringcase",
        "python-decouple",
        "python-dateutil==2.8.2",
        "pyjwt",
        "altscore",
        "streamlit",
        "streamlit-agraph",
    ],
    extras_require={},
    python_requires=">=3.8",
)
