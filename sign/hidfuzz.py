import hid
import time

try:
    print("Opening the device")

    h = hid.device()
    h.open(0x5131, 0x2007)

    print("Manufacturer: %s" % h.get_manufacturer_string())
    print("Product: %s" % h.get_product_string())
    print("Serial No: %s" % h.get_serial_number_string())

    # enable non-blocking mode
    h.set_nonblocking(1)
    # VID and PID number of the relay's module:
    # VID: 5131
    # PID: 2007
    # Generally, it is a fixed value and does not need to be changed.

    # Communication protocol description:
    # Default communication baud rate: 9600BPS
    # Turn on the 1-channel relay switch: A0 01 01 A2
    # Turn off the 1-channel relay switch: A0 01 00 A1
    # write some data to the device
    print("Write the data")
    h.write([0xA0, 0x01, 0x01, 0xA2]) # open

    # wait
    time.sleep(1)

    # read back the answer
    print("Read the data")
    while True:
        d = h.read(64)
        if d:
            print(d)
        else:
            break

    time.sleep(1)
    print("Closing the device")
    
    h.write([0xA0, 0x01, 0x00, 0xA1]) # close
    h.close()

except IOError as ex:
    print(ex)
    print("You probably don't have the hard-coded device.")
    print("Update the h.open() line in this script with the one")
    print("from the enumeration list output above and try again.")

print("Done")