from pathlib import Path

p = Path("src/dashboard.py")
text = p.read_text(encoding="utf-8")

text = text.replace("use_container_width=True", 'width="stretch"')
text = text.replace("use_container_width=False", 'width="content"')

p.write_text(text, encoding="utf-8")
print("✅ Updated Streamlit width arguments in src/dashboard.py")