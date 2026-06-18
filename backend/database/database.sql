/* Inital Database Schema */

/*Table of users */

CREATE TABLE users (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(50),
    phonenum TEXT UNIQUE,
    isLogged BOOLEAN
);
/*Table of governorates (for data analysis for dashboard) */
CREATE TABLE governorates(
ID INT AUTO_INCREMENT PRIMARY KEY,
name varchar(100) UNIQUE
)

-- A user can choose a governorate to start a trip
CREATE TABLE trips(
ID INT AUTO_INCREMENT PRIMARY KEY,
user_id INT REFERENCES users(ID),
governorate_id INT REFERENCES governorates(ID),
start_date DATE NOT NULL,
end_date DATE NOT NULL,
status VARCHAR(50),
notes TEXT
)

-- Table of Subscriptions -- 
CREATE TABLE subscriptions(
    ID INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(40),
	price INT
)

-- User can a subscription and aubscription can belong to different users. (One to many )
ALTER TABLE users
ADD subscription_id INT REFERENCES subscriptions(ID)

-- A table for landmarks -- 
CREATE TABLE landmarks(
 ID INT AUTO_INCREMENT PRIMARY_KEY,
 name text,
 location text,
 opening_hours TIME,
 closing_hours TIME,
 entrance_fee INT,
 photo TEXT
)

-- A trip consists of many landmarks to visit and a landmark can belong to more than one trip.
-- Many to many relationship--
CREATE TABLE trip_landmarks (
  trip_id INT REFERENCES trips(ID),
  landmark_id INT REFERENCES landmarks(ID),
  PRIMARY KEY (trip_id, landmark_id)
);


-- A table of payment methods
-- A user can have multiple payment methods but a payment method can only link to one user 
CREATE TABLE payment_methods(
 ID INT AUTO_INCREMENT PRIMARY_KEY,
 user_id INT REFERENCES users(ID),
 card_holder_name VARCHAR(50),
 card_number varchar(20),
 expiry_month INT,
 expiry_year INT,
 cvv VARCHAR(4),
 card_type VARCHAR(20)
)
