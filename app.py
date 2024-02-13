from flask import Flask, request, send_from_directory, Response
from werkzeug.exceptions import abort
from werkzeug.middleware.proxy_fix import ProxyFix
from typing import List

__author__ = "Michael Pogrebinsky - www.topdeveloperacademy.com"


from data.book import Book
from data.database import Database
from data.request_validator import RequestValidator, CreditCardValidationException, InvalidBillingInfo

app = Flask(__name__, static_url_path='')

# The lab is behind a http proxy, so it's not aware of the fact that it should use https.
# We use ProxyFix to enable it: https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#proxy-setups
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Used for any other security related needs by extensions or application, i.e. csrf token
app.config['SECRET_KEY'] = 'mysecretkey'

# Required for cookies set by Flask to work in the preview window that's integrated in the lab IDE
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

# Required to render urls with https when not in a request context. Urls within Udemy labs must use https
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Creating application databases and business logic
BOOKS_DIRECTORY = "resources/books"
checkout_request_validator = RequestValidator()
database = Database()

"""Complete your code here"""


@app.get('/')
def index():
    return app.send_static_file('index.html')



def aggregate_books(books: List[Book]) -> dict:
    """
    Creates a dictionary object that maps from 'books' to a list of book objects
    Example:
        {"books: [{"id": 123,
                    "name": "Course Name",
                    "description": "Course Description",
                    "image_file_name": "image.png",
                    "price_usd": 19.9,
                    "topic": "education",
                    "average_rating" : 4.5}]
        }
    """

    return {"books": [book.__dict__ for book in books]}
