# urbansim_parcel_bayarea

This is a repository for us to build a clean UrbanSim model for the Bay Area.

- `scripts` is for manual definitions of Orca tables, steps, etc. using Python functions
- `configs` is for definitions generated automatically using the modelmanager/template interface
- `data` is for data
- `notebooks` is for Jupyter notebooks

With just a few lines of code in the manual definitions, we can already load data, estimate and register models, and run steps, all from a notebook: [notebooks-sam/Data-loading.ipynb](https://github.com/ual/urbansim_parcel_bayarea/blob/master/Data-loading.ipynb)


## Setup

I think it will save headaches later on if we use an explicitly-defined Python environment for working on this.

My approach for this has been to use Conda `environment.yml` files. Not sure if this is the best way, so feel free to suggest alternatives.

1. Install the environment specified in the repository (this is slow):

`conda env create -f environment.yml`

2. Activate the environment:

`source activate ual-model` (Mac or Linux)  
or, `activate ual-model` (Windows)

3. Add ModelManager to the environment (it doesn't have a release yet, sorry) - only need to do this once:

`cd path-to-modelmanager`  
`python setup.py develop`

4. Launch Jupyter or run scripts

You'll also need to download the data file. Instructions are in the folder.
