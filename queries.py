INSERT_NEW_USER = "INSERT INTO users (username, hash) VALUES(?, ?)"
SELECT_CURRENT_USER = "SELECT * FROM users WHERE username = ?"
GET_READING_LIST = "SELECT * FROM books JOIN to_read ON books.id = to_read.book_id WHERE to_read.user_id = ?"
GET_HAVEREAD_LIST = "SELECT * FROM books JOIN books_read ON books.id = books_read.book_id WHERE books_read.user_id = ? ORDER BY time DESC LIMIT 5"
GET_CURRENT_LIST = "SELECT books.author AS author, books.title AS title, currently_reading.book_id AS book_id, currently_reading.user_id FROM books JOIN currently_reading ON books.id = currently_reading.book_id WHERE currently_reading.user_id = ?"
ADDTO_READING_LIST = "INSERT INTO to_read (user_id, book_id) VALUES (?, ?)"
SEARCH_DB = "SELECT * FROM books WHERE author LIKE ? OR title LIKE ?"
DEL_FROM_RL = "DELETE FROM to_read WHERE user_id = ? AND book_id = ?"
GET_RL_BOOKID = "SELECT book_id FROM to_read WHERE user_id = ?"
GET_CLIST = "SELECT book_id, user_id FROM currently_reading WHERE user_id = ?"
DEL_FROM_CL = "DELETE FROM currently_reading WHERE user_id = ? AND book_id = ?"
HAVE_READ = "INSERT INTO books_read (user_id, book_id) VALUES (?, ?)"
FIND_BOOK = "SELECT * FROM books WHERE id = ?"
GET_REVIEWS = "SELECT user_id, book_id, content, time, author, title, spoiler, rating FROM reviews JOIN books ON reviews.book_id = books.id where books.id = ? ORDER BY time DESC"
BOOKS_BY_AUTHOR = "SELECT * FROM books WHERE author = ?"
FIND_AUTHOR = "SELECT author FROM books WHERE id = ?"
MY_REVIEWS = "SELECT * FROM reviews WHERE user_id = ? ORDER BY time DESC"
GET_TITLE = "SELECT title FROM books WHERE id = ?"
TOP_25 = "SELECT * FROM books ORDER BY avg_rating DESC LIMIT 25"
GET_HAVEREAD_NOLIMIT = "SELECT * FROM books JOIN books_read ON books.id = books_read.book_id WHERE books_read.user_id = ? ORDER BY time DESC"
ADD_REVIEW = "INSERT INTO reviews (content, spoiler, book_id, user_id) VALUES(?, ?, ?, ?)"
LATEST_REVIEWS = "SELECT * FROM reviews ORDER BY time DESC LIMIT 10"
GET_USERNAME = "SELECT username FROM users WHERE id = ?"
ADDTO_CLIST = "INSERT INTO currently_reading (user_id, book_id) VALUES(?, ?)"
TOP_5 = "SELECT * FROM books ORDER BY avg_rating DESC LIMIT 5"
NEWEST_REVIEW = "SELECT user_id, book_id, content, time, author, title, spoiler, rating FROM reviews JOIN books ON reviews.book_id = books.id ORDER BY time DESC LIMIT 1"
INCREMENT_REVIEWS = "UPDATE books SET num_of_reviews = num_of_reviews + 1 WHERE id = ?"
INCREMENT_RATINGS = "UPDATE books SET num_of_ratings = num_of_ratings + 1 WHERE id = ?"
PICK_QUOTE = "SELECT * FROM quotes WHERE id = ?"
SELECT_SIMILAR = "SELECT title, author FROM books WHERE title LIKE ?"
ADD_BOOK = "INSERT INTO books (author, title, avg_rating, num_of_ratings) VALUES (?, ?, 0, 0)"
NEW_BOOK = "SELECT * FROM books WHERE author = ? AND title = ?"
NEW_AVERAGE = "UPDATE books SET avg_rating = ROUND((num_of_ratings * avg_rating + ?) / (num_of_ratings + 1), 2) WHERE id = ?"
REVIEW_AND_RATING = "INSERT INTO reviews (content, rating, spoiler, book_id, user_id) VALUES(?, ?, ?, ?, ?)"
THIS_REVIEW = "SELECT id FROM reviews ORDER BY time DESC LIMIT 1"

