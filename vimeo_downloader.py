import requests
import base64
from urllib.parse import urljoin


def get_json(master_url):
    response = requests.get(master_url)

    if response.status_code == 200:
        return response.json()

    else:
        return {}


def process_file(file_type: str, base_url, init_segment, segments, filename):
    segments_url = [f"{base_url}{segment['url']}" for segment in segments]
    segments_amount = len(segments_url)

    with open(filename, "wb") as output_file:
        output_file.write(base64.decodebytes(init_segment.encode('utf-8')))

    print(f">> Started Downloading -> {file_type}")

    for index, url in enumerate(segments_url):
        print(f">> Downloading {file_type} -> {index}/{segments_amount} Segments")
        res = requests.get(url)

        with open(filename, "ab") as output_file:
            output_file.write(res.content)

    print(f">> Finished Downloading -> {file_type}")


if __name__ == "__main__":
    master_url = "https://148vod-adaptive.akamaized.net/exp=1637310951~acl=%2Fab3d8cec-5ead-4321-b4a7-4e68b6d5e013%2F%2A~hmac=d2c0dd30ea2a482297ff48598f95cbd9a92567341453129b0fa8eb625d64bf5f/ab3d8cec-5ead-4321-b4a7-4e68b6d5e013/sep/video/4a5eb5ea,9fed1758,ef942145,e58e2097,fc8f7529/master.json?base64_init=1"
    res_json = get_json(master_url)

    if not res_json:
        print(">> No response from master url")
        quit()


    video_data = res_json["video"][0]   # TODO: Quailty Selector 
    audio_data = res_json["audio"][0]   # TODO: Quailty Selector 

    video_base_url = urljoin(urljoin(master_url, res_json["base_url"]), video_data["base_url"])
    audio_base_url = urljoin(urljoin(master_url, res_json["base_url"]), audio_data["base_url"])

    process_file("Video", video_base_url, video_data["init_segment"], video_data["segments"], f"{res_json['clip_id']}.m4v")
    process_file("Audio", audio_base_url, audio_data["init_segment"], audio_data["segments"], f"{res_json['clip_id']}.m4a")
