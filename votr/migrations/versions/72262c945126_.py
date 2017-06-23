"""empty message

Revision ID: 72262c945126
Revises: da5c40eb9fce
Create Date: 2017-06-23 18:02:33.100440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72262c945126'
down_revision = 'da5c40eb9fce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("polls") as batch_op:
        batch_op.drop_column('status')
    op.add_column('topics', sa.Column('status', sa.Boolean(), default=1))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('test', sa.VARCHAR(length=500), nullable=True))

    # ### end Alembic commands ###
