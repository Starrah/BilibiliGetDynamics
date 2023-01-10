import asyncio
import json
import os
import sys
import argparse
import aiohttp
from bilibili_api import user

parser = argparse.ArgumentParser()
parser.add_argument('uid', nargs=1)
parser.add_argument('--no_download', action="store_true", help="同时下载动态中的图片")
parser.add_argument('--full_json', action="store_true", help="输出动态完整数据")
args = parser.parse_args()

if len(sys.argv) == 1:
    sys.stderr.write("请输入用户的UID作为参数！")
    exit(1)
u = user.User(uid=int(sys.argv[1]))


async def fetch(session: aiohttp.ClientSession, url: str, path: str):
    try:
        async with session.get(url) as resp:
            with open(path, 'wb') as fd:
                while 1:
                    chunk = await resp.content.read(1024)  # 每次获取1024字节
                    if not chunk:
                        break
                    fd.write(chunk)
        # print("downloaded " + url)
    except:
        print("failed " + url)


def copyKeys(src, keys):
    res = {}
    for k in keys:
        if k in src:
            res[k] = src[k]
    return res


def getItem(input):
    if "item" in input:
        return getItem(input["item"])
    if "videos" in input:
        return getVideoItem(input)
    else:
        return getNormal(input)


def getNormal(input):
    res = copyKeys(input, ['description', 'pictures', 'content'])
    if "pictures" in res:
        res["pictures"] = [pic["img_src"] for pic in res["pictures"]]
    return res


def getVideoItem(input):
    res = copyKeys(input, ['title', 'desc', 'dynamic', 'short_link', 'stat', 'tname'])
    res["av"] = input["aid"]
    res["pictures"] = [input["pic"]]
    return res


def cardToObj(input):
    res = {
        "dynamic_id": input["desc"]["dynamic_id"],
        "timestamp": input["desc"]["timestamp"],
        "type": input["desc"]["type"],
        "item": getItem(input["card"])
    }
    if "origin" in input["card"]:
        originObj = json.loads(input["card"]["origin"])
        res["origin"] = getItem(originObj)
        if "user" in originObj and "name" in originObj["user"]:
            res["origin_user"] = originObj["user"]["name"]
    return res


async def main():
    with open(f'{sys.argv[1]}-result.json', "w", encoding="UTF-8") as f:
        offset = 0
        count = 0
        if not args.no_download:
            os.makedirs("pics", exist_ok=True)
        while True:
            # if offset != 0:
            #     f.write(",")
            res = await u.get_dynamics(offset)
            if res["has_more"] != 1:
                break
            offset = res["next_offset"]
            for card in res["cards"]:
                f.write(",\n" if count > 0 else "[\n")
                cardObj = cardToObj(card)
                if not args.no_download:
                    tasks = []
                    async with aiohttp.ClientSession() as session:
                        if "pictures" in cardObj["item"]:
                            for pic_url in cardObj["item"]["pictures"]:
                                task = fetch(session, pic_url, os.path.join("pics", os.path.basename(pic_url)))
                                tasks.append(task)
                            await asyncio.gather(*tasks)
                if not args.full_json:
                    cardStr = json.dumps(card,ensure_ascii=False)
                else:
                    cardStr = json.dumps(cardObj,ensure_ascii=False)
                f.write(cardStr)
                print(cardStr)
                count += 1
            f.flush()
            await asyncio.sleep(1)
        f.write("\n]")
    print()
    print("--------已完成！---------")


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
