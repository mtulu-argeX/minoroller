import threading
import socket
import sys
import time
import platform
# Example of interaction with a BLE UART device using a UART service
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

host = ''
port = 9000
locaddr = (host,port)


host_ip = "0.0.0.0"
response_port = 8890
uart = None

class Tello:
    def __init__(self):
        self._running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host_ip, response_port))  # Bind for receiving

    def terminate(self):
        self._running = False
        self.sock.close()

    def recv(self):
        """ Handler for Tello states message """
        while self._running:
            try:
                msg, _ = self.sock.recvfrom(1024)  # Read 1024-bytes from UDP socket
                A = msg.decode(encoding="utf-8")
                print("states: {}".format(A))
                A=[float(x.split(":")[1]) for x in A.strip().split(";")[:-1]]
                #formatMes="%4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f" % (A[0], A[1], A[2],  A[3], A[4], A[5],A[9], A[10], A[12] )
                formatMes="%4.0f%4.0f%4.0f%4.0f%4.0f" % (A[7], A[10], A[2], A[9],A[3] )
                #print ("A %s"%formatMes.encode(encoding="utf-8"))
                #uart.write(b'%s\r\n'%formatMes)
                #print ("A ",type (formatMes))
                _tmp = ("%s"%(formatMes)).encode()
                #print ("B ",type(_tmp), _tmp)
                uart.write(_tmp)

                #uart.write(_tmp)
                #uart.write(bytes('%s\r\n'%_tmp),'utf-8')
            except Exception as err:
                print(err)



# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recvDrone():
    count = 0
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break


def stateDrone():
    count = 0
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break


#print ('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')

#print ('end -- quit demo.\r\n')


def initDrone():

    #recvThread create
    recvThread = threading.Thread(target=recvDrone)
    recvThread.start()
    t = Tello()
    recvThread = threading.Thread(target=t.recv)
    recvThread.start()
    
   # stateThread = threading.Thread(target=stateDrone)
   # stateThread.start()

def sendCommandDrone(msg ):
    try:
        if 'end' == msg:
            print ('...')
            sock.close()

        # Send data
        msg = msg.encode(encoding="utf-8")
        sent = sock.sendto(msg, tello_address)
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()


# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.

def initBle():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()
    
    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))
    
    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

     # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        device = UART.find_device()
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout.
    return device


def main():
    device = initBle()
    initDrone()

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        UART.discover(device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        global uart
        uart = UART(device)
        print(uart)
        # Write a string to the TX characteristic.
        uart.write(b'Hello world!\r\n')
        #print("Sent 'Hello world!' to the device.")

        # Now wait up to one minute to receive data from the device.
        while True:
        #print('Waiting up to 60 seconds to receive data from the device...')
            received = uart.read(timeout_sec=60)
            if received is not None:
                # Received data, print it out.
                print('Received: {0}'.format(received))
            else:
                # Timeout waiting for data, None is returned.
                print('Received no data!')
                continue
            sendCommandDrone(received)
            #sendCommandDrone("state?")
    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()


# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)



