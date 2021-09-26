"""
A CLI program tool that takes an JPEG, JPG or PNG image as input and the following set of flags:
* -f <filepath> to hide a generic file in the input image file.
* -t to hide some text in the input image file, this argument takes a <path> value.
Each set of command line flags will have a unique heading or byte sequence before the actual data appears below in the output modified image file.

The main function validates the arguments using argparse, opens the file using os and sys.
checks to see that the input file is a file is done, as well for if  the output file already exists.
We also check that either fileor text is set. and if so that their input file path value exists.

Then we open the input file using Image.open, and creating the steg_image variable holding the data for the modified image file.
    Depending on if args.file or text is set, call different functions
    for each case, writing an apropriate headers to the args.input file byte stream after opening it.
    The headers for each case before the actual data is:
    * "|text_start|" if the args.text is set
    * "|file_start:<filename>|" if args.file is set, the <filename> is given by the parameter of the <filepath> file name and extension.
    Each case will also end with the "_end" suffix following the same format as the header.
    After all this, save the steg_image to the filepath specified by args.output and print a message to the screen/user.

The -d flag looks for each of these headers and reads all bytes until the ending.
The -d argument flag can be used to extract all hidden data in the given input image file, the program should then
walk through the bytes of the steg_image and look for either "|text_start|" or "|file_start:" followed by a filename and an ending "|".
If one of these headers are found the program should read until a matching ending header is found then print the text to the screen or save the bytes to a file on the system.
"""

import argparse
import os
import sys

text_start = "|text_start|"
text_start_len = len(text_start)
text_end = "|text_end|"
text_end_len = len(text_end)
file_start = "|file_start:"
file_start_len = len(file_start)
file_end = "|file_end:"
file_end_len = len(file_end)


def main():
    parser = argparse.ArgumentParser(
        description="A tool that takes an JPG or PNG image as input, hides some data in it and saves the new modified image.")
    #  parser.add_argument(
    #     "-i", "--input", help="The input image file to be modified.", required=True)
    parser.add_argument("input", type=str,
                        help="The input image file to be modified.")
    parser.add_argument(
        "-o", "--output", help="The output image file to be created.")
    parser.add_argument(
        "-v", "--verbose", help="Output more information about the process.", action="store_true")
    parser.add_argument(
        "-f", "--file", help="The file to be hidden in the input image file.")
    parser.add_argument(
        "-t", "--text", help="The text to be hidden in the input image file.")
    parser.add_argument(
        "-d", "--decode", help="Decode the input image file.", action="store_true")
    args = parser.parse_args()

    # Check if the input file exists
    if not os.path.isfile(args.input):
        print("Missing input file!")
        sys.exit(1)

    # Check if the output file already exists
    if args.output and os.path.isfile(args.output):
        print("The output file already exists. Do you want to overwrite it? ", end="")
        if input("(y/n): ").lower() != "y":
            sys.exit(1)

    # Check if the file to be hidden exists
    if args.file and not os.path.isfile(args.file):
        print("The file '{}' to be hidden does not exist.".format(args.file))
        sys.exit(1)

    # Check if the input file is a file is done, as well for if  the output file already exists, in such case prompts the user if it should be overwritten.
    if args.decode:
        decode(args.input, args.verbose)
    elif args.file:
        encode_file(args.input, args.file, args.output, args.verbose)
    elif args.text:
        encode_text(args.input, args.text, args.output, args.verbose)
    else:
        print("No file or text to hide was given.")
        sys.exit(1)


def encode_file(image_input, filepath, outpath, verbose):
    """
    Encode the file in the input image file.
    Write "|file_start:<filename>|" where the <filename> is the file name and extension given by the filepath parameter.
    Then write all bytes of the file specified by filepath to the steg_image, and lastly write an ending |file_end| header.
    """
    with open(outpath, "wb") as steg_image:
        with open(image_input, "rb") as source_image:
            # Read the bytes of the image file
            image_bytes = source_image.read()
            steg_image.write(image_bytes)
            if verbose:
                print("Source image was copied to the output file. (" +
                      str(len(image_bytes)) + " bytes)")

        # Open the file to be hidden
        with open(filepath, "rb") as source_file:
            # Read the bytes of the file
            file_bytes = source_file.read()

            filename = os.path.basename(filepath)
            # Write the header to the steg_image
            steg_image.write("{}{}|".format(file_start, filename).encode())

            # Write the bytes of the file to the steg_image
            steg_image.write(file_bytes)

            # Write the ending header to the steg_image
            steg_image.write("{}{}|".format(file_end, filename).encode())

            print("File was hidden in the image file. (" +
                  str(len(file_bytes) + file_start_len + len(filepath) + 1 + file_end_len) + " bytes)")

    print("The modified image was successfully saved to {}".format(outpath))


def encode_text(image_input, text, outpath, verbose):
    """
    Encode the text in the input image file.
    Write "|text_start|" to the steg_image, then write all bytes of the text to the steg_image, and lastly write an ending |text_end| header.
    """
    with open(outpath, "wb") as steg_image:
        with open(image_input, "rb") as source_image:
            # Read the bytes of the image file
            image_bytes = source_image.read()
            steg_image.write(image_bytes)
            if verbose:
                print("Source image was copied to the output file. (" +
                      str(len(image_bytes)) + " bytes)")

        # Get the byte representation of the text string
        text_bytes = text.encode()

        # Write the header to the steg_image
        steg_image.write(text_start.encode())

        # Write the bytes of the text to the steg_image
        steg_image.write(text_bytes)

        # Write the ending header to the steg_image
        steg_image.write(text_end.encode())

        print("Text was hidden in the image file. (" +
              str(len(text_bytes) + text_start_len + text_end_len) + " bytes)")

    print("The modified image was successfully saved to {}".format(outpath))


def decode(image_input, verbose):
    # Open the input image file Create the steg_image variable holding the data for the modified image file
    with open(image_input, "rb") as steg_image:
        """
        Decode the input image file.
        Walk through the bytes of the steg_image and look for either "|text_start|" or "|file_start:" followed by a filename and an ending "|".
        If one of these headers are found the program should read until a matching ending header is found then print the text to the screen or save the bytes to a file on the system.
        """

        # Create a variable to hold the bytes of the steg_image
        steg_bytes = steg_image.read()
        image_format = image_input.split(".")[-1].upper()

        # steg_bytes = steg_image.tobytes()
        if verbose:
            print("Image format: {}".format(image_format))
            print("Bytes read from file: {:02X}".format(len(steg_bytes)))
            print("Slice from start: " + str(steg_bytes[0:50]))
            print("Slice from end:   " + str(steg_bytes[-50:]))

        # Create a variable to hold the current byte position
        offset: int = 0
        if (image_format == "PNG"):
            # PNG images have a header of 12 bytes and end with a footer of 4 bytes with the data "IEND".
            # find the first index of "IEND"
            end_index = steg_bytes.find(b"IEND")
            if (end_index == -1):
                print("No ending IEND found.")
                sys.exit(1)
            offset = end_index + 4
            if verbose:
                print("Found IEND at offset {:02X}".format(end_index))
        elif (image_format == "JPEG" or image_format == "JPG"):
            # JPEG images have a header of 2 bytes and end with a footer of 2 bytes with the data "\xff\xd9".
            # find the first index of "\xff\xd9"
            end_index = steg_bytes.find(b"\xff\xd9")
            if (end_index == -1):
                print("No ending IEND found.")
                sys.exit(1)
            offset = end_index + 2
            if verbose:
                print("Found \xff\xd9 at offset {:02X}".format(end_index))

        found_texts = 0
        found_files = 0
        # Loop through the steg_bytes
        while offset < len(steg_bytes):
            if verbose:
                precent = 100 * (offset / len(steg_bytes))
                if offset == len(steg_bytes) - 1:
                    precent = 100.0
                print("offset: {:02X} ({:.2f}%)".format(offset, precent))
            # Check if the current byte is the text_start header
            if offset + text_start_len < len(steg_bytes) and steg_bytes[offset:offset + text_start_len] == text_start.encode():
                if verbose:
                    print("Found text_start at offset: {:02X}".format(offset))
                # Read the bytes until the text_end header
                text_bytes, offset = read_until(
                    steg_bytes, offset + text_start_len, text_end)

                # Decode the text bytes
                text = text_bytes.decode()

                # Print the text to the screen
                print("--- Text {} Start ---".format(found_texts + 1))
                print(text)
                print("---- Text {} End ----".format(found_texts + 1))

                # Set the offset to the end of the text_end header
                offset += text_end_len
                found_texts += 1
            # Check if the current byte is the file_start header
            elif offset + file_start_len < len(steg_bytes) and steg_bytes[offset:offset + file_start_len] == file_start.encode():
                if verbose:
                    print("Found file_start at offset: {:02X}".format(offset))
                # Get the file name from the header, the filename ends with a "|"
                file_name_bytes, offset = read_until(
                    steg_bytes, offset + file_start_len, "|")
                offset += 1  # skip the "|"

                # Decode the file name bytes
                file_name = file_name_bytes.decode()

                file_bytes, offset = read_until(
                    steg_bytes, offset, file_end + file_name + "|")

                # Check if file_name already exists
                save_file = True
                if os.path.isfile(file_name):
                    print(
                        "The file '{}' already exists. Do you want to overwrite it? ".format(file_name), end="")
                    if input("(y/n): ").lower() != "y":
                        save_file = False

                # Create a file with the file name
                if save_file:
                    with open(file_name, "wb") as file:
                        # Write the file bytes to the file
                        file.write(file_bytes)
                        print(
                            "Successfully extracted file '{}'! ({} bytes)".format(file_name, len(file_bytes)))

                # Set the offset to the end of the file_end header
                offset += file_end_len
                found_files += 1
            else:
                offset += 1
    print("\nDone decoding, {} hidden text message(s) and {} hidden file(s) were found.".format(
        found_texts, found_files))


def read_until(steg_bytes, offset, ending):
    """
    Read the bytes of the steg_bytes from the offset until the ending byte sequence is found.
    Return the bytes read and the offset of the ending byte sequence.
    """
    # Create a variable to hold the bytes read
    bytes_read = b""

    # Loop through the steg_bytes
    while offset < len(steg_bytes):
        # Check if the current byte is the ending byte sequence
        if steg_bytes[offset:offset + len(ending)] == ending.encode():
            # Return the bytes read and the offset of the ending byte sequence
            return bytes_read, offset
        # Read the next byte
        bytes_read += steg_bytes[offset:offset + 1]
        offset += 1


if __name__ == "__main__":
    main()
