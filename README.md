DiabetIA: predicting diabetic complications using Artificial Intelligence
==============================


Dataset
=========

The DiabetIA dataset 

| Dataset                                                           | Patients | Records | Variables | Download                                                                   |
| ----------------------------------------------------------------- | ---------: | ---------: | --------: | -------------------------------------------------------------------------- |
| DiabetIA              |         137,000 |  440,000 |    550 | [CONAHCYT Repository](TBD) (700 MB)


Install
=======

The only prerequisite is Python (tested with 3.10.6) and Docker.

1. Clone the repo.
2. Run `pip install -r requirements.txt`.
3. Run `python install.py` to build all the libraries inside Docker containers (this can take a while, like 10-30 minutes).

Running
=======

1. Run `python run.py` (this can take an extremely long time, potentially days)
2. Run `python plot.py` or `python create_website.py` to plot results.
3. Run `python data_export.py --out res.csv` to export all results into a csv file for additional post-processing.

Authors
=======

Built by [@AmphoraHealth](github.com/AmphoraHealth) with collaborations from the DiabetIA research group:
* Joaquin Tripp, BS, MS [@joaquintripp](github.com/joaquintripp)
* Daniel Santana Quinteros, BS, MS [@dasaqui](github.com/dasaqui)
* Rafael Pérez Estrada, BS [@RafaPe](github.com/RafaPe)
* Karina Figueroa Mora, PhD [@kaarinita](github.com/kaarinita)
* Arturo Lopez Pineda, PhD [@arturolp](github.com/arturolp)

Related Publication
==================

> Tripp et al (2023). DiabetIA: Building Machine Learning Models for Type 2 Diabetes Complications. MedRXiv https://doi.org/10.1101/2023.10.22.23297277
