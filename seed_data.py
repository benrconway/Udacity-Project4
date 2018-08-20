# Here will go all the seed data to give the website something to display.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Item, User

engine = create_engine('sqlite:///itemcatalogue.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(name="Ben", email="email@email.com", password=self.hash_password("password"))


category = Category(name="Nature", description="A list of courses and information relating to being out and at one with our natural surroundings", user=user)

item = Item(name="Monica Wilde", description="A blog on wild food, wild medicine, wild living and the old ways of doing and being as well as a place to learn by being in nature",
                     locatiion="Scotland", url="http://monicawilde.com/", user=user, category=category)
session.add(item)
session.commit()

item = Item(name="Back Country Survival", description="Outdoor survival courses available in Scotland.",
                     locatiion="Scotland", url="https://www.backcountrysurvival.co.uk/", user=user, category=category)

session.add(item)
session.commit()

item = Item(name="Woodland Way", description="Outdoor training and survival courses available in the UK.",
                     locatiion="UK", url="https://www.woodland-ways.co.uk/", user=user, category=category)

session.add(item)
session.commit()

item = Item(name="Britain's Best Forsts and Woodlands", description="A list of some beautiful forests and woodlands in the UK.",
                     locatiion="UK", url="http://www.countryfile.com/countryside/britains-best-forests-and-woodland", user=user, category=category)

session.add(item)
session.commit()

item = Item(name="Original Outdoors", description="An expansive list of courses and guided walks available in North Wales",
                     locatiion="North Wales", url="https://originaloutdoors.co.uk/all-courses/uk-foraging-wild-food-course/", user=user, category=category)

session.add(item)
session.commit()

session.add(category)
session.commit()

category = Category(name="Nurture", description="A list of styles and practices to nurture your own inner understanding of nature of self and the world", user=user)


item = Item(name="Wudang Daoism", description="The web portal to classes and information about Wudang Kungfu and Daoism from Jeff Reid.",
                     locatiion="Unknown", url="https://www.wudangdaoism.com/", user=user, category=category)

session.add(item)
session.commit()

item = Item(name="American Wudang", description="The web portal to classes in Taiji and Wudang Kungfu from Jake Pinnick.",
                     locatiion="America", url="https://www.americanwudang.com/", user=user, category=category)
session.add(item)
session.commit()

item = Item(name="Bai He Alba", description="The web presence of the White Crane School of Martial Arts in Scotland.",
                     locatiion="Scotland", url="http://www.whitecranescotland.com/", user=user, category=category)
session.add(item)
session.commit()

item = Item(name="Wudang Australis", description="The portal to information about classes being run by Benjamin Conway",
                     locatiion="Scotland", url="https://www.wudangaus.com/", user=user, category=category)
session.add(item)
session.commit()

session.add(category)
session.commit()

category = Category(name="Nutrition", description="Places to get good food, or learn how to collect your own.", user=user)

item = Item(name="Real Foods", description="Two stores in Edinburgh that offer an exceptional range of organic products to support everyday living",
            location="Edinburgh, Scotland", url="https://www.realfoods.co.uk/", user=user, category=category)
session.add(item)
session.commit()

item = Item(name="Healthy Supplies", description="An online shop for buying healthy and/or organic products in bulk for cheaper than store prices.",
            location="Online", url="https://www.healthysupplies.co.uk/", user=user, category=category)

session.add(item)
session.commit()

item = Item(name="Real Foods", description="Two stores in Edinburgh that offer an exceptional range of organic products to support everyday living",
            location="Edinburgh, Scotland", url="https://www.realfoods.co.uk/", user=user, category=category)

session.add(item)
session.commit()

item = Item(name="Robin Hartford's Foraging Courses and Wild Food Walks", description="The web portal to guided walks on wild foods available in England",
                     locatiion="England", url="https://www.foragingcourses.com/", user=user, category=category)
session.add(item)
session.commit()

item = Item(name="Fat Hen", description="The website of a professional forager who also offers courses on the subject.",
                     locatiion="England", url="http://www.fathen.org/", user=user, category=category)
session.add(item)
session.commit()

session.add(category)
session.commit()
