from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from lostandfound.models import Category


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        include_relationships = True
        load_instance = True


category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
