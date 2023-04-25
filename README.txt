Project Title: RogueLists

Project Overview:
RogueLists is a Django-based web application that uses web-scraped data to populate and update a database of game information for games on Steam that fall under the genre of "rogueLike". The purpose of this application is to allow users to create and share lists of their favorite games in this genre. These lists can be used to create personal tier lists, create watch-lists for upcoming games, or simply to browse and discover new games that they may enjoy.

Live Site:
https://www.kbcapstone.com/

Main Directories:
All major files will be found within the "capvenv" (Capstone Virtual Environment) folder and its sub-folders.
RogueLists\capvenv\roguelists\rogueapp\templates\rogueapp - contains templates used by the rogueapp module
RogueLists\capvenv\roguelists\rogueapp - contains the main codebase for the rogueapp module
RogueLists\capvenv\roguelists\static-files - contains static JS/CSS files used by the application
RogueLists\capvenv\roguelists - contains the main project files and configuration settings

Core Files:
RogueLists\capvenv\roguelists\rogueapp\models.py - contains database model and table structures
RogueLists\capvenv\roguelists\rogueapp\urls.py - contains url and slug render logic
RogueLists\capvenv\roguelists\rogueapp\views.py - contains logic for views and how pages know what to render

Local Installation and Setup
To get started locally with RogueLists, you'll need to follow these steps:

Clone the repository from Github.
Install Python 3.x on your system if you haven't already. (RogueLists was created using 3.11.0)
Create a virtual environment and activate it.
Install the required dependencies using pip install -r requirements.txt.
Create a new database for the application.
Run database migrations using python manage.py migrate.
Populate the database with scraped data by running the python manage.py scrape command.
Start the application by running python manage.py runserver

Using RogueLists
Once the application is up and running, users can navigate to the home page to see a list of all the games currently in the database. From there, they can create an account to start creating and sharing their own lists of favorite games.

To create a new list, users can click the "Create New List" button that appears in game searches and other user lists and enter a name and description for their list. They can then search for games in the database and add them to their list using the "Add to List" button.

Users can also view and edit their existing lists from their profile page, as well as view other users' lists and add them to their own watch-lists.

Admins/Superusers can find that they will have the ability to delete lists from the site itself, and also access the Admin area on the footer of each page, which gives them the ability to make more precise changes, or edit account info such as passwords and emails.

Contributing
If you'd like to contribute to RogueLists, we welcome pull requests and bug reports on Github. Before submitting a pull request, please make sure to run the test suite using python manage.py test to ensure that your changes don't break existing functionality.

Credits
RogueLists was created by Keegan Brunmeier as a capstone project for Asheville-Buncombe Technical Community College's Software & Web Development program. It makes use of data scraped from Steam using the BeautifulSoup library, as well as Django and several other open-source Python libraries.

License
RogueLists is licensed under the MIT License. Feel free to use this code for personal or commercial projects.