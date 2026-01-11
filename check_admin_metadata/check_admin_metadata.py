"""Checks that files are consistent with admin unique identifiers and file counts listed in admin metadata."""

import os
import sys
import webbrowser
from csv import reader


def main():
    print('This program checks that files have the correct unique identifiers and that file counts for that unique '
          '\nidentifier are correct according to an abbreviated admin metadata CSV.'
          '\nA correctly-formatted admin metadata CSV should have the two columns with the following headers:'
          '\n\t- Unique Identifier'
          '\n\t- File Count')
    directories, the_reader = get_info()

    metadata = construct_metadata(the_reader)
    links = []
    open_links = ''
    missing_identifers = []

    metadata_type = input('\nEnter type of unique identifer ["A" for Archival or "C" for Cataloged/MMS ID]: ')
    if metadata_type.casefold() == "C".casefold():
        links = run_mmsids(metadata)
    if links:
        open_links = input(f'\nDo you want to open all the links? [Enter "Y" for yes or "N" for no]: ')
        if open_links.casefold() == 'y'.casefold():
            for link in links:
                webbrowser.open_new_tab(link)
        if open_links.casefold() == 'n'.casefold():
            pass
    missing_identifiers = check_identifiers(directories, metadata)
    if missing_identifiers:
        print(f'\nPlease correct your unique identifiers before comparing file counts.'
              f'\nThis program is ending.')
        exit()
    if not missing_identifiers:
        error_list = check_file_counts(directories, metadata)
        if error_list:
            print(f'\nThe following discrepancies were discovered:')
            for error in error_list:
                print(f'\t{error}')


def construct_metadata(the_reader):
    row_number = 0
    metadata = {}
    for row in the_reader:
        row_number += 1
        if row_number > 1:
            identifier = row[0]
            count = row[1]
            if str(identifier) not in metadata:
                metadata[str(identifier)] = count
            else:
                print(f'\nThere is a problem with your metadata. {identifier} is not unique.'
                      f'\nThis program is ending. Please check your metadata and run again.')
                exit()
    return metadata


def run_mmsids(metadata):
    primo_link = ''
    links = []
    webbrowser.get(using='chrome')
    print(f'Ensure MMS ID validity by copying and pasting the following links into your browser.')
    print(f'Warnings will appear for MMS IDs ending in 0, but this program cannot otherwise determine validity.')
    print()
    print(f'{"MMS ID":<20}{"Valid ID":^14}{"Link":>20}')
    for mmsid in metadata:
        formatted_correctly = 'Y'
        primo_link = f'https://i-share-uiu.primo.exlibrisgroup.com/permalink/01CARLI_UIU/1njj0oi/alma{mmsid}'
        links.append(primo_link)
        if not mmsid.endswith('9'):
            formatted_correctly = 'N'
        print(f'{mmsid:<20}{formatted_correctly:^14}{primo_link:>20}')
    return links


def get_info():
    infile_path = input('\nPlease enter the path to your CSV: ')
    infile = open(infile_path, 'r', encoding='utf-8')
    the_reader = reader(infile)
    directories = []
    error_list = []
    directory = input('\nPlease enter the directory (e.g. /Volumes/digitize/project/QAqueue/session) in which your '
                      'files are stored: ')
    if sys.platform == 'win32':
        access_directory = f'{directory}\\access'
        directories.append(access_directory)
        pres_directory = f'{directory}\\preservation'
        directories.append(pres_directory)
    if sys.platform == 'darwin':
        access_directory = f'{directory}/access'
        directories.append(access_directory)
        pres_directory = f'{directory}/preservation'
        directories.append(pres_directory)
    return directories, the_reader


def check_identifiers(directories, metadata):
    missing_identifiers = []
    for directory in directories:
        file_tree = construct_file_tree(directory)
        file_tree_identifiers = list(file_tree.keys())
        metadata_identifiers = list(metadata.keys())
        file_missing = list(filter(lambda x: x not in file_tree_identifiers, metadata_identifiers))
        if file_missing:
            missing_identifiers.extend(file_missing)
            print(
                f'The following unique identifiers are present in the metadata CSV but are not present in {directory}: ')
            for file in file_missing:
                print(f'\t{file}')
        metadata_missing = list(filter(lambda x: x not in metadata_identifiers, file_tree_identifiers))
        if metadata_missing:
            missing_identifiers.extend(metadata_missing)
            print(
                f'The following unique identifiers are present in {directory} but are not present in the '
                f'metadata CSV: ')
            for file in metadata_missing:
                print(f'\t{file}')
    return missing_identifiers


def construct_file_tree(directory):
    file_list = os.listdir(directory)
    file_tree = {}
    for file in file_list:
        if file != '.Ds_Store':
            filename, suffix = file.split(".")
            if "-" in filename:
                prefix, file_number = filename.split("-")
                if str(prefix) not in file_tree.keys():
                    file_tree[str(prefix)] = 1
                else:
                    file_tree[prefix] += 1
            else:
                pass
    return file_tree


def check_file_counts(directories, metadata):
    error_list = []
    for directory in directories:
        file_tree = construct_file_tree(directory)
        for file, count in file_tree.items():
            file_tree_count = file_tree.get(file)
            metadata_count = metadata.get(file)
            if int(file_tree_count) != int(metadata_count):
                error_list.append(f'File counts for the unique identifier {file} are not consistent, with '
                                  f'{file_tree_count} files in {directory} and {metadata_count} files '
                                  f'listed in the metadata CSV.')
    return error_list


if __name__ == '__main__':
    main()
