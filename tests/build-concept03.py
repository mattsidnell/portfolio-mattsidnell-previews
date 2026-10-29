#!/usr/bin/env python3
"""Build faithful colourways from the dark, photo-and-code-panel Concept 03 reference.

All three variants preserve the dark Concept 03 composition:
big left headline, portrait/workspace + code UI on the right, expertise strip,
four REAL website screenshots in a row, then further genuine work.
"""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
docs=root/"docs"
template=(root/"tests"/"concept03-reference.html").read_text()
variants=[
  ("dark","Midnight Cyan","Original dark concept","Dark navy, electric cyan and tiny yellow flourishes. Closest to the Concept 03 image you selected."),
  ("cyan","Clean Cyan","Bright, technical and clear","The identical layout on a lighter white, navy and cyan palette."),
  ("yellow","Yellow Accent","Confident with warmth","The same layout with cyan plus more noticeable yellow details for creative energy.")
]
for key,name,tag,description in variants:
    dest=docs/f"concept03-{key}"
    dest.mkdir(parents=True,exist_ok=True)
    html=template.replace("__THEME__",key).replace("__VARIANT__",name)
    (dest/"index.html").write_text(html)
    print(f"Generated {dest.relative_to(root)}")
data={
 "project":"Matt Sidnell — Concept 03",
 "category":"Personal developer portfolio — design comparison",
 "title":"The real Concept 03. Three colour options.",
 "summary":"This is the layout you selected: bold headline, dark technical code panel, casual portrait treatment and a row of four real website screenshots. Compare exactly the same structure in three colours, starting with the original dark navy/cyan direction.",
 "notice":"Design review only. The hero shows Matt's genuine face in an illustrated casual hoodie composite, not a real hoodie photograph. The website screenshots are real. The Lyneham Flying Club and Pixlwrk examples come from local builds, clearly marked. No changes have been made to mattsidnell.co.uk.",
 "concepts":[
 {"name":name,"tag":tag,"description":description,"image":f"../assets/previews/concept03-{key}.jpg","url":f"../concept03-{key}/"}
 for key,name,tag,description in variants
 ]
}
(docs/"concept03"/"selector.json").write_text(json.dumps(data,indent=2)+"\n")
