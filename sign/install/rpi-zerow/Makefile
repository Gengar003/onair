PIPENV_DEFAULT_PATH=$(HOME)/.local/bin/pipenv
PIPENV_PATH=$(or $(shell which pipenv),$(PIPENV_DEFAULT_PATH))

PIPX_DEFAULT_PATH=/usr/bin/pipx
PIPX_PATH=$(or $(shell which pipx),$(PIPX_DEFAULT_PATH))

PYENV_DEFAULT_PATH=$(HOME)/.pyenv/bin/pyenv
PYENV_PATH=$(or $(shell which pyenv),$(PYENV_DEFAULT_PATH))

all: deps pyenv pipx #python # assume suitable python is already installed
	$(MAKE) pipenv

print-vars:
	@echo "PYENV_DEFAULT_PATH  : $(PYENV_DEFAULT_PATH)"
	@echo "PYENV_PATH          : $(PYENV_PATH)"
	@echo "PIPX_DEFAULT_PATH   : $(PIPX_DEFAULT_PATH)"
	@echo "PIPX_PATH           : $(PIPX_PATH)"
	@echo "PIPENV_DEFAULT_PATH : $(PIPENV_DEFAULT_PATH)"
	@echo "PIPENV_PATH         : $(PIPENV_PATH)"

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

.PHONY: pipx
pipx: $(PIPX_PATH)

$(PIPX_PATH):
	sudo apt-get install -y pipx
	pipx ensurepath

.PHONY: pipenv
pipenv: $(PIPENV_PATH)

$(PIPENV_PATH): $(PIPX_PATH)
	pipx install pipenv --force

python: PYTHON_VERSION=3.11.2
python: pyenv deps
	time $(PYENV_PATH) install --verbose $(PYTHON_VERSION)
	$(PYENV_PATH) global $(PYTHON_VERSION)

.PHONY: hidapitester
hidapitester: /usr/local/bin/hidapitester

/usr/local/bin/hidapitester: /etc/udev/rules.d/10-usb.rules
	wget https://github.com/todbot/hidapitester/releases/download/v0.5/hidapitester-linux-aarch64.zip -O /tmp/hidapitester.zip
	cd /tmp && unzip /tmp/hidapitester
	sudo cp /tmp/hidapitester /usr/local/bin/hidapitester
	sudo chmod a+x /usr/local/bin/hidapitester
	rm /tmp/hidapitester*

/etc/udev/rules.d/10-usb.rules:
	getent group usb || sudo groupadd usb
	sudo usermod -aG usb $(USER)
	sudo cp 10-usb.rules /etc/udev/rules.d/

/usr/local/bin/sign-state: sign-state /usr/local/bin/hidapitester
	sudo cp -fv sign-state /usr/local/bin/sign-state

.PHONY: systemd
systemd: /etc/systemd/system/onair.service
	sudo systemctl daemon-reload
	sudo systemctl enable onair.service
	sudo systemctl restart onair.service

# LOCAL_PORT will default to a random, unused local port.
/etc/systemd/system/onair.service: LOCAL_PORT=$(shell python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')
/etc/systemd/system/onair.service: TEMPLATE.service pipenv /usr/local/bin/sign-state
	@ if [ -z "$${REGISTER_URL}" ]; then echo "ERROR: Please specify a REGISTER_URL, e.g. \`make REGISTER_URL=... systemd'"; exit 1; fi
	USER=$(USER) \
	PIPENV_PATH=$(shell which pipenv) \
	SIGN_SRC_PATH=$(shell realpath $(CURDIR)/../../src) \
	LOCAL_PORT=$(LOCAL_PORT) \
	envsubst < TEMPLATE.service > /tmp/onair.service
	sudo cp /tmp/onair.service "$@"
