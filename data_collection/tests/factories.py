import json

from data_collection.models import RawData, DataRequest


def create_raw_data(**kwargs) -> RawData:
    raw_data = kwargs.get("raw_data")
    if not raw_data:
        sample_data = {"1": "1", "2": "2"}
        raw_data = json.dumps(sample_data)

    return RawData.objects.create(
        data_format=kwargs.get("data_format", RawData.DataFormats.JSON),
        data_type=kwargs.get("data_type", RawData.DataTypes.RESUME),
        raw_data=raw_data,
        data_request=kwargs.get("data_request", create_data_request()),
    )


def create_data_request(**kwargs) -> DataRequest:
    return DataRequest.objects.create(
        service=kwargs.get("service", DataRequest.Services.GLOBAL_TECH_ATS)
    )
