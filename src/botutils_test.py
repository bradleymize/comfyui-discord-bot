import logging
from unittest.mock import MagicMock
import pytest
import botutils
from testutils.mock import create_mock_object

class Test_is_valid_reaction():
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

class Test_parse_message():
    def test_does_nothing_if_not_queued_image_message(self, caplog):
        caplog.set_level(logging.INFO)
        assert botutils.parse_message("foo") is None
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message == "Message is not parseable"

    def test_parses_single_line_prompt(self):
        expected = {
            'workflow': 'myWorkflow',
            'seed': '12345',
            'width': '1024',
            'height': '768',
            'steps': '4',
            'cfg': 1,
            'prompt': 'Some single line prompt'
        }
        message = f"""Queued an image
Workflow: {expected['workflow']}
Seed: {expected['seed']}
Width: {expected['width']}
Height: {expected['height']}
Steps: {expected['steps']}
Prompt: {expected['prompt']}
prompt id: anything here unused
"""
        assert botutils.parse_message(message) == expected

    def test_parses_multi_line_prompt(self):
        expected = {
            'workflow': 'myWorkflow',
            'seed': '12345',
            'width': '1024',
            'height': '768',
            'steps': '4',
            'cfg': 1,
            'prompt': 'Some multi-line prompt\nAnd this is the second line\nAnd a third for funsies'
        }
        message = f"""Queued an image
Workflow: {expected['workflow']}
Seed: {expected['seed']}
Width: {expected['width']}
Height: {expected['height']}
Steps: {expected['steps']}
Prompt: {expected['prompt']}
prompt id: anything here unused
"""
        assert botutils.parse_message(message) == expected

class Test_get_and_fill_template():
    def test_should_return_filled_template(self, caplog):
        caplog.set_level(logging.INFO)
        values_map = {
            'workflow': 'default.json.template',
            'seed': '12345',
            'width': '1024',
            'height': '768',
            'steps': '4',
            'cfg': 1,
            'prompt': 'Cat in the hat'
        }
        filled_template = botutils.get_and_fill_template(values_map)

        assert caplog.records[0].levelname == "INFO"
        assert caplog.records[0].message == f"Getting workflow: {values_map['workflow']}"
        assert f"\"seed\": {values_map['seed']}" in filled_template
        assert f"\"width\": {values_map['width']}" in filled_template
        assert f"\"height\": {values_map['height']}" in filled_template
        assert f"\"steps\": {values_map['steps']}" in filled_template
        assert f"\"cfg\": {values_map['cfg']}" in filled_template
        assert f"\"text\": \"{values_map['prompt']}\"" in filled_template

class Test_get_interaction_by_prompt_id():
    def test_should_return_when_single_interaction(self):
        prompt_id = "123456"
        mock_interaction = MagicMock()
        type(mock_interaction).prompt_id = prompt_id
        botutils.interaction_queue = [mock_interaction]

        assert botutils.get_interaction_by_prompt_id(prompt_id) == mock_interaction

    def test_should_return_with_warning_when_multiple_interaction(self, caplog):
        caplog.set_level(logging.WARNING)
        prompt_id = "123456"
        mock_interaction_one = MagicMock()
        type(mock_interaction_one).prompt_id = prompt_id
        type(mock_interaction_one).name = "one"
        mock_interaction_two = MagicMock()
        type(mock_interaction_two).name = "two"
        type(mock_interaction_two).prompt_id = prompt_id


        botutils.interaction_queue = [mock_interaction_one, mock_interaction_two]

        retrieved_interaction = botutils.get_interaction_by_prompt_id(prompt_id)
        assert retrieved_interaction  == mock_interaction_one
        assert retrieved_interaction.prompt_id  == mock_interaction_one.prompt_id
        assert retrieved_interaction.prompt_id  == mock_interaction_two.prompt_id
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message == "Multiple interactions found, returning the first one, but this shouldn't happen"

    def test_should_raise_exception_if_no_interactions(self):
        prompt_id = "123456"
        botutils.interaction_queue = []

        with pytest.raises(Exception, match=f"Unable to find interaction with prompt_id: {prompt_id}"):
            botutils.get_interaction_by_prompt_id(prompt_id)

class Test_remove_interaction():
    def test_removes_interaction_when_present(self, caplog):
        caplog.set_level(logging.INFO)
        mock_interaction = MagicMock()
        botutils.interaction_queue = [mock_interaction]

        botutils.remove_interaction(mock_interaction)
        assert caplog.records[0].levelname == "INFO"
        assert caplog.records[0].message == "Removing interaction from queue"
        assert botutils.interaction_queue == []

    def test_logs_warning_when_interaction_not_in_queue(self, caplog):
        caplog.set_level(logging.INFO)
        mock_interaction = MagicMock()
        botutils.interaction_queue = []

        botutils.remove_interaction(mock_interaction)
        assert botutils.interaction_queue == []
        assert caplog.records[0].levelname == "INFO"
        assert caplog.records[0].message == "Removing interaction from queue"
        assert caplog.records[1].levelname == "WARNING"
        assert caplog.records[1].message == "Nothing to remove, interaction is not in the queue"
