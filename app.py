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


@app.get('/categories/')
def categories():
    return database.get_all_supported_categories()


@app.get('/books/')
def get_books():
    category = request.args.get('category')
    if category is not None:
        books = database.get_books_by_category(category)
    else:
        books = database.get_all_books()
    return aggregate_books(books)


@app.get('/trending/<int:max_number_of_books>')
def trending_books(max_number_of_books: int):
    books = database.get_trending_books(max_number_of_books)
    return aggregate_books(books)


@app.post('/checkout/')
def checkout():
    data = request.get_json()
    checkout_request_validator.validate_billing_info(first_name=data['first_name'], last_name=data['last_name'],
                                                     billing_address=data['billing_address'])
    checkout_request_validator.validate_credit_card(data['credit_card'])

    database.purchase_books(**data)
    return {"message": "Checkout completed successfully"}


@app.get('/book_download')
def book_download():
    book_id = request.args.get('book_id')
    filename = database.get_book_file_name(int(book_id))
    return send_from_directory(directory=BOOKS_DIRECTORY, path=filename, as_attachment=True)


@app.errorhandler(InvalidBillingInfo)
def handle_invalid_billing_info_exception(e):
    return Response(str(e), status=400, mimetype="text/plain")


@app.errorhandler(CreditCardValidationException)
def handle_credit_card_validation_exception(e):
    app.logger.warning(e)
    return Response(str(e), status=402, mimetype="text/plain")

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
