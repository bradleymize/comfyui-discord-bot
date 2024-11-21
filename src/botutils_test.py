from unittest import TestCase
import botutils
from testutils.mock import create_mock_object

class is_valid_reaction(TestCase):
    def test_is_valid_reaction(self):
        mock_RawReactionActionEvent = create_mock_object({
            'emoji': {'name': botutils.Reaction.REPEAT.value},
            'member': {'bot': False},
            'data_dict': {'message_author_id': '1'}
        })
        assert botutils.is_valid_reaction(mock_RawReactionActionEvent, 1)

    def test_fails_if_emoji_is_unsupported(self):
        mock_RawReactionActionEvent = create_mock_object({
            'emoji': {'name': "anything else"},
            'member': {'bot': False},
            'data_dict': {'message_author_id': '1'}
        })
        assert not botutils.is_valid_reaction(mock_RawReactionActionEvent, 1)

    def test_fails_if_bot_added_reaction(self):
        mock_RawReactionActionEvent = create_mock_object({
            'emoji': {'name': botutils.Reaction.REPEAT.value},
            'member': {'bot': True},
            'data_dict': {'message_author_id': '1'}
        })
        assert not botutils.is_valid_reaction(mock_RawReactionActionEvent, 1)

    def test_fails_if_message_belongs_to_different_bot(self):
        mock_RawReactionActionEvent = create_mock_object({
            'emoji': {'name': botutils.Reaction.REPEAT.value},
            'member': {'bot': False},
            'data_dict': {'message_author_id': '2'}
        })
        assert not botutils.is_valid_reaction(mock_RawReactionActionEvent, 1)