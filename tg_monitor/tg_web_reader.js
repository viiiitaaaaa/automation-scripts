// Reads channels through Telegram Web K (web.telegram.org/k, user is logged in) via its own API client:
// sees posts that t.me/s hides ("Please open Telegram") and channels with web preview turned off.
// Only channel histories are requested; private chats are never opened.
// Usage in the Telegram Web tab (claude-in-chrome javascript_tool), with tg_web_import.py --serve running:
//   paste this file, then  tgWebSync([["vibecoding_tg", 3890], ["anita_bold", 0]], 31)
//   -> posts with id >= minId and not older than `days` are POSTed to http://127.0.0.1:8765
function richText(node) {
  // rich_message = blocks like Instant View pages; every leaf string sits under a "text" key
  const out = [];
  const walk = (v, key) => {
    if (typeof v === "string") { if (key === "text" || key === "url") out.push(key === "url" ? " " + v : v); return; }
    if (Array.isArray(v)) { v.forEach(x => walk(x, key)); return; }
    if (v && typeof v === "object") {
      for (const [k, x] of Object.entries(v)) if (k !== "_" && k !== "pFlags") walk(x, k === "text" || k === "url" ? k : key === "text" ? "text" : k);
      if (/^pageBlock/.test(v._ || "")) out.push("\n");
    }
  };
  walk(node, "");
  return out.join("").replace(/\n{3,}/g, "\n\n").trim();
}

function mediaLabel(media) {
  // posts without text that t.me/s hides: quizzes and round video messages — name them instead of leaving them blank
  if (!media) return "";
  if (media._ === "messageMediaPoll") return "[Опрос] " + (media.poll.question.text || media.poll.question);
  if (media.pFlags?.round || media.document?.pFlags?.round) return "[Видеокружок — смотреть в приложении]";
  const kind = {messageMediaPhoto: "Фото", messageMediaDocument: "Видео/файл"}[media._] || media._;
  return `[${kind} без подписи — смотреть в приложении]`;
}

async function readChannel(username, minId, days) {
  const m = rootScope.managers;
  const peer = await m.appUsersManager.resolveUsername(username);
  if (!peer || !peer.id) return {username, error: "not found"};
  const inputPeer = await m.appChatsManager.getChannelInputPeer(peer.id);
  const since = Date.now() / 1000 - days * 86400;
  const posts = [];
  let offset = 0;
  for (let page = 0; page < 60; page++) {  // 29.09: exhaustive — whole window, not 1000 posts
    const res = await m.apiManager.invokeApi("messages.getHistory",
      {peer: inputPeer, offset_id: offset, offset_date: 0, add_offset: 0, limit: 100, max_id: 0, min_id: 0, hash: 0});
    const msgs = (res.messages || []).filter(x => x._ === "message");
    if (!msgs.length) break;
    for (const x of msgs) {
      if (x.id < minId || x.date < since) continue;
      if (!x.message && x.grouped_id) continue;  // album part: the caption is on another photo of the album
      const text = x.message || (x.rich_message ? richText(x.rich_message) : "") || mediaLabel(x.media);
      posts.push({channel: username, id: x.id, date: new Date(x.date * 1000).toISOString(), text,
                  media: x.media ? x.media._ : ""});
    }
    const last = msgs[msgs.length - 1];
    if (last.id <= minId || last.date < since) break;
    offset = last.id;
    await new Promise(r => setTimeout(r, 800));
  }
  return {username, posts};
}

async function tgWebSync(list, days = 31) {
  const report = [];
  const all = [];
  for (const [u, minId] of list) {
    try {
      const r = await readChannel(u, minId, days);
      if (r.error) { report.push(u + ": " + r.error); continue; }
      all.push(...r.posts);
      report.push(u + ": " + r.posts.length);
    } catch (e) { report.push(u + ": ошибка " + e); }
  }
  const resp = await fetch("http://127.0.0.1:8765/import", {method: "POST", body: JSON.stringify(all)});
  report.push("база: " + await resp.text());
  return report;
}

// Group chats (shopify_chat): messages of the last `days` days with the id of the message each one answers.
// Author = first name only. -> POST http://127.0.0.1:8765/chat
// minId: stop at an already stored message (incremental); offsetId: start below this id (backfill older history)
async function readChat(username, days = 45, minId = 0, offsetId = 0) {
  const m = rootScope.managers;
  const peer = await m.appUsersManager.resolveUsername(username);
  const inputPeer = await m.appChatsManager.getChannelInputPeer(peer.id);
  const since = Date.now() / 1000 - days * 86400;
  const out = [];
  let offset = offsetId;
  for (let page = 0; page < 1000; page++) {
    const res = await m.apiManager.invokeApi("messages.getHistory",
      {peer: inputPeer, offset_id: offset, offset_date: 0, add_offset: 0, limit: 100, max_id: 0, min_id: 0, hash: 0});
    const users = Object.fromEntries((res.users || []).map(u => [String(u.id), u.first_name || ""]));
    const msgs = (res.messages || []).filter(x => x._ === "message");
    if (!msgs.length) break;
    for (const x of msgs) {
      if (x.date < since) continue;
      out.push({chat: username, id: x.id, date: new Date(x.date * 1000).toISOString(), text: x.message || mediaLabel(x.media),
                reply_to: x.reply_to?.reply_to_msg_id || null, author: users[String(x.from_id?.user_id)] || ""});
    }
    const last = msgs[msgs.length - 1];
    if (last.date < since || (minId && last.id <= minId)) break;
    offset = last.id;
    await new Promise(r => setTimeout(r, 900));
  }
  const resp = await fetch("http://127.0.0.1:8765/chat", {method: "POST", body: JSON.stringify(out)});
  return [out.length + " сообщений", await resp.text()];
}
