import json
import numpy as np
import re
import requests
import pickle

rune_size = [60, 50]
img_cache = None

GET_IMAGE = True
USE_IMG_CACHE = True  # 使用图片url缓存，不用从prts查文件url
ADD_CSS = False

mn = "crisis_v2_01-01"  # 维多利亚 灰烬泽地
# mn = "crisis_v2_01-02"  # 大炎 设防关隘
# mn = "crisis_v2_01-03"  # 哥伦比亚 联邦监狱
# mn = "crisis_v2_01-05"  # 玻利瓦尔 翻修中沙滩
# mn = "crisis_v2_01-07"  # 切尔诺伯格 13区废墟

# 奖励图片，需要手动设置
reward_imgs = {
    "char_131_flameb@whirlwind#6": r'<div style="display: inline-block; position: relative; width: 120px; height: 120px;"><div><a href="https://prts.wiki/w/%E7%82%8E%E5%AE%A2" title="炎客"><img alt="Skin框.png" src="https://prts.wiki/images/thumb/0/05/Skin%E6%A1%86.png/120px-Skin%E6%A1%86.png" decoding="async" width="120" height="119" data-src="https://prts.wiki/images/thumb/0/05/Skin%E6%A1%86.png/120px-Skin%E6%A1%86.png" class=" lazyloaded" data-srcset="https://prts.wiki/images/0/05/Skin%E6%A1%86.png 1.5x" srcset="https://prts.wiki/images/0/05/Skin%E6%A1%86.png 1.5x"></a></div><div style="position: absolute; top: 21px; left: 26px;"><a href="https://prts.wiki/w/%E7%82%8E%E5%AE%A2" title="炎客"><img alt="头像 炎客 skin2.png" src="https://prts.wiki/images/thumb/9/96/%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png/67px-%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png" decoding="async" width="67" height="67" data-src="https://prts.wiki/images/thumb/9/96/%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png/67px-%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png" class=" lazyloaded" data-srcset="https://prts.wiki/images/thumb/9/96/%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png/101px-%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png 1.5x, https://prts.wiki/images/thumb/9/96/%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png/134px-%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png 2x" srcset="https://prts.wiki/images/thumb/9/96/%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png/101px-%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png 1.5x, https://prts.wiki/images/thumb/9/96/%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png/134px-%E5%A4%B4%E5%83%8F_%E7%82%8E%E5%AE%A2_skin2.png 2x"></a></div></div>',
    "itempack_mod_4": r'<div style="display:inline-block;position:relative"><a href="https://prts.wiki/w/%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97" title="模组数据整合块"><img alt="道具 带框 模组数据整合块.png" src="https://prts.wiki/images/thumb/e/e4/%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png/120px-%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png" decoding="async" width="120" height="120" data-src="https://prts.wiki/images/thumb/e/e4/%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png/120px-%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png" class=" ls-is-cached lazyloaded" data-srcset="https://prts.wiki/images/thumb/e/e4/%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png/180px-%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png 1.5x, /images/e/e4/%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png 2x" srcset="https://prts.wiki/images/thumb/e/e4/%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png/180px-%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png 1.5x, /images/e/e4/%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E6%95%B4%E5%90%88%E5%9D%97.png 2x"></a></div>',
    "furni_contract2_s1_01": r'<div style="display:inline-block;position:relative"><span class="mc-tooltips"><span style="display:inline-block;"><span><a href="https://prts.wiki/w/浊燃之旗" title="浊燃之旗"><span style="display:inline-block;position:relative;"><img class=" ls-is-cached lazyloaded" data-src="https://prts.wiki/images/3/3a/%E5%AE%B6%E5%85%B7_%E8%83%8C%E6%99%AF_R2.png" style="min-width:0% !important;" width="120px" src="https://prts.wiki/images/3/3a/%E5%AE%B6%E5%85%B7_%E8%83%8C%E6%99%AF_R2.png"><img class=" ls-is-cached lazyloaded" data-src="https://prts.wiki/images/0/01/%E5%AE%B6%E5%85%B7_%E6%B5%8A%E7%87%83%E4%B9%8B%E6%97%97.png" style="position:absolute;left:8%;top:17.3%;width:84%;min-width:0% !important;" src="https://prts.wiki/images/0/01/%E5%AE%B6%E5%85%B7_%E6%B5%8A%E7%87%83%E4%B9%8B%E6%97%97.png"></span></a></span></span></span></div>',
}


def html_escape(s):
    return s.replace("<", "&lt;").replace(">", "&gt;")


def plot_svg(pos):
    s = f"M{int(pos[0][0])} {int(-pos[0][1])}"
    n = len(pos)
    for i in range(1, n - 1):
        dir1 = np.array(pos[i - 1]) - np.array(pos[i])
        dir1 = dir1 / np.linalg.norm(dir1)
        dir2 = np.array(pos[i + 1]) - np.array(pos[i])
        dir2 = dir2 / np.linalg.norm(dir2)
        q = np.array(pos[i])
        p1 = q + 24 * dir1
        p2 = q + 24 * dir2
        s += f"L{int(p1[0])} {int(-p1[1])} S{int(q[0])} {int(-q[1])} {int(p2[0])} {int(-p2[1])}"
    s += f"L{int(pos[-1][0])} {int(-pos[-1][1])}"
    s = f'<path d="{s}" style="fill:none;stroke:#c42b3a;stroke-width:5;"/>'
    for i in [0, -1]:
        s += f'<circle cx="{int(pos[i][0])}" cy="{int(-pos[i][1])}" r="5" style="stroke:#c42b3a;fill:rgb(255,255,255);stroke-width:5" />'
    s += "\n"
    return s


def plot_svg2(pos, conor_r=14, circle_r=2):
    s = f"M{int(pos[0][0])} {int(-pos[0][1])}"
    n = len(pos)
    for i in range(1, n - 1):
        dir1 = np.array(pos[i - 1]) - np.array(pos[i])
        dir1 = dir1 / np.linalg.norm(dir1)
        dir2 = np.array(pos[i + 1]) - np.array(pos[i])
        dir2 = dir2 / np.linalg.norm(dir2)
        q = np.array(pos[i])
        p1 = q + conor_r * dir1
        p2 = q + conor_r * dir2
        s += f"L{int(p1[0])} {int(-p1[1])} S{int(q[0])} {int(-q[1])} {int(p2[0])} {int(-p2[1])}"
    s += f"L{int(pos[-1][0])} {int(-pos[-1][1])}"
    s = f'<path d="{s}" style="fill:none;stroke:#c42b3a;stroke-width:5;"/>'
    for i in [0, -1]:
        s += f'<circle cx="{int(pos[i][0])}" cy="{int(-pos[i][1])}" r="{circle_r}" style="stroke:#c42b3a;fill:rgb(255,255,255);stroke-width:5" />'
    s += "\n"
    return s


def exclusion_svg(pos, si):
    return f'<rect x="{int(pos[0] - si[0] / 2)}" y="{int(-pos[1] - si[1] / 2)}" width="{int(si[0])}" height="{int(si[1])}" rx="10" style="fill:none;stroke:#cccccc;stroke-width:5;" />\n'


def node_normal(pos, score, name, des, bgpos):
    name = html_escape(name)
    des = html_escape(des)

    s = f'<div style="position:absolute;left:{int(pos[0])}px;top:{int(-pos[1])}px;">'
    s += '<div class="normal_warp">'
    s += f'<div class="node_r1"><div class="node_sp" style="width:{int(bgpos[2])}px;height:{int(bgpos[3])}px;left:{int((50 - bgpos[2]) / 2)}px;top:{int((50 - bgpos[3]) / 2)}px;background-position-x:{int(-bgpos[0])}px;background-position-y:{int(-1024 + bgpos[3] + bgpos[1])}px;"></div></div>'
    s += f'<div class="node_r2_score"><svg><polygon class="score_level" points="8,3 3,13 13,13"></polygon></svg>{score}</div>'
    s += '<div class="text_warp">'
    s += f'<div class="a">{name}</div>'
    s += f'<div class="b">{des}</div>'
    s += "</div></div></div>\n"
    return s


def node_normal2(pos, score, name, des, img, si):
    name = html_escape(name)
    des = html_escape(des)

    s = f"""<div style="position:absolute;left:{int(pos[0])}px;top:{int(-pos[1])}px;">
            <div class="normal_warp">
                <div class="node_r1 mc-tooltips">
                    <div class="node_sp"
                    style="width:{si[0]}px;height:{si[1]}px;left:{int((rune_size[0] - si[0]) / 2)}px;top:{int((rune_size[1] - si[1]) / 2)}px;background-image:url({img});">
                    </div>
                    <div style="display:none" data-size="350" data-trigger="mouseenter focus">
                        <div class="a" style="color:#d32f2f;"><b>{name}</b></div>
                        <div class="b">{des}</div>
                    </div>
                </div>
                <div class="node_r2_score"><svg>
                        <polygon class="score_level" points="8,3 3,13 13,13"></polygon>
                    </svg>{score}</div>
            </div>
        </div>"""

    return s


def node_bag(pos, score, name, des, img, si, size_bag):
    name = html_escape(name)
    des = html_escape(des)

    s = f"""<div style="position:absolute;left:{int(pos[0])}px;top:{int(-pos[1])}px;">
            <div class="normal_warp">
                <div class="node_bag mc-tooltips" style="width:{size_bag['x']}px">
                    <div style="height: 100%;">
                        <div class="node_sp"
                        style="width:{si[0]}px;height:{si[1]}px;left:{int((rune_size[0] - si[0]) / 2)}px;top:{int((rune_size[1] - si[1]) / 2)}px;background-image:url({img});">
                        </div>
                        <div class="bag_name">{name.replace("指标集：", "")}</div>
                    </div>
                    <div style="display:none" data-size="350" data-trigger="mouseenter focus">
                        <div class="a" style="color:#d32f2f;"><b>{name}</b></div>
                        <div class="b">{des}</div>
                    </div>
                </div>
                <div class="node_r2_score" style="width: 100%; padding-right: 0; justify-content: unset;"><svg style="width: 40px;">
                        <polygon class="score_level" points="8,3 3,13 13,13"></polygon>
                    </svg>{score}</div>
            </div>
        </div>"""

    return s


def node_treasure_default(pos, si, subti, ti, name, des):
    subti = html_escape(subti)
    ti = html_escape(ti)

    s = f"""<div style="position:absolute;left:{int(pos[0])}px;top:{int(-pos[1])}px;">
        <div class="normal_warp node_reward mc-tooltips" style="left:{int(-si / 2)}px;top:{int(-si / 2)}px;">
            <div>
                <div class="node_r1_ mdi mdi-hexagon-slice-2 mdi-rotate-180" style="color: black;text-shadow: 0 0 6px #ffffffba;font-size: 110px;text-align: center;"></div>
                <div class="node_r2_" style="width:{int(si - 4)}px;">
                    <div class="a">{ti}</div>
                    <div class="b">{subti}</div>
                </div>
            </div>
            <div style="display:none" data-size="350" data-trigger="mouseenter focus">
                <div class="a" style="color:#d32f2f;"><b>晶块陈列室：{name}</b></div>
                <div class="b">{des}</div>
            </div>
        </div>
    </div>
    """
    return s


def node_treasure(pos, si, subti, ti, name, des, img=""):
    subti = html_escape(subti)
    ti = html_escape(ti)

    s = f"""<div style="position:absolute;left:{int(pos[0])}px;top:{int(-pos[1])}px;">
        <div class="treasure_warp node_reward mc-tooltips" style="left:{int(-si / 2)}px;top:{int(-si / 2)}px;">
            <div>
                <div class="node_r1_" style="width:{int(si)}px;height:{int(si)}px;">{img}</div>
                <div class="node_r2_" style="width:{int(si - 4)}px;">
                    <div class="a">{ti}</div>
                    <div class="b">{subti}</div>
                </div>
            </div>
            <div style="display:none" data-size="350" data-trigger="mouseenter focus">
                <div class="a" style="color:#d32f2f;"><b>晶块陈列室：{name}</b></div>
                <div class="b">{des}</div>
            </div>
        </div>
    </div>
    """
    return s


def pickle_write(path, data):
    with open(path, "wb") as f:
        pickle.dump(data, f)
    return True


def pickle_read(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data


def save_img_cache():
    global img_cache
    path = "img_cache.pickle"
    if img_cache is None:
        img_cache = {}
    pickle_write(path, img_cache)
    return img_cache


def load_img_cache():
    global img_cache
    path = "img_cache.pickle"
    try:
        img_cache = pickle_read(path)
    except Exception as e:
        print(e)
        save_img_cache()
    return img_cache


def save_img_to_cache(img, format="png", data={}):
    global img_cache
    if img_cache is None:
        load_img_cache()

    img_cache[f"{img}.{format}"] = data
    save_img_cache()

    return img_cache


def get_img_from_cache(img, format="png"):
    global img_cache
    if img_cache is None:
        load_img_cache()

    rtn = img_cache.get(f"{img}.{format}")

    return rtn


def get_img_from_prts(img, format="png"):
    S = requests.Session()

    URL = "https://prts.wiki/api.php"

    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": f"File:{img}.{format}",
        "prop": "imageinfo",
        "iiprop": "url|size",
    }

    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()

    print(DATA)
    print("--------")
    pages = DATA["query"]["pages"]
    for id, page in pages.items():
        url = page["imageinfo"][0]["url"]
        width = page["imageinfo"][0]["width"]
        height = page["imageinfo"][0]["height"]

        break

    rtn = {"url": url, "width": width, "height": height}

    return rtn


def get_img(img, format="png"):
    if USE_IMG_CACHE:
        rtn = get_img_from_cache(img, format)
        if rtn is not None:
            print("cache", rtn)
            return rtn

    rtn = get_img_from_prts(img, format)
    save_img_to_cache(img, format, data=rtn)
    print("prts", rtn)

    return rtn


# 关键节点
def node_reward(pos, name, des):
    s = f"""<div style="position:absolute;left:{int(pos[0])}px;top:{int(-pos[1])}px;">
            <div class="reward_warp mc-tooltips">
                <div style="height: 100%;"></div>
                <div style="display:none" data-size="350" data-trigger="mouseenter focus">
                    <div class="a" style="color:#d32f2f;"><b>阵眼任务：{name}</b></div>
                    <div class="b">{des}</div>
                </div>
            </div>
        </div>
    """
    return s


def fileread(name):
    with open(name, "r", encoding="utf-8") as f:
        return f.read()


def get_description_keys(str):
    blocks = re.findall(r"{.*?}", str)
    # print(blocks)
    keys = []
    for block in blocks:
        key = block[1:-1]
        if ":" in key:
            key = re.findall(r".*:", key)[0][:-1]

        if key[0] == "-":
            key = key[1:]
        keys.append(key)
        # print(key)
    print(keys)
    return blocks, keys


def get_keys_num(runeData, key):
    runes = runeData["packedRune"]["runes"]
    for rune in runes:
        blackboard = rune["blackboard"]
        for bb in blackboard:
            bb_key = bb["key"]
            if bb_key == key:
                return bb["value"]
    return "?"


def decode_description(runeData):
    packedRune = runeData["packedRune"]
    description = packedRune["description"]

    print(description)

    # description = description.replace(r"<@crisisv2.nag>", "")
    description = description.replace(r"</>", "")
    description = re.sub(r"<@.*?>", "", description)
    blocks, keys = get_description_keys(description)

    nums = []
    for key in keys:
        num = get_keys_num(runeData, key)
        nums.append(num)

    for i in range(len(blocks)):
        block = blocks[i]
        num = nums[i]

        if block[1] == "-":
            num = -num

        if r"%" in block:
            num = num * 100
            num = round(num, 5)
            num = str(num)
            if "." in num:
                num = re.sub(r"0+$", "", num)
            if num[-1] == ".":
                num = num[:-1]
            num = num + "%"

        nums[i] = num

    for i in range(len(blocks)):
        block = blocks[i]
        num = str(nums[i])
        description = description.replace(block, num)

    return description


file = json.loads(fileread("crisis_info.json"))

mapDetailDataMap = file["info"]["mapDetailDataMap"]


svgstr = ""
domstr = ""

nodeViewData = mapDetailDataMap[mn]["nodeViewData"]
nodeDataMap = mapDetailDataMap[mn]["nodeDataMap"]
runeDataMap = mapDetailDataMap[mn]["runeDataMap"]
# roadRelationDataMap=mapDetailDataMap[mn]['roadRelationDataMap']
bagDataMap = mapDetailDataMap[mn]["bagDataMap"]
rewardNodeDataMap = mapDetailDataMap[mn]["rewardNodeDataMap"]
challengeNodeDataMap = mapDetailDataMap[mn]["challengeNodeDataMap"]

nodePosMap = nodeViewData["nodePosMap"]
roadPosMap = nodeViewData["roadPosMap"]
exclusionDataMap = nodeViewData["exclusionDataMap"]
bagPosMap = nodeViewData["bagPosMap"]

# 互斥合约的框
for na, r in exclusionDataMap.items():
    svgstr += exclusion_svg(
        [r["pos"]["x"], r["pos"]["y"]], [r["size"]["x"], r["size"]["y"]]
    )

# 指标集的框
if bagPosMap is not None:
    for na, r in bagPosMap.items():
        svgstr += exclusion_svg(
            [r["pos"]["x"], r["pos"]["y"] + 5], [r["size"]["x"], r["size"]["y"]]
        )

# 连线
for na, r in roadPosMap.items():
    corner = r["inflectionList"]
    pos = [[r["startPos"]["x"], r["startPos"]["y"]]]
    for j in range(len(corner)):
        c_ = corner[j]
        pos.append([c_["cornerPos"]["x"], c_["cornerPos"]["y"]])
    pos.append([r["endPos"]["x"], r["endPos"]["y"]])
    pos = np.array(pos) + np.array([r["centerPos"]["x"], r["centerPos"]["y"]])
    svgstr += plot_svg2(pos)

# 指标集说明
for bag, bag_item in bagDataMap.items():
    r = bagPosMap[bag]
    pos = [
        int(r["pos"]["x"] - r["size"]["x"] / 2 + rune_size[0] / 2),
        int(r["pos"]["y"] + r["size"]["y"] / 2 - rune_size[1] / 2),
    ]
    slotPackFullName = bag_item["slotPackFullName"]
    slotPackName = bag_item["slotPackName"]
    rewardScore = bag_item["rewardScore"]
    dimension = bag_item["dimension"]
    previewTitle = bag_item["previewTitle"]

    url = "https://prts.wiki/images/2/2c/G_enemy_atk_2.png"
    si = [50, 46]
    if GET_IMAGE:
        img = get_img("cc_battleplan_dim_%d" % (dimension if rewardScore > 0 else -1))
        url = img["url"]
        si = [img["width"], img["height"]]
    # icon=f'评分图标_{slotPackName}'
    # print(icon)
    # img=get_img(icon)
    # url=img['url']
    # si=[img['width'],img['height']]

    domstr += node_bag(
        pos, rewardScore, slotPackFullName, previewTitle, url, si, r["size"]
    )


# 合约
for node, node_item in nodeDataMap.items():
    position = nodePosMap[node]["position"]
    pos = [position["x"], position["y"]]
    runeId = node_item["runeId"]
    nodeType = node_item["nodeType"]
    print(node, nodeType, "/" + str(runeId) + "/", pos)

    if nodeType == "NORMAL":
        runeData = runeDataMap[runeId]
        # print(runeData)
        runeName = runeData["runeName"]
        runeIcon = runeData["runeIcon"]
        score = runeData["score"]

        packedRune = runeData["packedRune"]
        description = packedRune["description"]

        description = decode_description(runeData)

        print(runeName, score, runeIcon)
        print(description)

        url = "https://prts.wiki/images/2/2c/G_enemy_atk_2.png"
        si = [50, 46]
        if GET_IMAGE:
            img = get_img(runeIcon)
            url = img["url"]
            si = [img["width"], img["height"]]

        domstr += node_normal2(pos, score, runeName, description, url, si)
    elif nodeType == "START":
        svgstr += plot_svg([pos])
    elif nodeType == "KEYPOINT":
        keypointData = challengeNodeDataMap[node]
        challengeName = keypointData["previewTitle"]
        description = keypointData["previewDesc"]
        domstr += node_reward(pos, challengeName, description)
    elif nodeType == "TREASURE":
        rewards = rewardNodeDataMap[node]
        previewTitle = rewards["previewTitle"]
        previewDesc = rewards["previewDesc"]
        reward = rewards["reward"]["id"]
        requestBagCnt = str(rewards["requestBagCnt"])

        print("!!!---------------------------")
        print(reward)

        img = reward_imgs.get(reward)

        subti = f"{requestBagCnt}/{requestBagCnt} 已领取"
        if img is not None:
            domstr += node_treasure(
                pos, 120, subti, "REWARDS", previewTitle, previewDesc, img
            )
        else:
            domstr += node_treasure_default(
                pos, 120, subti, "REWARDS", previewTitle, previewDesc
            )

    else:
        print("------------------------")
        domstr += node_normal2(
            pos,
            node,
            node,
            "description",
            "https://prts.wiki/images/d/d6/G_enemy_hp_1.png",
            [46, 46],
        )

# 画布大小
w = nodeViewData["width"]
h = nodeViewData["height"]
print(w, h)
allstr = ""
if ADD_CSS:
    allstr += f'{fileread("crisis_v2_season_1_1_css.html")}'  # CSS
allstr += f"<style>.act38_map_main{{width:{int(w)}px;height:{int(h)}px;}}.skin-minerva .act38_map_main{{width:{int(w/4)}px;height:{int(h/4)}px;transform-origin: left top;transform:scale(0.25);}}</style>\n"
allstr += f'<div class="act38_map_main"><div style="position:absolute;"><svg width="{int(w)}px" height="{int(h)}px">\n'
allstr = allstr + svgstr
allstr += "</svg>\n"
allstr += domstr
allstr += "</div></div>\n"
f = open(f"{mn}.html", "w", encoding="utf-8")
f.write(allstr)
