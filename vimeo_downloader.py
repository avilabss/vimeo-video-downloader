import requests
import base64
import sys
import os
import threading
from urllib.parse import urljoin


MAX_TRIES = 3
TIMEOUT = 10


def get_master_json(master_url: str) -> dict:
    tries = 0

    while tries < MAX_TRIES:
        tries += 1

        try:
            response = requests.get(master_url, timeout=TIMEOUT)

            if response.status_code == 200:
                return response.json()

            else:
                print(">> No response from master url")
                quit()

        except:
            print(f"Exception occured while fetching master json. Trying again ({tries})")

    else:
        print(">> Failed to fetch master json.")
        quit()


def get_content_segment(segment_url: str) -> bytes:
    tries = 0

    while tries < MAX_TRIES:
        tries += 1

        try:
            response = requests.get(segment_url, timeout=TIMEOUT)

            if response.status_code == 200:
                return response.content

            else:
                print(">> No response from segment url")
                quit()

        except:
            print(f"Exception occured while fetching content segment. Trying again ({tries})")

    else:
        print(">> Failed to fetch content segment.")
        quit()


def process_file(file_type: str, base_url: str, init_segment: str, segments: list, filename: str) -> None:
    segments_url = [f"{base_url}{segment['url']}" for segment in segments]
    segments_amount = len(segments_url)

    with open(filename, "wb") as output_file:
        output_file.write(base64.decodebytes(init_segment.encode('utf-8')))

    print(f">> Started Downloading -> {file_type}")

    for index, url in enumerate(segments_url):
        print(f">> Downloading {file_type} -> {index + 1}/{segments_amount} Segments")
        
        content = get_content_segment(url)

        with open(filename, "ab") as output_file:
            output_file.write(content)

    print(f">> Finished Downloading -> {file_type}")


def select_quality(video_data: list, audio_data: list) -> tuple:
    # TODO: Cli implementation for selecting quality. Only returning max quality right now!
    video_qualities = []
    audio_qualities = []
    max_video_quality = None
    max_audio_quality = None

    for index, video in enumerate(video_data):
        width = video["width"]
        height = video["height"]

        if max_video_quality is not None:
            max_index, max_width, max_height = max_video_quality

            if width > max_width or height > max_height:
                max_video_quality = (index, width, height)

        else:
            max_video_quality = (index, width, height)

        video_qualities.append((index, width, height))

    for index, audio in enumerate(audio_data):
        bitrate = audio["bitrate"]

        if max_audio_quality is not None:
            max_index, max_bitrate = max_audio_quality

            if bitrate > max_bitrate:
                max_audio_quality = (index, bitrate)

        else:
            max_audio_quality = (index, bitrate)

        audio_qualities.append((index, bitrate))

    return (max_video_quality, max_audio_quality)


if __name__ == "__main__":
    _, master_url = sys.argv
    master_json = get_master_json(master_url)

    video_data = master_json["video"]
    audio_data = master_json["audio"]

    max_video_quality, max_audio_quality = select_quality(video_data, audio_data)

    video_data = master_json["video"][max_video_quality[0]]
    audio_data = master_json["audio"][max_audio_quality[0]]
    
    video_base_url = urljoin(urljoin(master_url, master_json["base_url"]), video_data["base_url"])
    audio_base_url = urljoin(urljoin(master_url, master_json["base_url"]), audio_data["base_url"])

    video_file_name = f"{master_json['clip_id']}.m4v"
    audio_file_name = f"{master_json['clip_id']}.m4a"

    video_thread = threading.Thread(target=process_file, args=["Video", video_base_url, video_data["init_segment"], video_data["segments"], video_file_name])
    audio_thread = threading.Thread(target=process_file, args=["Audio", audio_base_url, audio_data["init_segment"], audio_data["segments"], audio_file_name])

    video_thread.start()
    audio_thread.start()

    video_thread.join()
    audio_thread.join()

    print(">> Merging audio and video")
    os.system(f"mkvmerge -o downloaded.mkv {video_file_name} {audio_file_name}")
    
    print(">> Removing cached audio and video files")
    os.remove(video_file_name)
    os.remove(audio_file_name)

    print(">> Content Downloaded Successfully!")

