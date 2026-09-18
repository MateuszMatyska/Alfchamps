# In memory of Alfred

> This tool is built in loving memory of Alfred, our champion — and the best dog a human could ask for.
> Best friend, always by my side. Forever missed, never forgotten.
>
> — In memory of Alfred 🏆

## About this tribute

"Alfchamps" is named after **Alfred** (Alfred + champion). He was a beloved dog
and the inspiration for this project.

These memorial lines are **hardcoded** in the application and appear on the
cover of every generated PDF report and in the app footer. They are intentionally
**not** editable in the application — the only way to change them is through a
**pull request to this repository**.

## Where the lines live

The canonical, hardcoded tribute is defined in:

```
backend/app/memorial.py
```

- `ALFRED_TRIBUTE` — the main memorial paragraph shown on report covers.
- `ALFRED_TAGLINE` — the short tagline shown on the report cover and footer.
- `ALFRED_PHOTO_HINT` — hint text for where to drop Alfred's photo.
- `MEMORIAL_DEFAULT` — default value used when a project has no override.

There is **no** runtime setting that can change these defaults. If you ever need
to update the tribute, open a pull request that edits `backend/app/memorial.py`.

## Alfred's photo

The photo shown on the in-app **Memorial page** is `assets/alfred_photo.png`.
Drop a photo of Alfred there (see `assets/README.md`). The photo is **not**
included in generated PDF reports — the report cover shows only the Alfchamps
logo (`assets/alfchamps_logo.png`) and the memorial text.
