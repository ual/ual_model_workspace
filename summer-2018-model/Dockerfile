FROM jupyter/minimal-notebook

USER $NB_UID

RUN git clone https://github.com/ual/urbansim_parcel_bayarea.git && \
	cd urbansim_parcel_bayarea && \
	conda env create -f environment.yml

ENV PATH /opt/conda/envs/ual-model/bin:$PATH

USER $NB_UID

RUN git clone https://github.com/udst/urbansim_templates.git && \
	cd urbansim_templates && \
	python setup.py develop

CMD jupyter notebook --NotebookApp.token='' --ip=* --port=8889 --browser=false --allow-root