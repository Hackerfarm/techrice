"""empty message

Revision ID: d434734cea00
Revises: None
Create Date: 2016-02-27 14:15:57.261304

"""

# revision identifiers, used by Alembic.
revision = 'd434734cea00'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensortypes', sa.Column('description', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensortypes', 'description')
    ### end Alembic commands ###
