# Purpose: Contains the Method class, which is used to represent a method of
# calculating prayer times.


from myprayer.api.location_types import Coordinates


class Method:
    name: str
    id: int
    params: dict[str, str]
    location: Coordinates

    def __init__(
        self,
        data: dict,
    ):
        self.name = data["name"]
        self.id = int(data["id"])
        self.params = data["params"]
        if "location" in data:
            self.location = Coordinates(
                data["location"]["latitude"],
                data["location"]["longitude"],
            )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"
