

class TestObject:

    def __init__(self) -> None:
        pass

    def run(self, json_response) -> bool:

        print(json_response)


        if type(json_response.result) != bool:
            print(json_response.result.channel)
