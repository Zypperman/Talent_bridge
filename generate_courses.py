import os, sqlite3, json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
db = sqlite3.connect(os.getenv("TALENTBRIDGE_DB_PATH", "/opt/talentbridge/data/talentbridge.db"))

_schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
db.executescript(open(_schema_path).read())

COURSES = [
    {
        "slug": "san-nas-fundamentals",
        "title": "SAN & NAS Fundamentals",
        "description": "Core storage networking concepts for data center operations."
    },
    {
        "slug": "data-center-networking",
        "title": "Data Center Networking",
        "description": "Networking fundamentals specific to data center environments."
    },
    {
        "slug": "cybersecurity-basics",
        "title": "Cybersecurity Basics",
        "description": "Foundational security concepts for tech operations roles."
    },
]

def generate_sections(course_title, course_description):
    prompt = f"""You are designing a technical training course for: "{course_title}"
Description: {course_description}

Design exactly 5-6 sections that take a learner from basic to advanced understanding of this topic, suitable for someone entering a data center / tech operations career.

Respond with ONLY valid JSON, no markdown fences, no other text, in this exact format:

{{
  "sections": [
    {{
      "section_number": "1.1",
      "title": "short section title",
      "content": "2-3 paragraphs of real, accurate technical teaching content for this section, written clearly for someone learning this for the first time, building on previous sections"
    }}
  ]
}}

Order sections from most foundational to most advanced. Each section's content should be substantial enough to teach the concept properly, but focused on ONE clear idea per section."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(raw)

INSERT_COURSE_SQL = "INSERT INTO courses (slug, title, description, display_order) VALUES (?, ?, ?, ?)"
INSERT_SECTION_SQL = "INSERT INTO sections (course_id, section_number, title, content, display_order) VALUES (?, ?, ?, ?, ?)"

for i, course in enumerate(COURSES):
    print(f"Generating: {course['title']}...")
    cursor = db.execute(INSERT_COURSE_SQL, (course["slug"], course["title"], course["description"], i))
    course_id = cursor.lastrowid

    result = generate_sections(course["title"], course["description"])
    for j, section in enumerate(result["sections"]):
        db.execute(INSERT_SECTION_SQL, (course_id, section["section_number"], section["title"], section["content"], j))
    db.commit()
    print(f"  -> {len(result['sections'])} sections created")

print("Done.")
