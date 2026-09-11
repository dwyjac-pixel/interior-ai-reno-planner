# Site source

`policy.md` is the privacy policy text. To republish after editing it:

```bash
python3 source/build_site.py source/policy.md .
git add -A && git commit -m "Update privacy policy" && git push
```

Bump the `EFFECTIVE` date in `build_site.py` when the policy changes.
