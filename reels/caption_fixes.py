"""Apply the one-off caption corrections in reels/caption_fixes.json to Reels
already published on the YardSwaps Facebook Page.

Each fix replaces its exact `find` text in the live description with `replace`.
A fix whose `find` text is no longer in the description is skipped, so the
script can run again safely. Nothing else on the post changes.

  META_PAGE_TOKEN  Page access token (secret, never printed)
  DRY_RUN          1 = only print what would change
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_reels import graph, GraphError  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    dry = os.environ.get("DRY_RUN", "0") == "1"
    with open(os.path.join(ROOT, "reels", "caption_fixes.json"), encoding="utf-8") as f:
        fixes = json.load(f)["fixes"]
    if not token:
        print("::notice::META_PAGE_TOKEN is not set, nothing changed.")
        return 0
    failed = 0
    for fx in fixes:
        if fx.get("platform") != "facebook":
            print(f"skip {fx.get('id')}: only Facebook captions can be edited")
            continue
        vid = fx["id"]
        try:
            desc = graph("GET", vid, token, fields="description").get("description") or ""
            if fx["find"] not in desc:
                print(f"{vid}: already fixed (text not found), skipped")
                continue
            new = desc.replace(fx["find"], fx["replace"])
            if dry:
                print(f"{vid}: would change\n--- before\n{desc}\n--- after\n{new}\n")
                continue
            graph("POST", vid, token, description=new)
            check = graph("GET", vid, token, fields="description").get("description") or ""
            ok = fx["find"] not in check and fx["replace"] in check
            print(f"{vid}: {'fixed' if ok else 'NOT confirmed'}\n{check}\n")
            failed += 0 if ok else 1
        except GraphError as e:
            failed += 1
            print(f"::error::{vid}: {e}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
