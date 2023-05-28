import json


def find_missing_gopro(filename):
    # Parse the file structure
    id_dict = parse_file_structure(filename)
    # Initialize an empty list to store id's with missing gopro files
    missing_gopro = []

    # Iterate over the id's in the dictionary
    for id, files in id_dict.items():
        # If there are no files under 'gopro', add the id to the list
        if len(files) == 0:
            missing_gopro.append(id)

    # Write the id's with missing gopro files to a new file
    with open('missing_gopro.txt', 'w') as f:
        for id in missing_gopro:
            f.write(id + '\n')


# Call the function
find_missing_gopro('folder_structure.txt')
