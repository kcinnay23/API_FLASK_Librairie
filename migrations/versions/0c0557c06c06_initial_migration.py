"""Initial migration

Revision ID: 0c0557c06c06
Revises: 
Create Date: 2022-02-15 19:38:26.104922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c0557c06c06'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('livres', 'categorie_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('livres', 'categorie_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
