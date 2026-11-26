# Stories with a tappable link

Alan 2026-11-26: "Other companies add links to their post", "but a working link", then
"the open your storefront ... then list your items link, search for new items link", and
"we need storefronts and sellers to post first to increase our inventory".

The Graph API cannot add a link sticker to a Story, so these are scheduled by hand in
Meta Business Suite (Story composer, Edit, Stickers, Link). `schedule.json` is the week:
date, Central time, audience, image, sticker text and the link for each platform.

- Three kinds, each with its own link: seller ("list your items", /sell-equipment),
  storefront ("open your storefront", /dealers?offer=founding) and buyer ("search new
  items", the home page). Sellers and storefronts lead; buyers get one or two a week.
- Look: storefront Stories use the post kit, white and blue (brand/posts/README.md).
  Seller Stories use the card look Alan approved for stills ("These images are super
  nice", 11-26): `seller-card-<slug>.jpg`, one real listing photo on top with a blue
  label, the light panel with the slate title and one blue "Free to list" line, and an
  empty band centred near y 1425 where the white "LIST YOURS FREE" sticker goes.
  The seven seller Stories for Nov 27 to Dec 3 were swapped to this look on 11-26 (the
  earlier-look Stories were removed from Business Suite; `earlier_image` keeps their
  files). Real listing photos only. Nothing to read in the top 200 px or the bottom
  340 px.
- Rotation (Alan 11-26, "we need to be ... rotating items we are showing over time, not
  just the same ones"): each new week of seller Stories uses listings not shown in a
  seller Story in the two weeks before, spread across item types.
- Dealers never read "list it free": storefront Stories carry the storefront offer.
- Before a week is scheduled, check that every listing and storefront shown is still live.
