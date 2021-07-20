Country-level Land Availability Model for Agriculture (CLLAMA 1.0) README - Thomas S Ball 2021.

CLLAMA runs in Python and outputs projected land-use data in .csv format. The following packages (that are not included in the Python standard library) are required to run the model:

numpy
pandas
xlrd
pickle-mixin
scipy
seaborn
matplotlib

This can be installed by executing 'python -m pip install --upgrade pip' followed by 'pip install {package}' in the command line (or Anaconda prompt if using Anaconda).

To run the model from the command line simply change to the directory containing 'CLLAMA.py' and execute 'python CLLAMA.py'.

The model is currently in a somewhat barebones state - there are a handful of parameters that can be altered using the 'model_params.py' file. To make more nuanced changes will require a basic level of Python knowledge. All model processes are contained within lib/mod/

The creation of this model has been a learning process; the code written earlier on in the development process is messier and less efficient than that written later. Some plotting functions used to sense-check the model may still be present, which can hopefully be forgiven!
