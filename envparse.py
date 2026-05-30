import os


def get_str(var_name: str) -> str:
    temp = os.getenv(var_name, None)
    assert_text = f"{var_name}={temp} is incorrectly defined in `.env`"
    assert temp is not None, assert_text
    return temp


def get_int(var_name: str) -> int:
    raw_text = get_str(var_name)
    try:
        temp = int(raw_text)
        return temp
    except Exception as ex:
        assert_text = (
            f"{var_name}={raw_text} could not be converted into int from `.env`"
        )
        assert False, assert_text


def get_bool(var_name: str) -> bool:
    temp = get_str(var_name)
    match temp.lower():
        case "true":
            return True
        case "false":
            return False
        case _:
            assert_text = f"{var_name}={temp} is not `true` or `false` in `.env`"
            assert False, assert_text


if __name__ == "__main__":
    pass
