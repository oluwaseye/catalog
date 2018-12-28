
# Item Catalog Application - (Car Talog)

## Project Overview

This project uses Python Flask Framework to deploy a RESTful web application that uses OAuth authentication and CRUD based data manipulation. This code will run on a local server.

## Setup

**1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/)**

**2. Google Oauth Authentication**

 - Go to https://console.developers.google.com/project and login with
   Google.
 - Create a new project.
 - Select "API's and Auth -> Credentials -> Create a new OAuth client
   ID" from the project menu.
 - Select Web Application.
 - On the consent screen, type in a product name and save.
 - Click download JSON and save it into the root director of this
   project.
 - Rename the JSON file "client_secrets.json"
 - 
### Run the Virtual Machine
 - Using the terminal, change directory to project directory, then type
   `vagrant up` to launch your virtual machine.
   When the VM is up and running, type in `vagrant ssh`
   Change the directory `cd /vagrant`, this gets you to the shared folder within the VM and host machine.

### Run the Project
First time running the project, you'll have to dump the default data first by typing `python data_dump.py` in the Linux Shell prompt
Finally, you should type in `python application.py` to run the application, then you can access the application in your browser at `http://localhost:8000`

## JSON Endpoints

The application has JSON endpoints for users to access the database info for development and testing purposes. These endpoints are as follows:

 1. `localhost:8000/categories/items/json` will display all items from the catalog.
 2.  `localhost:8000/categories/Sedan/items/json` will display all items in a category in JSON, where **Sedan** is the category.

    {
      "Items": [
        {
          "category": "Sedan", 
          "description": "Expect to see the 6.1-inch multimedia touchscreen.", 
          "id": 4, 
          "image": "https://goo.gl/iQk3DL", 
          "name": "2019 Toyota Corolla", 
          "price": "23000"
        }
      ]
    }

 
 3. `http://localhost:8000/categories/Sedan/2019%20Toyota%20Corolla/json` will like the web application give details on aspecific item in
    JSON.

## Troubleshooting
In some computers running Windows for OS the command `vagrant ssh` may not work correctly. For those systems please try `winpty vagrant ssh`