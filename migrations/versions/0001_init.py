"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
import app.models as models

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum(models.Role), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'datacenters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'objects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dc_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum(models.ObjectType), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('ip', sa.String(), nullable=True),
        sa.Column('fqdn', sa.String(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['dc_id'], ['datacenters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('section', sa.Enum(models.PageSection), nullable=False),
        sa.Column('content_md', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['object_id'], ['objects.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'relations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('src_object_id', sa.Integer(), nullable=False),
        sa.Column('dst_object_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['dst_object_id'], ['objects.id'], ),
        sa.ForeignKeyConstraint(['src_object_id'], ['objects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('kind', sa.Enum(models.DocumentKind), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['object_id'], ['objects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('symptom', sa.Text(), nullable=True),
        sa.Column('cause', sa.Text(), nullable=True),
        sa.Column('check', sa.Text(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['object_id'], ['objects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('incidents')
    op.drop_table('documents')
    op.drop_table('relations')
    op.drop_table('pages')
    op.drop_table('objects')
    op.drop_table('datacenters')
    op.drop_table('companies')
    op.drop_table('users')
