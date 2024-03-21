PIPX_DEFAULT_PATH=/usr/bin/pipx
PIPX_PATH=$(or $(shell which pipx),$(PIPX_DEFAULT_PATH))

PYENV_DEFAULT_PATH=$(HOME)/.pyenv/bin/pyenv
PYENV_PATH=$(or $(shell which pyenv),$(PYENV_DEFAULT_PATH))

all: deps pyenv pipx python
	$(MAKE) pipenv

print-vars:
	@echo "PIPX_DEFAULT_PATH: $(PIPX_DEFAULT_PATH)"
	@echo "PIPX_PATH: $(PIPX_PATH)"

.PHONY: deps
deps:
	sudo apt-get install -y \
		build-essential \
		llvm \
		libbz2-dev \
		libffi-dev \
		liblzma-dev \
		libncurses5-dev \
		libncursesw5-dev \
		libssl-dev \
		libreadline-dev \
		libsqlite3-dev \
		python3-openssl \
		time \
		tk-dev \
		xz-utils \
		zlib1g-dev


.PHONY: pyenv
pyenv: $(PYENV_PATH)

$(PYENV_PATH):
	curl https://pyenv.run | bash
	if ! grep -q "pyenv init -" ~/.bashrc 2> /dev/null; then \
		printf 'export PATH="$$HOME/.pyenv/bin:$$PATH"\neval "$$(pyenv init -)"\neval "$$(pyenv virtualenv-init -)"\n' >> ~/.bashrc; \
	fi

.PHONY: pipx python
pipx: $(PIPX_PATH)

$(PIPX_PATH):
	python -m pip install --user pipx
	pipx ensurepath

.PHONY: pipenv
pipenv: $(PIPX_PATH)
	pipx install pipenv

python: PYTHON_VERSION=3.10.3
python: pyenv deps
	time pyenv install --verbose $(PYTHON_VERSION)
	pyenv global $(PYTHON_VERSION)

