import asyncio
import json
import sys

from bilibili_api import user

if len(sys.argv) == 1:
    sys.stderr.write("请输入用户的UID作为参数！")
    exit(1)
u = user.User(uid=int(sys.argv[1]))


def copyKeys(src, keys):
    res = {}
    for k in keys:
        if k in src:
            res[k] = src[k]
    return res


def getItem(input):
    res = copyKeys(input, ['description', 'pictures', 'content'])
    if "pictures" in res:
        res["pictures"] = [pic["img_src"] for pic in res["pictures"]]
    return res


def cardToObj(input):
    res = {
        "dynamic_id": input["desc"]["dynamic_id"],
        "timestamp": input["desc"]["timestamp"],
        "item": getItem(input["card"]["item"])
    }
    if "origin" in input["card"]:
        originObj = json.loads(input["card"]["origin"])
        res["origin"] = getItem(originObj["item"])
        if "user" in originObj and "name" in originObj["user"]:
            res["origin_user"] = originObj["user"]["name"]
    return res


async def main():
    with open("result.json", "w", encoding="UTF-8") as f:
        offset = 0
        count = 0
        while True:
            if offset != 0:
                f.write(",")
            res = await u.get_dynamics(offset)
            if res["has_more"] != 1:
                break
            offset = res["next_offset"]
            for card in res["cards"]:
                f.write(",\n" if count > 0 else "[\n")
                cardObj = cardToObj(card)
                cardStr = str(cardObj)
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
