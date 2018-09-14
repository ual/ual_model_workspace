# ual_model_workspace

This repository is a public workspace for notebooks and other material related to developing a suite of template-based UrbanSim model components. See [wiki](https://github.com/ual/urbansim_parcel_bayarea/wiki) for lots more info.

Related repositories:

- [udst/urbansim_templates](https://github.com/udst/urbansim_templates/) (template library in development)
- [udst/choicemodels](https://github.com/udst/choicemodels/) (discrete choice statistics library in development)


## Setup

The easiest way to get all the dependencies in place is to use a conda environment.

1. Install [Anaconda Python](https://www.anaconda.com/download/#macos)

	Or if you've already installed it previously, run: `conda update conda`

2. Build the environment (takes several minutes): `conda env create -f environment.yml`

3. Activate the environment: `source activate template-env`

	(For Windows, just use `activate template-env`)

4. Install development versions of ChoiceModels and UrbanSim Templates

    Navigate to directory where folders should go, then:
    
    ```
    git clone https://github.com/udst/choicemodels.git
	cd choicemodels
    python setup.py develop
	cd ..
    git clone https://github.com/udst/urbansim_templates.git
	cd urbansim_templates
    python setup.py develop
    ```

5. All set! Whenever you open a new terminal window, use `source activate template-env` to activate the environment

6. Periodically (or when there's new functionality you want to use) run `git pull` from inside the choicemodels and urbansim_templates folders to update the codebases
