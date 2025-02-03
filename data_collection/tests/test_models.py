import json

import pytest

from data_collection.models import RawData
from data_collection.tests.factories import create_raw_data


@pytest.mark.django_db
def test_raw_data_parsed_data():
    # given
    test_data = {"1": "123", "2": "456"}
    raw_data = create_raw_data(
        raw_data=json.dumps(test_data), data_format=RawData.DataFormats.JSON
    )

    # when / then
    assert raw_data.parsed_data == test_data
