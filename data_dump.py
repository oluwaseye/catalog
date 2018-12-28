from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, User

engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False}, echo=True)
# Bind the engine to the metadata of the Base class
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Data dump for default user
default_user = User(name="Oluwaseye", email="seyz4all@gmail.com",
                    picture='https://goo.gl/Xsv6AR')
session.add(default_user)
session.commit()
print("Catalog Categories added successfully!")

# Data Dump for default Category items
# Store the Category object rows in an array
category_array = [
    Category(name="Coupe", picture="https://goo.gl/bnjtuZ", user_id=1),
    Category(name="Sedan", picture="https://goo.gl/HmwcfK", user_id=1),
    Category(name="Truck", picture="https://goo.gl/g8YFqy", user_id=1),
    Category(name="Crossover", picture="https://goo.gl/MDszth", user_id=1),
    Category(name="SUV", picture="https://goo.gl/MMpXFq", user_id=1)
]
for i in range(len(category_array)):
    session.add(category_array[i])
    session.commit()
print("Catalog Categories added successfully!")

# Data Dump for default Items
# Store the Item object rows in an array
items_array = [
    Items(name="2018 Honda Civic LX",
          image="https://goo.gl/XdU2An",
          price="25000",
          description="Excellent fuel economy and performance engines.",
          category_id=1,
          user_id=1),

    Items(name="Ford Explorer",
          image="https://goo.gl/61Trmf",
          price="40000",
          description="Some excellent standard features with a V6 engine.",
          category_id=5,
          user_id=1),

    Items(name="Jeep Cherokee",
          image="https://www.carmax.com/cars/jeep/cherokee",
          price="35000",
          description="If you want the ruggedness of the Grand Cherokee. ",
          category_id=5,
          user_id=1),

    Items(name="2019 Toyota Corolla",
          image="https://goo.gl/iQk3DL",
          price="23000",
          description="Expect to see the 6.1-inch multimedia touchscreen.",
          category_id=2,
          user_id=1),

    Items(name="2018 Jeep Compass",
          image="https://goo.gl/Nu2vbh",
          price="34000",
          description="Compact SUV with off-road capability.",
          category_id=4,
          user_id=1),

    Items(name="2018 Chevrolet Silverado 1500",
          image="https://goo.gl/J3cqgU",
          price="29000",
          description="Rearview camera and 7-inch touchscreen now standard.",
          category_id=3,
          user_id=1)
]
for i in range(len(items_array)):
    session.add(items_array[i])
    session.commit()
print("Catalog Items added successfully!")
