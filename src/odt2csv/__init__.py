"""
odt2csv
Created by: Samarthya Lykamanuella
Establishment year: 2025

This program converts an OOMMF DataTable output (ODT) into a CSV-like file.
Created on 2023-07-08 by Samarthya Lykamanuella (github.com/groaking).
Adapted into PyPI on 2025-04-14 by Samarthya Lykamanuella (github.com/groaking).

LICENSE NOTICE:
===============

This file is part of odt2csv.

odt2csv is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

odt2csv is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with odt2csv. If not, see <https://www.gnu.org/licenses/>.
"""

# For separating filenames/paths.
# (Default package from Python installation. No PIP extension required.)
import os

# Local import.
from .exceptions import InvalidParserBehaviorError
from .exceptions import MultipleTableStartsError
from .exceptions import ODTFileNotFoundError

def despacifier(str_):
    """
    A simple function that removes redundant (double) space characters.
    """
    while str_.__contains__('  '):
        str_ = str_.replace('  ', ' ')
    # Ensures that the string does not start or end in blank spaces
    str_ = str_.strip()
    return str_

def remove_empty(input_list=[]):
    """
    Remover of empty list items or list items with only blank spaces.
    Assumes each item in input_list is a string.
    """
    # The new list
    output_list = []
    
    # Read the input list/array
    for a in input_list:
        l = a.strip()
        if len(l) == 0:
            # The list item is empty
            # No need to append to the new list
            pass
        else:
            # You've made it, item list!
            output_list.append(l)
    
    # Return the sanitized list
    return output_list

def space2comma(str_):
    """ Turn all space characters into commas.
    """
    # Despacify!
    str_ = despacifier(str_)
    # Convert spaces to commas
    str_ = str_.replace(' ', ',')
    return str_

def tokenize_header(str_):
    """ Sanitize the header so that all column names are quoted (string-like)
    and all curly brackets are removed.
    """
    l = despacifier(str_)
    
    # First step: detecting the existence of the opening '{' delimeter.
    # The variable 'p' is retained for historical reasons.
    # 'ch' stands for 'column header'.
    p = ch = remove_empty(l.split('{'))
    
    # The sanitized column header.
    sanitized_ch = ''
    
    # Next step: after splitting the line by the existence of '{',
    # find the closing '}' delimeter.
    for q in p:
        q = q.strip()
        if q.__contains__('}') and not q.startswith('}'):
            r = remove_empty(q.split('}'))
            # Append the first item of r, r[0], which is the only item encapsulated by {...} expression.
            sanitized_ch += "\"\"," if r.__len__() == 0 else "\"" + r[0] + "\","
            
            # r[1], r[2], etc., if they exist, are just regular substring
            # that do not contain blank spaces.
            # Do normal splitting-by-whitespace if they exist.
            if len(r) > 1:
                for s in r[1].split(' '):
                    sanitized_ch += "\"" + s + "\","
        
        # If no '}' delimeter is found, then the substring has no blank space in it.
        # Do normal splitting-by-whitespace.
        else:
            r = remove_empty(q.split(' '))
            for s in r:
                if s.startswith('}'):
                    s = s[1:]
                sanitized_ch += "\"" + s + "\","
    
    # Trim trailing commas.
    sanitized_ch = sanitized_ch[:-1]
    return sanitized_ch

def convert(odt_input: str, csv_output: str = None, output_suffix: str = None, keep_unit: bool = False, parser_behavior: int = 2):
    """
    This function converts an OOMMF Data Table (ODT) file into a CSV file.
    The CSV file is output to the same directory as the ODT, by default.
    
    Due to the behavior of OOMMF evolver, which appends data to an already existing ODT file instead of rewriting the file, it can create file inconsistencies when a single ODT file contains data from two or more simulations. We must define parser behavior so that we can make a decision regarding data conflict.
    
    The parser behavior of the ODT file is as follows:
    1 ('new'): If a single ODT file contains multiple table starts, only select the newest data to be converted as CSV.
    2 ('fail'): If a single ODT file contains two or more table starts, 
    3 ('raw'): Remove multiple table start headers and treat the ODT file as a single, coherent file.
    
    :param odt_input: The path to the ODT file to be converted.
    :param csv_output: The target file path to which the output CSV file will be saved (if not specified, the program will output the CSV file into the ODT file's parent directory. Ignores 'output_suffix' argument.
    :param output_suffix: The suffix file name of the output CSV file. Ignored if 'csv_output' argument is present.
    :param keep_unit: Whether or not to keep the unit name (e.g., second, Joule, etc.) row intact.
    :param parser_behavior: The behavior of the ODT file parser.
    """
    
    # Detecting if input file exists.
    if not os.path.exists(odt_input):
        raise ODTFileNotFoundError(odt_input)
    
    # Determining the output CSV path.
    if csv_output is None and output_suffix is None:
        fo = os.path.splitext(odt_input)[0] + '.csv'
    elif csv_output is None and output_suffix is not None:
        fo = os.path.splitext(odt_input)[0] + str(output_suffix) + '.csv'
    else:
        fo = csv_output
        # Ensuring that the filename always ends in 'csv'.
        if fo[-4:] != '.csv':
            fo += '.csv'
    
    # Reading the input ODT file.
    read_in = open(odt_input, 'r')
    
    # Detecting multiple table starts.
    table_start_count = 0
    for l in read_in:
        
        # Stripping redundant blank chars
        l = l.strip()
        if l.startswith('# Table Start'):
            table_start_count += 1
    
    # Reloading the file input stream.
    read_in.close()
    del read_in
    read_in = open(odt_input, 'r')
    
    # Behavior parameter-specific actions.
    raw_parsing_mode = None
    if str(parser_behavior) == '1' or str(parser_behavior) == 'new':
        raw_parsing_mode = False
    elif str(parser_behavior) == '2' or str(parser_behavior) == 'fail':
        if table_start_count > 1:
            raise MultipleTableStartsError(table_start_count)
        else:
            raw_parsing_mode = False
    elif str(parser_behavior) == '3' or str(parser_behavior) == 'raw':
        raw_parsing_mode = True
    else:
        raise InvalidParserBehaviorError(parser_behavior)
    
    # Do the actual parsing of ODT file.
    if raw_parsing_mode is not None:
        
        # Setting up the writer.
        open(fo, 'w').close()  # --- truncate/overwrite any existing files.
        write_out = open(fo, 'a')
        
        # Reading the input file to convert.
        encountered_table_starts = 0
        for l in read_in:
            
            # Stripping redundant blank chars.
            l = l.strip()
            if l.startswith('# Table Start'):
                encountered_table_starts += 1
            
            # Only do the next steps if we have reached the newest table start.
            if not raw_parsing_mode:
                if encountered_table_starts < table_start_count:
                    continue
            
            # Detecting column header.
            if l[:10] == '# Columns:':
                '''
                l = despacifier(l[10:])
                
                # First step: detecting the existence of the opening '{' delimeter.
                # The variable 'p' is retained for historical reasons.
                # 'ch' stands for 'column header'.
                p = ch = remove_empty(l.split('{'))
                
                # The sanitized column header.
                sanitized_ch = ''
                
                # Next step: after splitting the line by the existence of '{',
                # find the closing '}' delimeter.
                for q in p:
                    if q.__contains__('}'):
                        r = remove_empty(q.split('}'))
                        # Append the first item of r, r[0], which is the only item encapsulated by {...} expression.
                        sanitized_ch += "\"" + r[0] + "\","
                        
                        # r[1], r[2], etc., if they exist, are just regular substring
                        # that do not contain blank spaces.
                        # Do normal splitting-by-whitespace if they exist.
                        if len(r) > 1:
                            for s in r[1].split(' '):
                                sanitized_ch += "\"" + s + "\","
                    
                    # If no '}' delimeter is found, then the substring has no blank space in it.
                    # Do normal splitting-by-whitespace.
                    else:
                        r = remove_empty(q.split(' '))
                        for s in r:
                            sanitized_ch += "\"" + s + "\","
                
                # Trim trailing commas.
                sanitized_ch = sanitized_ch[:-1]'''
                
                # Append this header to the first line of the output file.
                write_out.write(tokenize_header(l[10:]) + '\n')
                continue
            
            # Detecting unit header.
            elif l[:8] == '# Units:':
                if keep_unit:
                    write_out.write(tokenize_header(l[8:]) + '\n')
                    continue
            
            # Detecting general comments.
            elif l[:1] == '#':
                # Pass this one; no need to process this line,
                # which is a comment line.
                continue
            
            # Data rows
            else:
                # Convert this row full of numbers into csv-compatible row.
                new_l = space2comma(l) + '\n'
                write_out.write(new_l)
                continue
        
        # Closing the writer.
        write_out.close()
    
    # Closing the reader.
    read_in.close()
    
    
"""        
        if raw_parsing_mode:
            # Reading the input file to convert.
            for l in read_in:
                
                # Stripping redundant blank chars.
                l = l.strip()
                
                # Detecting column header.
                if l[:10] == '# Columns:':
                    l = despacifier(l[10:])
                    
                    # First step: detecting the existence of the opening '{' delimeter.
                    # The variable 'p' is retained for historical reasons.
                    # 'ch' stands for 'column header'.
                    p = ch = remove_empty(l.split('{'))
                    
                    # The sanitized column header.
                    sanitized_ch = ''
                    
                    # Next step: after splitting the line by the existence of '{',
                    # find the closing '}' delimeter.
                    for q in p:
                        if q.__contains__('}'):
                            r = remove_empty(q.split('}'))
                            # Append the first item of r, r[0], which is the only item encapsulated by {...} expression.
                            sanitized_ch += "\"" + r[0] + "\","
                            
                            # r[1], r[2], etc., if they exist, are just regular substring
                            # that do not contain blank spaces.
                            # Do normal splitting-by-whitespace if they exist.
                            if len(r) > 1:
                                for s in r[1].split(' '):
                                    sanitized_ch += "\"" + s + "\","
                        
                        # If no '}' delimeter is found, then the substring has no blank space in it.
                        # Do normal splitting-by-whitespace.
                        else:
                            r = remove_empty(q.split(' '))
                            for s in r:
                                sanitized_ch += "\"" + s + "\","
                    
                    # Trim trailing commas.
                    sanitized_ch = sanitized_ch[:-1]
                    
                    # Append this header to the first line of the output file.
                    write_out.write(sanitized_ch + '\n')
                    continue
                
                # Detecting general comments.
                elif l[:1] == '#':
                    # Pass this one; no need to process this line,
                    # which is a comment line.
                    continue
                
                # Data rows
                else:
                    # Convert this row full of numbers into csv-compatible row.
                    new_l = space2comma(l) + '\n'
                    write_out.write(new_l)
                    continue
        
        else:  # --- this parser behavior only converts the newest (most below) data into CSV.
            # Reading the input file to convert.
            encountered_table_starts = 0
            for l in read_in:
                
                # Stripping redundant blank chars.
                l = l.strip()
                if l.startswith('# Table Start'):
                    encountered_table_starts += 1
                
                # Only do the next steps if we have reached the newest table start.
                if encountered_table_starts < table_start_count:
                    continue
                
                # Detecting column header.
                if l[:10] == '# Columns:':
                    l = despacifier(l[10:])
                    
                    # First step: detecting the existence of the opening '{' delimeter.
                    # The variable 'p' is retained for historical reasons.
                    # 'ch' stands for 'column header'.
                    p = ch = remove_empty(l.split('{'))
                    
                    # The sanitized column header.
                    sanitized_ch = ''
                    
                    # Next step: after splitting the line by the existence of '{',
                    # find the closing '}' delimeter.
                    for q in p:
                        if q.__contains__('}'):
                            r = remove_empty(q.split('}'))
                            # Append the first item of r, r[0], which is the only item encapsulated by {...} expression.
                            sanitized_ch += "\"" + r[0] + "\","
                            
                            # r[1], r[2], etc., if they exist, are just regular substring
                            # that do not contain blank spaces.
                            # Do normal splitting-by-whitespace if they exist.
                            if len(r) > 1:
                                for s in r[1].split(' '):
                                    sanitized_ch += "\"" + s + "\","
                        
                        # If no '}' delimeter is found, then the substring has no blank space in it.
                        # Do normal splitting-by-whitespace.
                        else:
                            r = remove_empty(q.split(' '))
                            for s in r:
                                sanitized_ch += "\"" + s + "\","
                    
                    # Trim trailing commas.
                    sanitized_ch = sanitized_ch[:-1]
                    
                    # Append this header to the first line of the output file.
                    write_out.write(sanitized_ch + '\n')
                    continue
                
                # Detecting general comments.
                elif l[:1] == '#':
                    # Pass this one; no need to process this line,
                    # which is a comment line.
                    continue
                
                # Data rows
                else:
                    # Convert this row full of numbers into csv-compatible row.
                    new_l = space2comma(l) + '\n'
                    write_out.write(new_l)
                    continue
            
        
        # Closing the writer.
        write_out.close()
    
    # Closing the reader.
    read_in.close()





"""