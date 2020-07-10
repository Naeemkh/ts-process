Setting up Environment
======================
It is a better idea to install/use the package in a virtual environment. We recommend Python 3.7 or 3.8 versions. Here are the steps to set up a virtual environment.

.. code-block:: console

    $ python3 -m venv your_env_name
    $ source your_env_name/bin/activate

Type ``deactivate`` to close the virtual environment. Use `Jupyter Notebook<https://jupyter.org>` for long and interactive processing. Use the following command to add your virtual environment into Jupyter Notebook as a Python kernel. 

.. code-block:: console

    $ python3 -m ipykernel install --user --name your_env_name --display-name "your_display_name"

``your_display_name`` is a name that your environment will be listed with that name on Jupyter Notebook.  


Installation
------------ 

In order to install the package, please download the package from `Github repository <https://github.com/Naeemkh/tsprocess>`_. The package name is ``tsprocess``. Install the package according to the following commands:

.. code-block:: console

    $ pip install -r tsprocess/requirements.txt
    $ pip install -e tsprocess
    $ python
    >>> from tsprocess import project as pr
    >>> project_1 = pr.Project('project1')

