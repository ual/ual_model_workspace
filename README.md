# ual_land_use_model

This is a repository for us to build a clean UrbanSim model for the Bay Area.


## Setup

I think it will save headaches later on if we use an explicitly-defined Python environment for working on this.

My approach for this has been to use Conda `environment.yml` files. Not sure if this is the best way, so feel free to suggest alternatives.

1. Install the environment specified in the repository (this is slow):

`conda env create -f environment.yml`

2. Activate the environment:

`source activate ual-model` (Mac or Linux)  
or, `activate ual-model` (Windows)

3. Add ModelManager to the environment (it doesn't have a release yet, sorry):

`cd path-to-modelmanager`
`python setup.py develop`

4. Launch Jupyer or run scripts
