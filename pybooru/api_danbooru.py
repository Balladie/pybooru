# -*- coding: utf-8 -*-

"""pybooru.api_danbooru

This module contains all API calls of Danbooru for Pybooru.

Classes:
    Danbooru -- Contains all API calls.
"""

# __future__ imports
from __future__ import absolute_import

# pybooru imports
from .exceptions import PybooruAPIError


class DanbooruApi(object):
    """Contains all Danbooru API calls.

    API Versions: v2.105.0
    doc: https://danbooru.donmai.us/wiki_pages/43568
    """

    def post_list(self, **params):
        """Get a list of posts.

        Parameters:
            limit: How many posts you want to retrieve. There is a hard limit
                   of 100 posts per request.
            page: The page number.
            tags: The tags to search for. Any tag combination that works on the
                  web site will work here. This includes all the meta-tags.
            raw: When this parameter is set the tags parameter will not be
                 parsed for aliased tags, metatags or multiple tags, and will
                 instead be parsed as a single literal tag.
        """
        return self._get('posts.json', params)

    def post_show(self, id_):
        """Get a post

        Parameters:
            id_: where id_ is the post id.
        """
        return self._get("/posts/{0}.json".format(id_))

    def post_update(self, id_, tag_string=None, rating=None, source=None,
                    parent_id=None):
        """Update a specific post.

        Parameters:
            id_: The id number of the post to update.
            tag_string: A space delimited list of tags.
            rating: The rating for the post. Can be: safe, questionable, or
                    explicit.
            source: If this is a URL, Danbooru will download the file.
            parent_id: The ID of the parent post.
        """
        params = {
            'post[tag_string]': tag_string,
            'post[rating]': rating,
            'ost[source]': source,
            'post[parent_id]': parent_id
            }
        return self._get('/posts/{0}.json'.format(id_), params, 'PUT')
