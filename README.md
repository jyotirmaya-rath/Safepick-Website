# SafePick website (safepick.app)

The company website for SafePick Corporation: 22 pages, plain files, no database.

| Folder / file | What it is |
| --- | --- |
| `site/` | **The website.** This is the folder that gets published. |
| `Preview SafePick website.command` | Double-click to see the site on this Mac at http://localhost:8080. |
| `build/` | The sources the site is made from. Only needed to change the site. |

## See it

Double-click **Preview SafePick website.command**. Close the Terminal window to stop.

## Change it

- **Store links on launch day:** open `build/static/assets/js/site.js`, paste the App Store and Google Play addresses, then rebuild. Every "Coming soon" button becomes a download button.
- **Company name, e-mail addresses, legal date:** the `CONFIG` block at the top of `build/build.py`.
- **Words on a page:** `build/pages/` (one file per page; blog articles start with `blog-`).
- **Rebuild:** in Terminal, `python3 build/build.py` from this folder. It rewrites `site/` and checks every link and picture.

## Put it online

1. Create these three addresses for the safepick.app domain (Namecheap: Domain List, Manage, Email Forwarding) and forward them to an inbox you read: `support@`, `partners@`, `privacy@`. The site and the privacy policy publish them.
2. Upload the **contents of `site/`** to a static web host (GitHub Pages, Cloudflare Pages and Netlify are free). `.app` addresses only work over HTTPS, which these hosts switch on for you.
3. In the host, add `safepick.app` as a custom domain and copy the DNS records it gives you into Namecheap (Domain List, Manage, Advanced DNS).
4. Open https://safepick.app and click through the menu.

## Before it goes live, confirm

- The company's legal name (`SafePick Corporation`) and province (British Columbia). They appear in the footer, privacy policy and terms.
- The founders' profiles on the Founders page.
- That a lawyer has read the privacy policy and terms. They describe what the app does today; if the app changes, update them.
