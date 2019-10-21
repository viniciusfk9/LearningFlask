"""empty message

Revision ID: 797527a05e23
Revises: 9f336475d91f
Create Date: 2017-06-24 21:38:36.576263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '797527a05e23'
down_revision = '9f336475d91f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('options', schema=None) as batch_op:
        batch_op.create_unique_constraint('unique_user_name', ['name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('options', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###