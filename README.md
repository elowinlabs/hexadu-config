# Remote-config repo template

These files belong in a **SEPARATE GitHub repo** (e.g. `hexadu-config`) — not
inside the Hexadu app source repo. Cloudflare Pages connects to that repo
and serves `config.json` over HTTPS at a public URL; the app fetches that
URL read-only.

> The split is deliberate: Cloudflare Pages deploys a whole repo, so we
> don't want the app's private source code tied to a public-facing web
> deployment. A small dedicated repo holding just this content is the
> clean separation.

## Standup checklist

1. **Create a new GitHub repo** — `hexadu-config` (private recommended).
2. **Copy the files in this folder into the repo root**, preserving the
   `.github/workflows/` layout:
   ```
   hexadu-config/
     config.json
     validate_config.py
     .github/workflows/validate-config.yml
   ```
3. **Push to GitHub.** The validator Action should run on the first
   commit (or PR) and turn green.
4. **Cloudflare Pages → Workers & Pages → Create → Pages → Connect to
   Git** → select the new repo. Framework preset: **None**. No build
   command. Build output directory: repo root. Deploy.
5. Cloudflare hands back a URL like
   `https://hexadu-config.pages.dev/config.json` — paste that into the
   app's [`ServiceConfig.remoteConfigURL`](../../Hexadu/Services/ServiceConfig.swift)
   constant and ship a build.
6. **Branch protection** — GitHub → Settings → Branches → Add ruleset
   for `main`. Require status checks (select `validate`) and require a
   PR before merging. Now every config change runs validation before
   it can deploy.

## Verifying it's live

```bash
curl -s https://hexadu-config.pages.dev/config.json
```

You should see the JSON. Apps pick up new values on their next launch
(see the `refresh()` flow in
[`LiveRemoteConfigService`](../../Hexadu/Services/RemoteConfig.swift)).

## When you add a new flag

Order matters — do all three in this sequence:

1. Add the property to the `RemoteConfig` Swift model **with a value
   in `safeDefault`** and ship a build.
2. Add the key + type to `SCHEMA` in `validate_config.py` in this
   repo.
3. *Only then* start setting the key in `config.json`.

The validator is intentionally strict about unexpected keys to prevent
adding a flag to the JSON before the model knows about it (which would
mean older shipped builds silently ignore it AND newer ones fail
validation).

## Day-to-day operating

See the full runbook in the app repo at
`docs/architecture/03-admin-operations-guide.md` — covers GitHub web
UI vs CLI workflows, Cloudflare rollback, TelemetryDeck dashboards,
and free-tier limits.
