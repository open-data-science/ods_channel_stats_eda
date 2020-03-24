# ods_channel_stats_eda
Public analysis of ODS Channel questionnaire statistics.

This repo contains two versions of the audience stats summary: [for those who just wants to look at graphs](research_eda_concise_version.ipynb) and [for those who wants to crunch numbers themselves](research_eda.ipynb). The former one utilizes imports from external to the jupyter notebook .py file [eda_utils.py](eda_utils.py), while the latter keeps all the code inside notebook and contains more comments on what exactly was done. First one is for beginners, non-professionals, those who just want to understand the audience better and the second is for more curious ones.

## Installation and initial setup

```bash
poetry install
poetry run jupyter notebook
```

In case of missing python version and poetry, they can be installed with [pyenv](https://github.com/pyenv/pyenv) and [poetry](https://github.com/python-poetry/poetry). Alternatively, you can try using separate [script](https://github.com/Hiyorimi/i_am_new_python_developer) to setup developer environment at your own risk.
