Raspberry Pi Zero W
===================

**NOT** the Zero 2 W

1. Use the Raspberry Pi Imager to install a Debian-based Raspberry Pi OS
	* e.g. `Raspberry Pi OS (Legacy, 32-bit) Lite`
2. Run `make` to prepare the pi
3. You may now run `pipenv run python ./sign.py` from the `src` directory

Installing as a Systemd Service
==============================

Optionally run `make systemd` to install a systemd service that will start the sign on system boot.
This uses [TEMPLATE.service](./TEMPLATE.service) and makes several assumptions about your sign:

1. It uses a USB HID relay
2. It will "register" with an onair [server](../../../server)

Find out the `VIDPID` of your USB relay, and the full URL to register a sign with your server, then run

	make systemd VIDPID=xxxx/xxxx REGISTER_URL=http://your-server/onair/api/v1/register

Find USB HID Relay VIDPID
------------------------
TODO


