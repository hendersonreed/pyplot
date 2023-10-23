import serial
import sys
import time

file_contents = ""


def chunk(file_contents):
    """
    Splits the file contents into at-most 60 byte chunks of valid commands separated by semicolons.
    """  # noqa
    chunks = []

    current_chunk = ""
    commands = file_contents.split(';')

    for command in commands:
        # Check if adding the next command and the
        # OA command exceeds the 60-byte limit
        if len(current_chunk) + len(command) + 3 + 1 <= 60:
            current_chunk += command + ";"
        else:
            chunks.append(current_chunk + "OA;")
            current_chunk = command + ";"

    # Append the last chunk to the list of chunks
    if current_chunk:
        chunks.append(current_chunk.strip(';'))  # Remove trailing semicolon

    return chunks


def wait_for_end_of_OA(ser):
    curr = True
    while curr != b'\r':
        curr = ser.read()
    return True


# Check if at least one command-line argument is provided
if len(sys.argv) < 2:
    print("Error: Please provide a file as the first argument")
else:
    # Get the filename from the command-line argument
    filename = sys.argv[1]

    try:
        # Attempt to open and read the file
        with open(filename, 'r') as file:
            file_contents = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")

command_chunks = chunk(file_contents)

try:
    # Define the serial port
    ser = serial.Serial('/dev/ttyUSB0', timeout=1)

    # Perform any serial communication operations here
    for each in command_chunks:
        ser.write(str.encode(each))
        wait_for_end_of_OA(ser)

    # Close the serial port when done
    ser.close()


except serial.SerialException:
    print("Couldn't connect to plotter")
