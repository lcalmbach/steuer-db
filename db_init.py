
import os
import pyodbc
srv = 'LIESTAL\LIESTAL'
db_name = 'globomantics'

def get_connection():
    """Generates the connection string using the specified server and database name"""

    connection_string = f"Driver={{SQL Server}};Server={srv};Database={db_name};Trusted_Connection=yes;Timeout=600"
    return pyodbc.connect(connection_string)


conn = get_connection()
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS items")
c.execute("DROP TABLE IF EXISTS categories")
c.execute("DROP TABLE IF EXISTS subcategories")
c.execute("DROP TABLE IF EXISTS comments")

c.execute("""CREATE TABLE categories(
                    id              INT IDENTITY(1,1) NOT NULL,
                    name            varchar(50) NOT NULL,
                    CONSTRAINT PK_categories PRIMARY KEY CLUSTERED (id)
)""")

c.execute("""CREATE TABLE subcategories(
                    id              INT IDENTITY(1,1) NOT NULL,
                    name            varchar(50) NOT NULL,
                    category_id     INT NOT NULL,
                    CONSTRAINT PK_subcategories PRIMARY KEY CLUSTERED (id)
)""")

c.execute("""CREATE TABLE items(
                    id              INT IDENTITY(1,1) NOT NULL,
                    title           varchar(50) NOT NULL,
                    description     varchar(50) NOT NULL,
                    price           REAL NOT NULL,
                    image           varchar(50) NOT NULL,
                    category_id     INT NOT NULL,
                    subcategory_id  INT NOT NULL,
                    CONSTRAINT PK_items PRIMARY KEY CLUSTERED (id)
)""")

c.execute("""CREATE TABLE comments(
                    id              INT IDENTITY(1,1) NOT NULL,
                    content         varchar(50),
                    item_id         INT,
                    CONSTRAINT PK_comments PRIMARY KEY CLUSTERED (id)
)""")

categories = [
    ("Food",),
    ("Technology",),
    ("Books",)
]
c.executemany("INSERT INTO categories (name) VALUES (?)", categories)

subcategories = [
    ("Fruit", 1),
    ("Dairy product", 1),
    ("Cassette", 2),
    ("Phone", 2),
    ("TV", 2),
    ("Historical fiction", 3),
    ("Science fiction", 3)
]
c.executemany("INSERT INTO subcategories (name, category_id) VALUES (?,?)", subcategories)

items = [
    ("Old Tape", "You can record anything.", 2.0, "", 2, 3),
    ("Bananas", "1kg of fresh bananas.", 1.0, "", 1, 1),
    ("Vintage TV", "In color!", 150.0, "", 2, 5),
    ("Cow Milk", "From the best farms.", 5.0, "", 1, 2)
]
c.executemany("INSERT INTO items (title, description, price, image, category_id, subcategory_id) VALUES (?,?,?,?,?,?)", items)

comments = [
    ("This item is great!", 1),
    ("Whats up?", 2),
    ("Spam spam", 3)
]
c.executemany("INSERT INTO comments (content, item_id) VALUES (?,?)", comments)

conn.commit()
conn.close()

print("Database is created and initialized.")
print("You can see the tables with the show_tables.py script.")
