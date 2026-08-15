# One-time setup

Follow these once to get the blog live at **ed25519.io**. After that, every
`git push` to `main` deploys automatically.

## 1. Push this repo to GitHub

Create a new repository on GitHub (any name works — e.g. `ed25519.io`), then:

```bash
git add .
git commit -m "Initial blog"
git branch -M main
git remote add origin git@github.com:<your-username>/<repo>.git
git push -u origin main
```

## 2. Turn on GitHub Pages

In the repo on GitHub: **Settings → Pages**.

- Under **Build and deployment → Source**, select **GitHub Actions**.

That's it — the workflow in `.github/workflows/deploy.yml` will build and deploy.
Watch the first run under the **Actions** tab.

## 3. Add the custom domain in GitHub

Still in **Settings → Pages**, under **Custom domain**, enter:

```
ed25519.io
```

Click **Save**. (This repo already ships a `public/CNAME` file with the same
value, so the setting persists across deploys.)

## 4. Point the domain's DNS at GitHub

Do this at whoever you buy `ed25519.io` from (the domain registrar / DNS
provider). You're configuring an **apex domain** (no `www`), so add these
records:

**A records** — host/name `@` (or blank), pointing to each of:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

**AAAA records** (IPv6) — host/name `@`, pointing to each of:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

**Optional — redirect `www` to the apex.** Add a **CNAME** record:

```
Host:  www
Value: <your-username>.github.io
```

DNS can take anywhere from a few minutes to a few hours to propagate.

## 5. Enable HTTPS

Back in **Settings → Pages**, once GitHub verifies the domain, tick
**Enforce HTTPS**. (The certificate may take a little while to become available
after DNS resolves.)

---

### Verifying DNS

```bash
dig +short ed25519.io          # should list the four 185.199.x.x addresses
dig +short www.ed25519.io      # should show <your-username>.github.io
```

### If you ever change the domain

Update it in three places: `public/CNAME`, the `site` field in
`astro.config.mjs`, and **Settings → Pages → Custom domain**.
