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

class Odt2CsvException(Exception):
    """ The super-class for all exceptions related to odt2csv. This exception should not be called directly. """

class InvalidParserBehaviorError(Odt2CsvException):
    """ Error raised when the parser behavior argument passed to the parser function is not defined. """

    def __init__(self, arg: str = ''):
        self.arg = arg

    def __repr__(self):
        return f'Cannot find parser behavior: {self.arg}. You must specify either "new", "fail", or "raw" (see the documentation for further details.)'
    
    __str__ = __repr__

class MultipleTableStartsError(Odt2CsvException):
    """ Error raised when the parser detects multiple table starts in the ODT file. """

    def __init__(self, arg: str = ''):
        self.arg = arg

    def __repr__(self):
        return f'Cannot convert ODT file that has multiple ({self.arg}) table starts.'
    
    __str__ = __repr__

class ODTFileNotFoundError(Odt2CsvException):
    """ Error raised when the input ODT file is not found. """

    def __init__(self, arg: str = ''):
        self.arg = arg

    def __repr__(self):
        return f'Cannot find the input ODT file: {self.arg}. You must specify a valid file path.'
    
    __str__ = __repr__
