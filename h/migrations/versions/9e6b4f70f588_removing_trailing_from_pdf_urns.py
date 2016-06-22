"""Remove trailing # from PDF URNs.

Revision ID: 9e6b4f70f588
Revises: 467ea2898660
Create Date: 2016-06-21 17:50:14.261947

"""
from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '9e6b4f70f588'
down_revision = '467ea2898660'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from h.models import Annotation
from h.models import DocumentURI


Session = sessionmaker()


def upgrade():
    session = Session(bind=op.get_bind())

    document_uris = session.query(DocumentURI).filter(
        sa.or_(
            DocumentURI.claimant.like('urn:x-pdf:%#'),
            DocumentURI.uri.like('urn:x-pdf:%#'),
        )
    )

    for doc_uri in document_uris:

        if doc_uri.claimant.endswith('#'):
            new_claimant = doc_uri.claimant[:-1]
        else:
            new_claimant = doc_uri.claimant

        if doc_uri.claimant_normalized.endswith('#'):
            new_claimant_normalized = doc_uri.claimant_normalized[:-1]
        else:
            new_claimant_normalized = doc_uri.claimant_normalized

        if doc_uri.uri.endswith('#'):
            new_uri = doc_uri.uri[:-1]
        else:
            new_uri = doc_uri.uri

        if doc_uri.uri_normalized.endswith('#'):
            new_uri_normalized = doc_uri.uri_normalized[:-1]
        else:
            new_uri_normalized = doc_uri.uri_normalized

        conflicting_doc_uris = session.query(DocumentURI).filter_by(
            claimant_normalized=new_claimant_normalized,
            uri_normalized=new_uri_normalized,
            type=doc_uri.type,
            content_type=doc_uri.content_type)

        conflicting_doc_uri = conflicting_doc_uris.one_or_none()

        if conflicting_doc_uri:
            session.delete(doc_uri)
        else:
            doc_uri.claimant = new_claimant
            doc_uri.uri = new_uri

    annotations = session.query(Annotation).filter(
        Annotation.target_uri.like('urn:x-pdf:%#'))

    for annotation in annotations:
        annotation.target_uri = annotation.target_uri[:-1]

    session.commit()


def downgrade():
    pass
