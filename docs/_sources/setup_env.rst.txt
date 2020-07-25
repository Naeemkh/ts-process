Setting Up Environment
======================
It is a better idea to install/use the package in a virtual environment. We
recommend Python 3.7 or 3.8 versions. Here are the steps to set up a virtual 
environment and install the package. In order to install the package, please
download the package from
`Github repository <https://github.com/Naeemkh/tsprocess>`_. The package name
is ``tsprocess``.


Conda
-----
Here are the steps for running the code with anaconda virtual environment. 
Please make sure that you have
`anaconda <https://www.anaconda.com/products/individual>`_ installed on your
system. You can also install
`miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ which is the 
lightweight version of anaconda.

- Step 1: Create a virtual environment

.. code-block:: console

    $ conda create --name your_venv python=3.7

Type 'y' (yes) for popup questions.

- Step 2: Activate the virtual environment

.. code-block:: console

    $ conda activate your_venv

- Step 3: Navigate to the downloaded ``tsprocess`` folder and install the package requirements.

.. code-block:: console

    $ pip3 install -r requirements.txt

- Step 4: Navigate one folder up and install the package.

.. code-block:: console

    $ pip3 install -e tsprocess

That's it. You should be able to *import tsprocess* and use it. However, if you 
want to use the code inside `Jupyter Notebook <https://jupyter.org>`_ 
please follow the next steps.

- Step 5: Register the kernel on Jupyter Notebook:

Make sure that you have activated the virtual environment (Please see Step 2). 
Next, install *ipykernel*:

.. code-block:: console

    $ conda install -c anaconda ipykernel

Type 'y' (yes) for popup questions.
The last step is adding the kernel into Jupyter Notebook. 


.. code-block:: console

    $ python3 -m ipykernel install --user --name your_venv_name

- Step 6: Open your notebook and start processing

In your working directory (any arbitrary directory that you work on your data), 
open terminal and fire up notebook:

.. code-block:: console

    $ jupyter notebook

At the top right corner, there is a button labeled `New` key. Choose your 
recently created kernel (in this example: your_venv_name). Choosing a kernel 
will open a new tab that you can work on.





