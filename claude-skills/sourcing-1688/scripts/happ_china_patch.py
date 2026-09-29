"""Накладка правил «китайские сайты напрямую» на СВЕЖИЙ сервер из подписки Happ.

Зачем: подписка «Обходы4» часто меняет серверы, а наш сервер «1688 + Pinduoduo напрямую»
был копией старого. Скрипт берёт любой свежий конфиг и добавляет к нему только наши правила,
сами серверы (адреса, ключи) не трогает.

Как пользоваться:
  1. В Happ: правый клик (или «⋮») по нужному серверу подписки → «Копировать конфиг / Поделиться → JSON».
  2. python happ_china_patch.py            — возьмёт JSON из буфера, допишет правила, положит обратно в буфер
     python happ_china_patch.py file.json  — то же из файла
  3. В Happ: «+» → «Импорт из буфера обмена» → появится сервер «… | 1688+PDD+17 напрямую».
"""
import json, subprocess, sys, time, datetime, pathlib

DIRECT_DOMAINS = [
    # 1688 / Alibaba / Taobao
    "1688.com", "alicdn.com", "mmstat.com", "taobao.com", "tbcdn.cn", "alibaba.com", "alipay.com",
    "aliyuncs.com", "alibabausercontent.com", "alibaba-inc.com", "tmall.com", "dingtalk.com",
    # Pinduoduo (pdd.net — антибот-проверка, без неё нет товаров)
    "pinduoduo.com", "yangkeduo.com", "pddpic.com", "pddugc.com", "pinduoduo.net", "pdd.net",
    "pinduoduo.cn", "yangkeduo.cn", "pddglobalhk.com", "hutaojie.com",
    # Оптовые рынки одежды, Baidu, 妙手ERP (28.09: 17zwd через VPN грузился плохо / обрывался)
    "17zwd.com", "17.shop", "vvic.com", "baidu.com", "bdimg.com", "bdstatic.com", "91miaoshou.com",
]
# Картинки PDD: у img-4.pddpic.com 2 адреса; 14.0.37.180 отвечает за 0,2 с, 148.253.245.44 — 25 с/таймаут
# напрямую (проверено 27.09). Быстрый закрепляем, медленный пускаем через VPN.
# Замерять из скрипта нельзя: при включённом Happ всё идёт через его VPN-адаптер.
PDD_IMG_HOST, PDD_IMG_FAST, PDD_IMG_SLOW = "img-4.pddpic.com", "14.0.37.180", ["148.253.245.44"]
OUT = pathlib.Path(__file__).with_name("happ_china_latest.json")


def read_clipboard():
    return subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
                          capture_output=True, text=True, encoding="utf-8").stdout


def write_clipboard(text):
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "[Console]::InputEncoding=[Text.Encoding]::UTF8; $input | Set-Clipboard"],
                   input=text, text=True, encoding="utf-8")


def patch(cfg):
    if isinstance(cfg, list):          # подписка целиком — берём первый сервер
        cfg = cfg[0]
    routing = cfg.setdefault("routing", {})
    rules = routing.setdefault("rules", [])
    # убираем нашу прошлую накладку, если конфиг уже был пропатчен
    ours = {f"domain:{d}" for d in DIRECT_DOMAINS} | {f"{ip}/32" for ip in PDD_IMG_SLOW}
    rules[:] = [r for r in rules if not (set(r.get("domain", [])) | set(r.get("ip", []))) & ours]
    china = {"type": "field", "domain": [f"domain:{d}" for d in DIRECT_DOMAINS], "outboundTag": "direct"}

    # куда идёт «всё остальное» (VPN): балансировщик или outbound
    last = next((r for r in reversed(rules) if "domain" not in r and "ip" not in r and "protocol" not in r), None)
    vpn = {"balancerTag": last["balancerTag"]} if last and "balancerTag" in last else {
        "outboundTag": (last or {}).get("outboundTag") or next(
            o["tag"] for o in cfg["outbounds"] if o.get("protocol") not in ("freedom", "blackhole", "dns"))}

    # outbound direct должен существовать
    if not any(o.get("tag") == "direct" for o in cfg["outbounds"]):
        cfg["outbounds"].append({"protocol": "freedom", "tag": "direct"})

    cfg.setdefault("dns", {}).setdefault("hosts", {})[PDD_IMG_HOST] = PDD_IMG_FAST
    head = [{"type": "field", "ip": [f"{ip}/32" for ip in PDD_IMG_SLOW], **vpn}, china]
    # наши правила — в самое начало, чтобы их не перебили правила подписки
    rules[0:0] = head
    routing.setdefault("domainStrategy", "AsIs")

    stamp = datetime.date.today().strftime("%d.%m")
    base = (cfg.get("remarks") or "сервер").split(" | 1688")[0]
    cfg["remarks"] = f"{base} | 1688+PDD+17 напрямую {stamp}"
    return cfg


def main():
    raw = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else read_clipboard()
    try:
        cfg = json.loads(raw)
    except Exception:
        sys.exit("В буфере не JSON-конфиг. В Happ скопируйте сервер именно как JSON (не ссылку vless://).")
    cfg = patch(cfg)
    text = json.dumps(cfg, ensure_ascii=False, indent=2)
    OUT.write_text(text, encoding="utf-8")
    write_clipboard(text)
    print(f"\nГотово: «{cfg['remarks']}»\nСохранено в {OUT}\nКонфиг уже в буфере — в Happ нажмите «+» → импорт из буфера.")


if __name__ == "__main__":
    main()
