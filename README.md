# Udacity Full Stack Nanodegree Project 4: Item Catalog

## Healthy Direction

- Authentication and Authorization
- How to plan and build an API
- Using python Flask to create a server for **serving** up information for the consumption of users on the website, or
 individuals wishing to consume our API
- Understanding how to secure access and ensure proper API and information hygiene
- etc.

My server will render and support a items in the nature of ways to be healthy. I will focus on listing classes available
and also shops that sell healthy products. Set up into the following categories, Nature, Nurture and Nutrition.

#### Nature
Will be classes and individuals who give information and workshops on how to access the good things from nature through
forage, natural medicines and wilderness awareness and survival skills.

#### Nuture
Are classes, etc aimed at learning something that will foster your natural health and well being.

#### Nutrition
As you may have guessed, is about places and shops that you can source healthy foods and goods to care for what and how
you put into/onto your body.



## Required Setup:

..- Download and install Virtual Box (https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and Vagrant (https://www.vagrantup.com/downloads.html)

..- Once you have both of those setup in your system, go you can fork and/or clone the Full Stack Nanodegree course's VM setup from here (https://github.com/udacity/fullstack-nanodegree-vm).

Navigate into the cloned repository and then into the subdirectory 'vagrant'. Inside this directory, run the command 'vagrant up'. This may take a while to execute as it is downloading and installing a linux operating system.

Once it has completed, clone this project into the '/vagrant' directory, this will now be available to run within the vagrant virtual machine that is currently running.

Now use the command 'vagrant ssh' to move into the newly created Virtual Machine (VM), once inside, run the commands 'python models.py' & 'python database_setup.py' (which will create the appropriate database and seed it with the catalogue data).

Now you should be setup and ready to go. To run this Flask server please use the command 'python views.py', enter the port you would like to use (or leave it blank for http://localhost:5000/) and navigate to that address in your favourite browser.

If everything has been successful, you should be presented with my project.

## Exploring the project:

The website should show you all the details of the categories and their items, however it isn't until you
sign in that you can see the functionality for Adding, Editing or Deleting items. To address this though
you have two options:
1) Sign in with Google and add a few items of your own
2) Join up and sign in, then add some of your own items, or;
3) Login with the Username: Ben and Password: password

With the final option you will be able to perform add/edit/delete functionality for all objects currently being shown.

### API Endpoints:

You can explore the api without authorization, however there is no functionality for editing information through the supplied endpoints at present.

1) /api/categories/ <br>
Shows all the categories and all the items <br>
2) /api/categories/<category_name>/items <br>
Provides all the items of a given category, the name is supplied as a string (Nature, Nurture or Nutrition) <br>
3) /api/categories/<category_name>/items/item_id/ <br>
Provides only the single item from the selected category. <br>

If you find any bugs or have any comments, please send them to myself here at Github, or to my email address of
benrconway84@gmail.com

Thank you and I hope you enjoy my first foray into Authentication and Authorization.
