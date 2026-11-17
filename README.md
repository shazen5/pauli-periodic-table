# The Pauli Principle and the Periodic Table

AI-Assisted Physics Simulation · Topic 8 — interactive website.

- `index.html`: the whole site (vanilla JavaScript and inline SVG, no build step in the browser)
- `assets/`: the video, its poster frame, the notebook figures and the `.ipynb`
- `_build/`: `template.html` and `build.py`. These copy the notebook text, code and outputs word for word into `index.html`.

## Updating the site

If you change the notebook text, copy the new `.ipynb` to `assets/Topic8_Pauli_Periodic_Table.ipynb` and rebuild:

```
python _build/build.py
```

If you change the page layout or simulations, edit `_build/template.html` and run the build again. Do not edit `index.html` directly, because the next build overwrites it.

Then publish:

```
git add .
git commit -m "update"
git push
```

GitHub Pages updates about a minute after the push.
