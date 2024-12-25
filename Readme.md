# Personalized Intelligent Tutoring System (PITS)

This repo is based on the book [Building Data-Driven Applications with LlamaIndex](https://www.packtpub.com/en-us/product/building-data-driven-applications-with-llamaindex-9781835089507) ([repo](https://github.com/PacktPublishing/Building-Data-Driven-Applications-with-LlamaIndex)) which I did some improvements to.

## Introduction

This repo is a personalized intelligent tutoring system (PITS) that uses LlamaIndex to generate slides and quizzes based on the user's study materials.

# Install requirements

- use pip to install the requirements
```bash
pip install -r requirements.txt
```

- Install spacy
```bash
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
```


# TODOs
- [ ] Add showing slides in the UI
- [ ] Add other options for model providers
- [ ] resume session doesn't work properly before "slides