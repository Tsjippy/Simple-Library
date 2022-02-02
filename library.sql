DROP TABLE IF EXISTS "Users";
DROP TABLE IF EXISTS "Items";
DROP TABLE IF EXISTS "Settings";

CREATE TABLE "Users"(
	"id" 			INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"display_name" 		TEXT DEFAULT 'New User',
	"first_name" 		TEXT,
	"last_name" 		TEXT,
	"birthday"	 		TEXT,
	"barcode" 			TEXT,
	"picture"		 	TEXT,
	"max_items"			INTEGER,
	"loan_period"		INTEGER	
);

CREATE TABLE "Items"(
	"id" 				INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"title" 			TEXT DEFAULT 'New Item',
	"item_type"			TEXT DEFAULT 'Book',
	"author" 			TEXT,
	"isbn" 				INTEGER,
	"barcode" 			TEXT,
	"picture"		 	TEXT,
	"linked_to" 		INTEGER,
	"loaned_since"		INTEGER,
	"due_date"			INTEGER
);

CREATE TABLE "Settings"(
	"id" 				INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"key"				TEXT,
	"value"				TEXT
);