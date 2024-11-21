from unittest.mock import MagicMock


def create_mock_object(properties: dict) -> MagicMock:
    ####################################################
    def _create_nested_mock_object(parent: MagicMock, props: dict) -> MagicMock:
        for prop_name in props:
            if isinstance(props[prop_name], dict):
                if not prop_name.endswith("_dict"):
                    setattr(type(parent), prop_name, _create_nested_mock_object(MagicMock(), props[prop_name]))
                else:
                    setattr(type(parent), prop_name[:-5], props[prop_name])
            else:
                setattr(type(parent), prop_name, props[prop_name])

        return parent
    ####################################################
    return _create_nested_mock_object(MagicMock(), properties)


def print_mock(mock: MagicMock):
    ####################################################
    def _populate_attributes(obj: dict, mock_obj: MagicMock) -> dict:
        valid_properties = filter(lambda method: not method.startswith("__") and not method.endswith("__"), vars(type(mock_obj)))
        for prop in valid_properties:
            value = getattr(mock_obj, prop)
            if isinstance(value, MagicMock):
                # print(f"mock_obj.{prop} is another MagicMock, recurse")
                obj[prop] = _populate_attributes({}, value)
            else:
                # print(f"mock_obj.{prop} = {value}")
                obj[prop] = value

        return obj
    ####################################################
    print(_populate_attributes({}, mock))
