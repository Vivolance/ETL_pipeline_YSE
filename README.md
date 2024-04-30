# Prototype Playground

## Objective
- Prototype solutions for extract search results from a raw yahoo search engine HTML

## Understanding Spacy

Spacy is a machine learning package which allows us to easily load and use common NLP models

It provides 3 common models; there are more but let's focus on these 3 common ones
- en_core_web_sm (uses convolutional neural network, smallest but fastest)
- en_core_web_lg (good balance between speed and performance, convolutional neural network)
- en_core_web_trf (uses transformers, slower but more performant than en_core_web_lg)

## We will use en_core_web_lg first for our experiment

Download the model; The model is a fancy MB / GB worth of vectors, which represents it's understanding of NLP.

This model is pre-trained.

These "vectors" have a common name; We call them weights

```
python -m spacy download en_core_web_lg
```

## Installing dependencies

```commandline
poetry install
```

## Upgrade dependencies on poetry

Edit `pyproject.toml` to have the new version under `tool.poetry.dependencies`

Create a new file with
- `--no-update` ensures we don't update other dependencies that didn't have a change in dependencies in `pyproject.toml`

```commandline
poetry lock --no-update
```

## Creating a venv

```commandline
poetry shell
```



