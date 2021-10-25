"""trial

Revision ID: 35a3a5115a38
Revises: 
Create Date: 2021-10-06 14:36:09.798948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35a3a5115a38'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('timer',
    sa.Column('pomodoro_id', sa.Integer(), nullable=False),
    sa.Column('pomodoro_count', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('pomodoro_complete', sa.Boolean(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ),
    sa.PrimaryKeyConstraint('pomodoro_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('timer')
    # ### end Alembic commands ###
