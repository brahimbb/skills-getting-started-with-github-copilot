import pytest

from src.app import activities


@pytest.fixture(autouse=True)
def restore_activity_participants():
    participant_lists = {
        name: details["participants"].copy()
        for name, details in activities.items()
    }

    yield

    for name, participants in participant_lists.items():
        activities[name]["participants"] = participants
