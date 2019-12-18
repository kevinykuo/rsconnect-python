ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

RUN python -m pip install \
	# base requirements
	six click  \
	# extended requirements to render notebooks to static HTML
	nbconvert jupyter_client ipykernel \
	# dev dependencies
	pyflakes pytest pytest-cov

ARG MINICONDA_VERSION=4.7.12.1
RUN curl -L -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda2-4.7.12.1-Linux-x86_64.sh && \
	chmod +x ./miniconda.sh && \
	./miniconda.sh -b -p /opt/anaconda

RUN /opt/anaconda/bin/conda create -y -n testenv \
	python=${PYTHON_VERSION} \
	# base requirements
	six click  \
	# extended requirements to render notebooks to static HTML
	nbconvert jupyter_client ipykernel \
	# dev dependencies
	pyflakes pytest pytest-cov
