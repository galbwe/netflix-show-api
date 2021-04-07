"""update string column lengths, add director table

Revision ID: 477fc039b87e
Revises: 269caaa5cf46
Create Date: 2021-04-07 00:15:28.814211

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '477fc039b87e'
down_revision = '269caaa5cf46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('director',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('director_netflix_title',
    sa.Column('director_id', postgresql.UUID(), nullable=True),
    sa.Column('netflix_title_id', postgresql.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['director_id'], ['director.id'], ),
    sa.ForeignKeyConstraint(['netflix_title_id'], ['netflix_title.id'], )
    )
    op.drop_column('netflix_title', 'director')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('netflix_title', sa.Column('director', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.drop_table('director_netflix_title')
    op.drop_table('director')
    # ### end Alembic commands ###