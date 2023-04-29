Project Title: RogueLists

Project Overview:
RogueLists is a Django-based web application that uses web-scraped data to populate and update a database of game information for games on Steam that fall under the genre of "roguelike". 
The purpose of this application is to allow users to create and share lists of their favorite games in this genre. These lists can be used to create personal tier lists, create watch-lists for upcoming games, or simply to browse and discover new games that they may enjoy.

PythonAnywhere is used to host and run the project, and automated jobs are set up to update the database daily with new game information such as pricing, release dates, and genre tags.
These updates ensure that the site has the most current and accurate information available for users.
The database is updated automatically without any intervention needed from the developer, thanks to PythonAnywhere's scheduling feature.

Live Site:
https://www.kbcapstone.com/

Main Directories:
All major files will be found within the "capvenv" (Capstone Virtual Environment) folder and its sub-folders.

#contains templates used by the rogueapp module, this directory is where you will find most HTML pages 
RogueLists\capvenv\roguelists\rogueapp\templates\rogueapp

#contains the main codebase for the rogueapp module
RogueLists\capvenv\roguelists\rogueapp

#contains static JS/Image/CSS files used by the application
RogueLists\capvenv\roguelists\static-files

#contains the main project files and configuration settings
RogueLists\capvenv\roguelists

Core Files:
#contains database model and table structures (See note below this section about SQL scripts)
RogueLists\capvenv\roguelists\rogueapp\models.py

#contains url and slug render logic
RogueLists\capvenv\roguelists\rogueapp\urls.py

#contains logic for views and how pages know what to render
RogueLists\capvenv\roguelists\rogueapp\views.py

#web scraping python script that is run daily on host to update DB games/prices
RogueLists\capvenv\roguelists\update-game-table-pythonanywhere.py

#CSV file that is used to update the database daily (The contents of this file are also modified daily based on the scrape results)
RogueLists\capvenv\roguelists\roguelike.csv

Note about SQL in relation to this project:
Django uses an Object-Relational Mapping (ORM) framework, which is a technique of mapping between the relational database and the object-oriented programming language. Django provides a high-level abstraction layer that allows developers to work with databases using Python classes and methods instead of writing SQL scripts.

The models.py file in a Django app contains Python classes that represent database tables. These classes inherit from the django.db.models.Model class and define attributes that map to fields in the database table. The ORM framework takes care of translating these Python classes and their attributes into SQL queries and executing them against the database.

When Django is set up, it creates tables in the database for each of the defined models. This is done by running a series of migrations, which are scripts that Django generates based on changes to the models. These migrations are stored in a special folder within the app called migrations.

Therefore, Django does not require a typical SQL script file to initiate a database because the models and the ORM handle the creation and management of database tables. The models.py file is similar to a SQL script file in that it defines the structure of the database, but it is written in Python and uses Django's ORM to interact with the database. You can find the models.py file for a Django app in the app folder at capvenv\roguelists\rogueapp\models.py.

Using RogueLists
Once the application is up and running, users can navigate to the home page to see a new lists and popular games, and use the search feature to find any other roguelike game. 
From there, they can create an account to start creating and sharing their own lists of games.

To create a new list, users can click the "Create New List" button that appears in game searches and other user lists and enter a name and description for their list. 
They can then search for games in the database and add them to their list using the "Add to List" button.

Users can also view and edit their existing lists from their profile page, as well as view other users' lists, follow other users, and "like" lists.

Admins/Superusers can find that they will have the ability to delete lists from the site itself
Access the Admin area on the footer of each page to make more precise changes to the database, or edit account info such as passwords, emails, and admin/staff status.

Credits
RogueLists was created by Keegan Brunmeier as a capstone project for Asheville-Buncombe Technical Community College's Software & Web Development program. It makes use of data scraped from Steam using the BeautifulSoup library, as well as Django and several other open-source Python libraries.

License
RogueLists is licensed under the MIT License. Feel free to use this code for personal or commercial projects.