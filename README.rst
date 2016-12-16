================
Movies Navigator
================

A tool that makes use of the structure build by the movies_organizer project in order to provide a fast easy way to manage and navigate your movies.

Description
===========

Movies Navigator is meant to be used on top of the project movies_organizer.
It uses the organized structure by movies_organizer to provide a CLI based interface that helps users manage their movies directory.
The CLI interface allows users to filter their movies by: movie type (seen, watchlist), minimum rating, maximum rating and genres.
Users also have the ability to move their movies from seen directory to watchlist directory (and vice-versa) with a simple command.
For the structure of these commands and other ones please refer to the usage section.

Installation
============

Installing the application is very simple.
To do so please follow the directions below:

1. Install Python https://www.python.org/downloads/ and add it to your path
2. Install Git https://git-scm.com/downloads and add it yo your path
3. Check if you have pip (python package manager) installed by running `pip --version`

 a. If not download the file [get-pip.py] (https://bootstrap.pypa.io/get-pip.py/), being careful to save it as a .py file rather than .txt
 b. Run it from the command prompt: python get-pip.py

4. Run the command `pip install git+https://github.com/alimasri/movies_navigator`

This command will download and install the project with the required dependencies.

Usage
=====



Note
====

This project has been set up using PyScaffold 2.5.7. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.
