"""Provides the User class."""
from ..const import API_PATH
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .reddit.redditor import Redditor
from .reddit.subreddit import Subreddit


class User(PRAWBase):
    """The user class provides methods for the currently authenticated user."""

    def __init__(self, reddit):
        """Initialize a User instance.

        This class is intended to be interfaced with through ``reddit.user``.

        """
        super(User, self).__init__(reddit, None)
        self._me = None

    def blocked(self):
        """Return a RedditorList of blocked Redditors."""
        return self._reddit.get(API_PATH['blocked'])

    def contributor_subreddits(self, **generator_kwargs):
        """Return a ListingGenerator of subreddits user is a contributor of.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['my_contributor'],
                                **generator_kwargs)

    def friends(self):
        """Return a RedditorList of friends."""
        return self._reddit.get(API_PATH['friends'])

    def karma(self):
        """Return a dictionary mapping subreddits to their karma."""
        karma_map = {}
        for row in self._reddit.get(API_PATH['karma'])['data']:
            subreddit = Subreddit(self._reddit, row['sr'])
            del row['sr']
            karma_map[subreddit] = row
        return karma_map

    def me(self, use_cache=True):  # pylint: disable=invalid-name
        """Return a :class:`.Redditor` instance for the authenticated user.

        :param use_cache: When true, and if this function has been previously
            called, returned the cached version (default: True).

        .. note:: If you change the Reddit instance's authorization, you might
           want to refresh the cached value. Prefer using separate Reddit
           instances, however, for distinct authorizations.

        """
        if self._me is None or not use_cache:
            user_data = self._reddit.get(API_PATH['me'])
            self._me = Redditor(self._reddit, _data=user_data)
        return self._me

    def moderator_subreddits(self, **generator_kwargs):
        """Return a ListingGenerator of subreddits the user is a moderator of.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['my_moderator'],
                                **generator_kwargs)

    def multireddits(self):
        """Return a list of multireddits belonging to the user."""
        return self._reddit.get(API_PATH['my_multireddits'])

    def subreddits(self, **generator_kwargs):
        """Return a ListingGenerator of subreddits the user is subscribed to.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['my_subreddits'],
                                **generator_kwargs)
