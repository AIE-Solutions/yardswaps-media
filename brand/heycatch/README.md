# HeyCatch backgrounds

Alan, 2026-11-26: "Heychat allows to setup own images". HeyCatch (app.heycatch.ai) makes three short posts a day
and lays its own caption over a background. Left alone it picks stock pictures and trending memes. In Videos,
the gear icon (Post settings), "Background images and videos", it takes our own files instead.

`plates/` holds what we load there: one real listing photo each, shown whole on white, the item named on the
one blue tag, the wordmark once (the post kit look, brand/posts/README.md). No headline, because HeyCatch
writes its own line on top. `make_plates.py SRC_DIR` rebuilds them from a folder of listing photos.

Rules: real listing photos only (no stock, AI or Canva pictures), no faces, plates or phone numbers, and no
price or "for sale" on a plate, because a queued post can go out weeks later, after the item has sold.

## What we learned loading them (2026-11-26)

- A slideshow slide is 4:5: HeyCatch shows the middle 1080 x 1350 of the plate. The plates keep the tag, the
  photo and the wordmark inside that window and leave a white band under the photo.
- Settings ("Only mine", remixes "Never") change new ideas only. Posts already queued and ideas already
  waiting in the deck keep their old pictures.
- An idea can be rebuilt by hand before it is approved: Edit, then per slide "Choose image" (our library,
  search by file name), double-click the caption to rewrite it, drag it into the white band under the photo,
  Preview, Save. Saving does not approve it.
- Rewrite HeyCatch's wording against MESSAGING.md before approving: it likes the category count, "free
  dealer storefront" and "post in 60 seconds", none of which we say.
- Only the slideshow format reads on a white plate. The other three formats use a person cutout or a video
  clip with thin outlined text.
- Free: swipes (20 a day), per-post edits, "Regenerate videos". Costs credits: the "+" for more ideas. Don't.
