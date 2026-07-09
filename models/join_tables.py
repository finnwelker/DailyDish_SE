from sqlalchemy import Column, Integer, String, Table, ForeignKey
from database import Base

# Tags und User
user_tags = Table("user_tags", Base.metadata,
                  Column("user_id", Integer, ForeignKey("users.id")),
                  Column("tag_id", Integer, ForeignKey("tags.id")))

# Tags und Rezepte
recipe_tags = Table("recipe_tags", Base.metadata,
                    Column("recipe_id", Integer, ForeignKey("recipes.id")),
                    Column("tag_id", Integer, ForeignKey("tags.id"))
                    )

favourites = Table("favourites", Base.metadata,
                   Column("user_id", Integer, ForeignKey("users.id")),
                   Column("recipe_id", Integer, ForeignKey("recipes.id")))
