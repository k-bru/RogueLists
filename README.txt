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

#contains templates used by the rogueapp module
RogueLists\capvenv\roguelists\rogueapp\templates\rogueapp

#contains the main codebase for the rogueapp module
RogueLists\capvenv\roguelists\rogueapp

#contains static JS/CSS files used by the application
RogueLists\capvenv\roguelists\static-files

#contains the main project files and configuration settings
RogueLists\capvenv\roguelists

Core Files:
#contains database model and table structures
RogueLists\capvenv\roguelists\rogueapp\models.py

#contains url and slug render logic
RogueLists\capvenv\roguelists\rogueapp\urls.py

#contains logic for views and how pages know what to render
RogueLists\capvenv\roguelists\rogueapp\views.py

#web scraping python script that is run daily on host to update DB games/prices
RogueLists\capvenv\roguelists\update-game-table-pythonanywhere.py

#CSV file that is used to update the database daily (This file also is changed daily based on the scrape results)
RogueLists\capvenv\roguelists\roguelike.csv

Overall, PythonAnywhere has been a reliable and easy-to-use platform for hosting this project and setting up automated tasks.
Using RogueLists
Once the application is up and running, users can navigate to the home page to see a new lists and popular games, and use the search feature to find any other roguelike game. 
From there, they can create an account to start creating and sharing their own lists of games.

To create a new list, users can click the "Create New List" button that appears in game searches and other user lists and enter a name and description for their list. 
They can then search for games in the database and add them to their list using the "Add to List" button.

Users can also view and edit their existing lists from their profile page, as well as view other users' lists, follow other users, and "like" lists.

Admins/Superusers can find that they will have the ability to delete lists from the site itself
Access the Admin area on the footer of each page to make more precise changes to the database, or edit account info such as passwords and emails.

Credits
RogueLists was created by Keegan Brunmeier as a capstone project for Asheville-Buncombe Technical Community College's Software & Web Development program. It makes use of data scraped from Steam using the BeautifulSoup library, as well as Django and several other open-source Python libraries.

License
RogueLists is licensed under the MIT License. Feel free to use this code for personal or commercial projects.