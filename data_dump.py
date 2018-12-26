from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, User

engine = create_engine('sqlite:///itemcatalog.db', connect_args={'check_same_thread': False}, echo=True)
# Bind the engine to the metadata of the Base class
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Data dump for default user
default_user = User(name="Oluwaseye", email="seyz4all@gmail.com", picture='http://cdn.onlinewebfonts.com/svg/download_542975.png')
session.add(default_user)
session.commit()
print("Catalog Categories added successfully!")

# Data Dump for default Category items
# Store the Category object rows in an array
category_array = [
    Category(name="Coupe", picture="https://images.honestjohn.co.uk/imagecache/file/width/640/media/12626210/toyota-gt86-7.jpg", user_id=1)
    , Category(name="Sedan", picture="https://s.aolcdn.com/dims-global/dims3/GLOB/legacy_thumbnail/788x525/quality/85/https://s.aolcdn.com/commerce/autodata/images/USC80MAC171A121001.jpg", user_id=1)
    , Category(name="Truck", picture="https://www.longhornrentals.com/wp-content/uploads/2015/05/ford-truck-rental.jpg", user_id=1)
    , Category(name="Crossover", picture="https://www.carmax.com/~/media/images/carmax/com/Articles/best-crossover-suvs/10-nissan-murano-new.jpg?la=en&hash=FDA673B6A8F0390C9FBA8A6C1EC75F8A85EEAB87", user_id=1)
    ,Category(name="SUV", picture="https://www.carmax.com/~/media/images/carmax/com/Articles/best-suvs/09-nissan-rogue-new.jpg?la=en&hash=8308EFE4B6C2E9FDD085552489809F09FAE28ABC", user_id=1)
]
for i in range(len(category_array)):
    session.add(category_array[i])
    session.commit() 
print("Catalog Categories added successfully!")

# Data Dump for default Items
# Store the Item object rows in an array
items_array = [
    Items(name="2018 Honda Civic LX",
              image="https://img2.carmax.com/img/vehicles/16800740/1/v-0x8d66010a27ae02/1920.jpg",
              price="25000",
              description="Excellent fuel economy and performance from turbocharged engines.",
              category_id=1,
              user_id=1),

    Items(name="Ford Explorer",
              image="https://www.carmax.com/~/media/images/carmax/com/Articles/best-suvs/05-ford-explorer-new.jpg?la=en&hash=B9F45D4E124EC27C4C0F2D90B724BCE580F2DB57",
              price="40000",
              description="Some excellent standard features include a rearview camera, Ford Sync, and a 3.5L V6 engine.",
              category_id=5,
              user_id=1),

    Items(name="Jeep Cherokee",
              image="https://www.carmax.com/cars/jeep/cherokee",
              price="35000",
              description="If you want the ruggedness of the Grand Cherokee in a smaller package, the Jeep Cherokee is another great option. ",
              category_id=5,
              user_id=1),

    Items(name="2019 Toyota Corolla",
              image="https://img2.carmax.com/img/vehicles/16819266/1/v-0x8d665e98bb7fc9/1920.jpg",
              price="23000",
              description="Expect to see the standard 6.1-inch multimedia touchscreen return in 2019, including the optional 7.0-inch touchscreen with SiriusXM satellite radio and its available navigation system. ",
              category_id=2,
              user_id=1),

    Items(name="2018 Jeep Compass",
              image="https://img2.carmax.com/img/vehicles/16758011/1/v-0x8d654aaf39a023/1920.jpg",
              price="34000",
              description="Compact SUV with off-road capability defines the 2018 Jeep Compass. Explore technology, capability, design & other features of the trail rated 2018 Compass.",
              category_id=4,
              user_id=1),

    Items(name="2018 Chevrolet Silverado 1500",
              image="https://img2.carmax.com/img/vehicles/16837768/1/v-0x8d65fdb403b26f/1920.jpg",
              price="29000",
              description="Rearview camera and 7-inch touchscreen now standard across the board",
              category_id=3,
              user_id=1)
]
for i in range(len(items_array)):
    session.add(items_array[i])
    session.commit() 
print("Catalog Items added successfully!")