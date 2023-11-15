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

The main prerequisites are Python (tested with version 3.10.6) and R (tested with version 4.2.2). It is strongly recommended to install Make to orchestrate the complex pipelines for data transformation or training.

Also we recommend to verify if you have the commands wget and unzip available on your operative sistem

To create the virtual environment used for Python, you can run the command `make create_env`. Alternatively, you can manually install all the dependencies using the file requirements.txt.

To download the diabetia database used for this repository you can run the command `make diabetia`. Alternatively you can download it from [Conahcyt](https://repositorio-salud.conacyt.mx/jspui/bitstream/1000/296/hk_database_17ago2023.zip), uncompress it as data/hk_database.csv and run secuentially the codes unde preprocess folder.

The main code was developed to run on Unix-like environments such as macOS and Linux, but it can also run on Windows if you install Make (or without it if you run the Python or R codes manually).

Running
=======

The scripts under scripts2print and scripts2plot can be executed manually using Python with commands like `python3 scripts2print/table_one_patients.py`. Similarly, the scripts under scripts4ml can also be run manually. However, we strongly recommend using Make to orchestrate the pipelines for optimal execution.

## Running the pipelines

To check if the pipeline can run under your installation you can run the command:
`make test`

To run the complete pipeline on the first fold you can run the command:
`make 1-fold`

To run the complete pipeline on the complete 5-folds verification you can run the command:
`make 5-folds`

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
