# HeyCatch backgrounds

Alan, 2026-11-26: "Heychat allows to setup own images". HeyCatch (app.heycatch.ai) makes three short posts a day
and lays its own caption over a background. Left alone it picks stock pictures and trending memes. In Videos,
the gear icon (Post settings), "Background images and videos", it takes our own files instead.

`plates/` holds what we load there: one real listing photo each, shown whole on white, the item named on the
one blue tag, the wordmark once (the post kit look, brand/posts/README.md). No headline, because HeyCatch
writes its own line on top. `make_plates.py SRC_DIR` rebuilds them from a folder of listing photos.

Rules: real listing photos only (no stock, AI or Canva pictures), no faces, plates or phone numbers, and no
price or "for sale" on a plate, because a queued post can go out weeks later, after the item has sold.
