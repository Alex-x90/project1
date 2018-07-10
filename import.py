import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    # Open a file using Python's CSV reader.
    f = open("zips.csv")
    reader = csv.reader(f)

    # Iterate over the rows of the opened CSV file.
    for row in reader:

        # Execute database queries, one per row; then print out confirmation.
        db.execute("INSERT INTO weather (zipcode, city, state,lattitude,longitude,population) VALUES (:a, :b, :c, :d, :e, :f)",
                    {"a": row[0], "b": row[1], "c": row[2], "d": row[3], "e":row[4], "f": row[5]})

    # Technically this is when all of the queries we've made happen!
    db.commit()

if __name__ == "__main__":
    main()
