# -*- coding: utf-8 -*-

import sqlalchemy as sa
from pyramid import security
from sqlalchemy.orm import exc
import slugify

from h.api import models
from h.db import Base
from h.db import mixins
from h import pubid


GROUP_NAME_MIN_LENGTH = 4
GROUP_NAME_MAX_LENGTH = 25


class GroupFactory(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, pubid):
        try:
            return self.request.db.query(Group).filter_by(pubid=pubid).one()
        except exc.NoResultFound:
            raise KeyError()


class Group(Base, mixins.Timestamps):
    __tablename__ = 'group'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    # We don't expose the integer PK to the world, so we generate a short
    # random string to use as the publicly visible ID.
    pubid = sa.Column(sa.Text(),
                      default=pubid.generate,
                      unique=True,
                      nullable=False)
    name = sa.Column(sa.UnicodeText(), nullable=False, index=True)

    # We store information about who created the group -- we don't use this
    # currently, but it seems careless to lose this information when in the
    # future these people may be the first admins of their groups.
    creator_id = sa.Column(
        sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    creator = sa.orm.relationship('User')

    # Group membership
    members = sa.orm.relationship(
        'User', secondary='user_group', backref=sa.orm.backref(
            'groups', order_by='Group.name'))

    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.members.append(creator)

    @sa.orm.validates('name')
    def validate_name(self, key, name):
        if not GROUP_NAME_MIN_LENGTH <= len(name) <= GROUP_NAME_MAX_LENGTH:
            raise ValueError('name must be between {min} and {max} characters '
                             'long'.format(min=GROUP_NAME_MIN_LENGTH,
                                           max=GROUP_NAME_MAX_LENGTH))
        return name

    @property
    def slug(self):
        """A version of this group's name suitable for use in a URL."""
        return slugify.slugify(self.name)

    def documents(self, limit=25):
        """
        Return this group's most recently annotated documents.

        Only returns documents that have shared annotations in this group,
        not documents that only have private annotations in the group.

        """
        documents = []
        annotations = (
            sa.orm.object_session(self).query(models.Annotation)
            .filter_by(groupid=self.pubid, shared=True)
            .order_by(models.Annotation.updated.desc())
            .limit(1000))
        for annotation in annotations:
            if annotation.document and annotation.document not in documents:
                documents.append(annotation.document)
                if len(documents) >= limit:
                    break

        return documents

    def __acl__(self):
        return [
            (security.Allow, 'group:{}'.format(self.pubid), 'read'),
            security.DENY_ALL,
        ]

    def __repr__(self):
        return '<Group: %s>' % self.slug

    @classmethod
    def created_by(cls, session, user):
        """Return a query object filtering groups by creator."""
        return session.query(cls).filter(Group.creator == user)


USER_GROUP_TABLE = sa.Table(
    'user_group', Base.metadata,
    sa.Column('user_id',
              sa.Integer,
              sa.ForeignKey('user.id'),
              nullable=False),
    sa.Column('group_id',
              sa.Integer,
              sa.ForeignKey('group.id'),
              nullable=False)
)
