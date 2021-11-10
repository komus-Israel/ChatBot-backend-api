"""empty message

Revision ID: f328c033f429
Revises: 7bca24d77737
Create Date: 2021-11-10 07:52:34.614538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f328c033f429'
down_revision = '7bca24d77737'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feed_back', sa.Column('feedback', sa.Text(), nullable=False))
    op.add_column('feed_back', sa.Column('date', sa.String(length=200), nullable=False))
    op.drop_index('ix_feed_back_admin_id', table_name='feed_back')
    op.create_index(op.f('ix_feed_back_feedback'), 'feed_back', ['feedback'], unique=False)
    op.drop_column('feed_back', 'admin_id')
    op.drop_column('feed_back', 'date_registered')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feed_back', sa.Column('date_registered', sa.VARCHAR(length=200), autoincrement=False, nullable=False))
    op.add_column('feed_back', sa.Column('admin_id', sa.VARCHAR(length=200), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_feed_back_feedback'), table_name='feed_back')
    op.create_index('ix_feed_back_admin_id', 'feed_back', ['admin_id'], unique=False)
    op.drop_column('feed_back', 'date')
    op.drop_column('feed_back', 'feedback')
    # ### end Alembic commands ###
