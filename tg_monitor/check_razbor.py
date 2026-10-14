# 14.10: проверка разбора помощников СКРИПТОМ, а не вторым агентом (vibecoding_community/245745, zeroshot):
# каждый пост пачки in_N.txt есть в out_N.json, JSON целый, у не-skip есть headline и for_us, у моды — radar.
# Запуск: python check_razbor.py <папка с in_*.txt и out_*.json>   → «совпало M из M» или список дыр; код выхода 1 при дырах.
import json, re, sys, glob, os

TREND = {"now_trends", "moda_po_sprosu", "odezhda_stil_moda", "shop_sekret", "shoppingfyou", "topoeva_olesya", "runtobuy",
         "svetlana_nechego_nadet", "moda_vtelege", "my_image_and_style", "valeri_bloc", "pro_reelss", "promty_by_irri",
         "photopingvin_ai", "BrandAnalytics", "thetrends_journal"}


def check(folder):
    holes, total = [], 0
    for fin in sorted(glob.glob(os.path.join(folder, "in_*.txt"))):
        n = re.search(r"in_(\d+)\.txt$", fin).group(1)
        keys = re.findall(r"^--- (\S+/\d+) ", open(fin, encoding="utf-8").read(), re.M)
        total += len(keys)
        fout = os.path.join(folder, f"out_{n}.json")
        try:
            out = json.load(open(fout, encoding="utf-8"))
        except Exception as e:
            holes.append(f"out_{n}.json: не читается ({e.__class__.__name__})")
            continue
        for k in keys:
            v = out.get(k)
            if v is None:
                holes.append(f"{k}: нет в out_{n}.json")
            elif v.get("cat") != "skip":
                if not v.get("headline") or not v.get("for_us"):
                    holes.append(f"{k}: нет headline/for_us")
                if k.split("/")[0] in TREND and v.get("cat") == "biz" and not v.get("radar"):
                    holes.append(f"{k}: модный пост без radar")
        if len(keys) and sum(1 for k in keys if out.get(k, {}).get("cat") == "skip") == len(keys):
            holes.append(f"out_{n}.json: ВСЁ skip — подозрительно, перепроверить пачку")
    return total, holes


if __name__ == "__main__":
    total, holes = check(sys.argv[1])
    print(f"совпало {total - len([h for h in holes if 'нет в' in h])} из {total}")
    for h in holes:
        print(" -", h)
    sys.exit(1 if holes else 0)
