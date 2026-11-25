# Browser-only GitHub upload steps

## 1. Preserve the current site

If the repository already contains a published map, download a ZIP from **Code → Download ZIP** before replacing files. This gives you an easy backup.

## 2. Upload Version 1.2

1. Extract `european-captives-map-v1.2.zip` on your computer.
2. Open the extracted `european-captives-map-v1.2` folder.
3. Open the intended GitHub repository in your browser.
4. Choose **Add file → Upload files**.
5. Drag in the **contents** of the extracted folder, not the outer folder itself.
6. Confirm that `index.html` will be at the repository root and that the `data` and `scripts` folders are present.
7. Use a commit message such as `Publish European Captives Map v1.2`.
8. Select **Commit changes**.

If GitHub does not replace an older file automatically, open the old file, use the three-dot menu to delete it, commit that deletion, and then upload the new file with the same path.

## 3. Enable or confirm GitHub Pages

1. Open the repository's **Settings**.
2. In the left sidebar, choose **Pages** under **Code and automation**.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Choose the `main` branch and `/ (root)` folder.
5. Select **Save**.

No verified domain is required.

## 4. Confirm the deployment

1. Open the **Actions** tab.
2. Wait for the Pages deployment to show a green check.
3. Return to **Settings → Pages**.
4. Select **Visit site**.
5. Use a hard refresh if an older version appears: `Ctrl+Shift+R` on Windows or `Command+Shift+R` on Mac.

## 5. Review these acceptance checks

- The main title still says **European Captives**, and the smaller `Mediterranean Captivity Project · Version 1.1` heading is gone.
- No CARTO message, watermark, or API-key prompt appears.
- **How to use this map** opens the guide.
- The map options appear in this order: Both, Origins, Captivity, No Location Data.
- **No Location Data** keeps the map visible without markers and presents the searchable no-location record list.
- Documented connections are on at first load.
- The two time-slider handles have the same color and opacity.
- **Reset Filters** restores Both, documented connections, the full date range, and a blank search.
- Searching a known name still returns a record when the active option permits it.
- The historical record follows this order: Name, Place of Origin, Place of Captivity, Convert, Date, Ship Name, Source, Notes, and Record ID.
- The normalized-year/January 1 explanation appears only as a small note beneath Date in the historical record.
- Source and Notes display independently from their original CSV columns.
- **Download complete dataset (CSV)** downloads one complete 3,137-row CSV.
- No unknown-captivity marker appears in the Strait of Gibraltar.

## 6. Record the release

After review, create a GitHub release or tag named `v1.2` and note the publication date. Keep the Version 1.1 ZIP as the prior release archive.
