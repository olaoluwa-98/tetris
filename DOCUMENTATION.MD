# Tetris Documentation for Admin / Developer

## Install the following

* python 3.6
* mysql server (comes with XAMPP)
* pip (comes with python 3.6) and virtualenv


## Setup

* open terminal
* clone the project i.e `git clone https://github.com/olaoluwa-98/tetris.git`
* install virtualenv with `pip install virtualenv`
* navigate into tetris folder in your terminal i.e `cd tetris`
* create a virtual environment `virtualenv venv`
* activate the virtual environment `venv\Scripts\activate` for windows cmd or `source venv\bin\activate` for bash
* install the project requirements `pip install -r requirements.txt`
* make migrations `python manage.py makemigrations store`

* configure your database in the settings.py in the tetris folder
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<database_name>',
        'USER': '<database_user>',
        'PASSWORD': '<database_passowrd>',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}
```

** NB: make sure your mysql server is running
* run the migrations `python manage.py migrate`

## Starting the project

You may need to create a django superuser so you can easily navigate the database, use this command to create a superuser
`python manage.py createsuperuser` and enter the required details.

run `python manage.py runserver` to start the project


## Information about how the site operates

### For a nomal user (a customer)

* He creates an account through `/register`.
* He can see popular products and brands in `/`
* He cart add to or remove from cart and wish list any where products appear
* He can view his wish list `/wish-list`
* He can view his cart `/cart`
* He can view his orders `/orders`
* He can view his ordered items by order `/order/reference`
* When he orders, he can cancel his order

### For a staff user (an administrator)

* He gets his account by being a superuser `python manage.py createsuperuser`
* He has all administrative privileges
* He however should be careful in using them
* navigating here takes him to the admin `/staff`
* He can view anything in the database.


### The following are the things the administrator should do

* add or edit the following:
	* Products,
	* Images of Products,
	* Categories of Products,
	* Brands of Products,
* NB: He should not delete any of this because, it'll affect important things like orders, cart items, wishlist, ordered items etc.

* When customers place orders on products:
	* he/ she is to monitor the order and orderitem models to see new ones
	* the pending orders should be changed to processing if the product is being packaged,
	* the processing orders should `not` be changed to delivered, only the customers should do that
	* pending orders can be cancelled if the products are not available any more, notify the customer