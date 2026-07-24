import asyncio
import json

from shazamio import Shazam


FILES = [
    "/private/tmp/song_snip_30.wav",
    "/private/tmp/song_snip_120.wav",
    "/private/tmp/song_snip_240.wav",
]


async def main():
    shazam = Shazam()
    for path in FILES:
        try:
            result = await shazam.recognize(path)
            track = result.get("track") or {}
            print(
                json.dumps(
                    {
                        "file": path,
                        "title": track.get("title"),
                        "subtitle": track.get("subtitle"),
                        "url": track.get("url"),
                        "key": track.get("key"),
                        "isrc": track.get("isrc"),
                    },
                    ensure_ascii=False,
                )
            )
        except Exception as exc:
            print(json.dumps({"file": path, "error": str(exc)}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
