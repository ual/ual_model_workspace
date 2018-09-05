# urbansim_parcel_bayarea

This repository is a public workspace for notebooks and other material related to developing a suite of template-based UrbanSim model components.

Related repositories:

- [udst/urbansim_templates](https://github.com/udst/urbansim_templates/) (template library in development)
- [udst/choicemodels](https://github.com/udst/choicemodels/) (discrete choice statistics library in development)


## Tips and guidelines

Lots more resources in the [wiki](https://github.com/ual/urbansim_parcel_bayarea/wiki).

### Setup

The easiest way to get all the dependencies in place is to install Anaconda Python and set up the environment specified in `environment.yml`.

1. Install [Anaconda Python](https://www.anaconda.com/download/#macos).

2. `conda update conda`

3. One-time setup (several minutes)
   `conda env create -f environment.yml`

4. Activate the environment
   `source activate template-env`

5. Install development versions of ChoiceModels and UrbanSim Templates

    Navigate to directory where choicemodels folder should go
    
    ```py
    git clone https://github.com/udst/choicemodels.git
	cd choicemodels
    python setup.py develop
    ```
    
    Navigate to directory where urbansim_templates folder should go
    
    ```py
    git clone https://github.com/udst/urbansim_templates.git
	cd urbansim_templates
    python setup.py develop
    ```

6. All set! Whenever you open a new terminal window, use `source activate template-env` to activate the environment

7. Periodically (or when there's new functionality you want to use) run `git pull` from within the choicemodels and urbansim_templates folders to update the codebases


### File organization

Let's use sub-directories for distinct projects, particularly if they require variations to data schemas or base data. Setting a notebook's working directory to a particular sub-folder will give it access to the configs, scripts, and base data it contains.



## Updates

9-5-2018: Updated the conda environment in `environment.yml` with some newer library versions. Feel free to create separate environment files for different projects as needed.

9-3-2018: Moved older material into a "summer-2018-model" directory and created new directories for parcel and unit model work.