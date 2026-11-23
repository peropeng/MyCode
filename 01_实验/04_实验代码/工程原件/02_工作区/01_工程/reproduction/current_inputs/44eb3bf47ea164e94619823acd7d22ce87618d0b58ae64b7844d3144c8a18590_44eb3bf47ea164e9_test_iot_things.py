import boto3

from moto import mock_iot
from moto.core import DEFAULT_ACCOUNT_ID as ACCOUNT_ID


pass  # withheld independent test














pass  # withheld independent test




















pass  # withheld independent test























































@mock_iot
def test_describe_thing():
    client = boto3.client("iot", region_name="ap-northeast-1")
    name = "my-thing"

    client.create_thing(thingName=name)
    client.update_thing(thingName=name, attributePayload={"attributes": {"k1": "v1"}})

    thing = client.describe_thing(thingName=name)
    assert thing["thingName"] == name
    assert "defaultClientId" in thing
    assert thing["attributes"] == {"k1": "v1"}
    assert thing["version"] == 1


pass  # withheld independent test













@mock_iot
def test_list_things_with_next_token():
    client = boto3.client("iot", region_name="ap-northeast-1")

    for i in range(0, 200):
        client.create_thing(thingName=str(i + 1))

    things = client.list_things()
    assert len(things["things"]) == 50
    assert things["things"][0]["thingName"] == "1"
    assert (
        things["things"][0]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/1"
    )
    assert things["things"][-1]["thingName"] == "50"
    assert (
        things["things"][-1]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/50"
    )

    things = client.list_things(nextToken=things["nextToken"])
    assert len(things["things"]) == 50
    assert things["things"][0]["thingName"] == "51"
    assert (
        things["things"][0]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/51"
    )
    assert things["things"][-1]["thingName"] == "100"
    assert (
        things["things"][-1]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/100"
    )

    things = client.list_things(nextToken=things["nextToken"])
    assert len(things["things"]) == 50
    assert things["things"][0]["thingName"] == "101"
    assert (
        things["things"][0]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/101"
    )
    assert things["things"][-1]["thingName"] == "150"
    assert (
        things["things"][-1]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/150"
    )

    things = client.list_things(nextToken=things["nextToken"])
    assert "nextToken" not in things
    assert len(things["things"]) == 50
    assert things["things"][0]["thingName"] == "151"
    assert (
        things["things"][0]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/151"
    )
    assert things["things"][-1]["thingName"] == "200"
    assert (
        things["things"][-1]["thingArn"]
        == f"arn:aws:iot:ap-northeast-1:{ACCOUNT_ID}:thing/200"
    )


pass  # withheld independent test















































































































