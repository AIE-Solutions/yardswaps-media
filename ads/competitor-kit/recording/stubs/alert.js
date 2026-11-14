// recording only: auto-press the confirming button so confirm dialogs complete on web
export default class Alert { static alert(t, m, btns) { const b = (btns || []).find((x) => x.style !== 'cancel' && x.onPress); if (b) setTimeout(b.onPress, 500); } }
