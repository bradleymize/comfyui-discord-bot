import logging
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
import botutils
import discord
from testutils.mock import create_mock_object

class Test_ComfyUICommand():
    def test_populates_defaults(self):
        expected = 'A simple prompt'
        cmd = botutils.ComfyUICommand(
            MagicMock(),
            'A simple prompt',
        )
        assert cmd.prompt == expected
        assert cmd.workflow == "default.json.template"
        assert cmd.seed is not None
        assert cmd.width == 1024
        assert cmd.height == 1024
        assert cmd.steps == 4
        assert cmd.cfg == 1

    def test_sets_overrides(self):
        expected = 'A simple prompt'
        cmd = botutils.ComfyUICommand(
            MagicMock(),
            'A simple prompt',
            "my.workflow",
            '1',
            2,
            3,
            8,
            9
        )
        assert cmd.prompt == expected
        assert cmd.workflow == "my.workflow"
        assert cmd.seed == 1
        assert cmd.width == 2
        assert cmd.height == 3
        assert cmd.steps == 8
        assert cmd.cfg == 9

    def test_makes_prompt_json_friendly(self):
        expected = 'A \\"complex\\" prompt'
        cmd = botutils.ComfyUICommand(
            MagicMock(),
            'A "complex" prompt',
        )
        assert cmd.prompt == expected

    def test_returns_configuration(self):
        cmd = botutils.ComfyUICommand(
            MagicMock(),
            'A simple prompt',
            "my.workflow",
            '1',
            2,
            3,
            8,
            9
        )
        values_map = cmd.get_values_map()
        assert values_map['workflow'] == "my.workflow"
        assert values_map['seed'] == 1
        assert values_map['width'] == 2
        assert values_map['height'] == 3
        assert values_map['steps'] == 8
        assert values_map['cfg'] == 9
        assert values_map['prompt'] == "A simple prompt"

class Test_MyBotInteraction():
    @pytest.mark.asyncio
    async def test_create_raises_exception_if_not_supported_data_type(self):
        with pytest.raises(Exception, match=f"Unsupported interaction data: foo"):
            mock_data = MagicMock()
            type(mock_data).__name__ = "foo"
            await botutils.MyBotInteraction.create(MagicMock(), mock_data)

    @pytest.mark.asyncio
    async def test_creates_instance_using_comfy_ui_command(self):
        ctx = create_mock_object({
            'interaction': {
                'user': 'foobar'
            }
        })
        cmd = botutils.ComfyUICommand(
            ctx,
            'A simple prompt',
        )
        interaction = await botutils.MyBotInteraction.create(MagicMock(), cmd)
        assert interaction.interaction_type == botutils.InteractionType.COMFY_UI_COMMAND
        assert interaction.mention == 'foobar'
        assert interaction.values_map['width'] == 1024

    @pytest.mark.asyncio
    @patch('random.getrandbits')
    @patch('botutils.parse_message')
    async def test_create_handles_repeat_reaction(self, mock_parse_message, mock_getrandbits):
        reaction = create_mock_object({
            'channel_id': 1,
            'message_id': 2,
            'user_id': 3,
            'emoji': {
                'name': botutils.Reaction.REPEAT.value
            }
        })
        reaction.__class__ = discord.RawReactionActionEvent

        channel_mock = MagicMock()
        channel_mock.fetch_message = AsyncMock(side_effect=[
            create_mock_object({
                'reference': {
                    'message_id': 'reference to original message'
                }
            }),
            create_mock_object({
                'content': 'the original message'
            })
        ])

        bot_mock = MagicMock()
        bot_mock.fetch_channel = AsyncMock(return_value=channel_mock)
        bot_mock.fetch_user = AsyncMock(return_value="John Doe")

        mock_parse_message.return_value = {'seed': 1}
        mock_getrandbits.return_value = 4

        interaction = await botutils.MyBotInteraction.create(bot_mock, reaction)

        assert interaction.message.reference.message_id == "reference to original message"
        assert interaction.reply_to.content == "the original message"
        assert interaction.mention == "John Doe"
        assert interaction.values_map['seed'] == 4
        bot_mock.fetch_channel.assert_called_with(1)
        channel_mock.fetch_message.mock_calls[0].assert_called_with(2)
        channel_mock.fetch_message.mock_calls[1].assert_called_with("reference to original message")
        bot_mock.fetch_user.assert_called_with(3)

    @pytest.mark.asyncio
    @patch('botutils.parse_message')
    async def test_create_handles_delete_reaction(self, mock_parse_message):
        reaction = create_mock_object({
            'channel_id': 1,
            'message_id': 2,
            'user_id': 3,
            'emoji': {
                'name': botutils.Reaction.DELETE.value
            }
        })
        reaction.__class__ = discord.RawReactionActionEvent

        channel_mock = MagicMock()
        channel_mock.fetch_message = AsyncMock(side_effect=[
            create_mock_object({
                'reference': {
                    'message_id': 'reference to original message'
                }
            }),
            create_mock_object({
                'content': 'the original message'
            })
        ])

        bot_mock = MagicMock()
        bot_mock.fetch_channel = AsyncMock(return_value=channel_mock)
        bot_mock.fetch_user = AsyncMock(return_value="John Doe")

        mock_parse_message.return_value = {'seed': 1}

        interaction = await botutils.MyBotInteraction.create(bot_mock, reaction)

        assert interaction.message.reference.message_id == "reference to original message"
        assert interaction.reply_to.content == "the original message"
        assert interaction.mention == "John Doe"
        assert interaction.values_map['seed'] == 1

    @pytest.mark.asyncio
    async def test_create_throws_exception_for_unsupported_emoji(self):
        reaction = create_mock_object({
            'emoji': {
                'name': "anything"
            }
        })
        reaction.__class__ = discord.RawReactionActionEvent
        bot_mock = MagicMock()

        with pytest.raises(Exception, match=f"Unsupported reaction: anything"):
            await botutils.MyBotInteraction.create(bot_mock, reaction)

    @pytest.mark.asyncio
    async def test_get_prompt_returns_the_prompt_string(self, caplog):
        caplog.set_level(logging.INFO)
        ctx = create_mock_object({
            'interaction': {
                'user': 'foobar'
            }
        })
        cmd = botutils.ComfyUICommand(
            ctx,
            'A simple prompt',
        )
        interaction = await botutils.MyBotInteraction.create(MagicMock(), cmd)
        prompt = interaction.get_prompt()

        assert caplog.records[0].levelname == "INFO"
        assert caplog.records[0].message == "Getting workflow template and prompt"
        assert "A simple prompt" == prompt["6"]["inputs"]["text"]

    @pytest.mark.asyncio
    @patch('random.getrandbits')
    @patch('botutils.parse_message')
    async def test_MyBotInteraction_string_representation(self, mock_parse_message, mock_getrandbits):
        reaction = create_mock_object({
            'channel_id': 1,
            'message_id': 2,
            'user_id': 3,
            'emoji': {
                'name': botutils.Reaction.REPEAT.value
            }
        })
        reaction.__class__ = discord.RawReactionActionEvent

        channel_mock = MagicMock()
        channel_mock.fetch_message = AsyncMock(side_effect=[
            create_mock_object({
                'reference': {
                    'message_id': 'reference to original message'
                }
            }),
            create_mock_object({
                'id': 8,
                'content': 'the original message'
            })
        ])

        bot_mock = MagicMock()
        bot_mock.fetch_channel = AsyncMock(return_value=channel_mock)
        bot_mock.fetch_user = AsyncMock(return_value="John Doe")

        mock_parse_message.return_value = {'seed': 1}
        mock_getrandbits.return_value = 4

        interaction = await botutils.MyBotInteraction.create(bot_mock, reaction)
        interaction_representation = f"{interaction}"

        assert "MyBotInteraction(REPEAT, mention John Doe when replying to message 8)" in interaction_representation
        assert "{'seed': 4}" in interaction_representation

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
