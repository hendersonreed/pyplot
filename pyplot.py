import serial
import sys
import re

# config section

PLOTTER_NAME = "/dev/ttyUSB0"
PLOTTER_MAX_X = 10300
PLOTTER_MAX_Y = 7650

# end of config section

file_contents = ""


def scale_command(s, scale_ratio):
    # Match the command part (letters) and the numeric part (digits and commas)
    command_match = re.match(r'([A-Za-z]+)', s)
    numeric_match = re.search(r'(\d+)?,(\d+)?', s)
    x = 0
    y = 0

    if command_match:
        command = command_match.group(1)
        if numeric_match.group():
            x = x * scale_ratio
            y = y * scale_ratio
            nums = f"{x},{y}"
        else:
            nums = ""
    return f"{command}{nums}"


def find_max_xy(commands):
    coordinates = [re.search(r'(\d+)?,(\d+)?', command)
                   for command in commands]
    xmax = 0
    ymax = 0
    for each in coordinates:
        if each:
            xmax = max(xmax, int(each.group(1)))
            ymax = max(ymax, int(each.group(2)))

    return xmax, ymax


def scale_to_plotter(file_contents):
    commands = file_contents.split(';')
    for each in commands:
        each = scale_command(each)
    return commands


def chunk(commands):
    """
    Splits the file contents into at-most 60 byte chunks of valid commands separated by semicolons.
    """  # noqa

    current_chunk = ""
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

scaled_commands = scale_to_plotter(file_contents)
command_chunks = chunk(scaled_commands)

try:
    # Define the serial port
    ser = serial.Serial(PLOTTER_NAME, timeout=1)

    # Perform any serial communication operations here
    for each in command_chunks:
        ser.write(str.encode(each))
        wait_for_end_of_OA(ser)

    # Close the serial port when done
    ser.close()


except serial.SerialException:
    print("Couldn't connect to plotter")
