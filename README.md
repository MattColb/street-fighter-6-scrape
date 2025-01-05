## How to Use:

- Install the requirements using `pip install -r requirements.txt`
- Create a .env file containing the file that you want your database to be in and the file that your cookie is in
    - i.e. DBNAME = "test.db" 
    - COOKIE_NAME="cookies-streetfighter-com.txt"
- Download your cookie from https://www.streetfighter.com/6/buckler/ in the Netscape format into the txt file that corresponds to your .env file.
- Get the user code of the user whose matches you want to scrape.
- Run `python main.py -i {uid}` where uid is the user code of the user to scrape. 
