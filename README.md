# Med Online API

## Installation
To install the necessary dependencies, make sure you have `pip` and a virtual environment set up. Then, run the following command: pip install `dependence`

## Dependencies
The following libraries are required for this project:

* mysqlclient: MySQL connector for Django -> `pip install mysqlclient`
* pymysql: Pure Python MySQL client library -> `pip install pymysql`
* django-autoslug: Automatically generates unique slugs based on a model field -> `pip install django-autoslug`.
* pillow: Library for image processing in Python -> `pip install Pillow`

## Database Setup
This project uses MySQL as the database. Make sure you have MySQL installed and running. Then, follow these steps:

1. Create the database in MySQL: `CREATE DATABASE med_online;`

2. Run database migrations:
* `python manage.py makemigrations users`
* `python manage.py migrate`

