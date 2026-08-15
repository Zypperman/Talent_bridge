**Talent Bridge — Hackathon Pitch Preparation** 

**THE PITCH** 

**Opening (hook — start here)**

“Batam's data center boom is creating real technical jobs — but most of Batam's current tech workforce is in operational roles, not the specialized engineering roles this boom needs. The skills gap is real. The question is: how do you close it fast, and how does an employer actually trust that someone is ready?” 

**The problem (be sharp, not long)** 

“Today, if someone wants to upskill, they go to YouTube, Udemy, Coursera, Pluralsight. These platforms have real experts creating real content — that's not the problem. The problem is what happens after the content: a multiple-choice quiz at the end, and a 'Certificate of Completion.' That certificate proves you watched the videos. It doesn't prove you understand the material. And when an employer sees that certificate, they have no real way to know the difference.” 

**The solution** 

“Talent Bridge closes that gap with one core idea: **learning through real conversation, not content consumption.** 

AI drafts each course — I personally review and validate every course for technical accuracy before it reaches a learner, since I have real hands-on experience in this domain myself. 

Each course is broken into sequential sections — 1.1, 1.2, 1.3 — each one building on the last. A learner can't skip ahead. To move from 1.1 to 1.2, they have to have a real conversation with an AI instructor, explain the concept back in their own words, and demonstrate they actually understood it — not just clicked through it. 

While that conversation happens, Talent Bridge is transparently evaluating three things: how quickly they reached real understanding, how well they explained it back, and how sharp their own questions were. The learner knows this is happening — it's not hidden. That evaluation is exactly what gets shown to employers. 

A credential only gets issued once every section of a course is genuinely completed. So when an employer sees a Talent Bridge credential, they're not looking at a certificate — they're looking at evidence.” 

**How the employer side works** 

“Employers post a job, list the required course credentials, and instantly see every candidate whose verified understanding matches — not a resume claim, actual demonstrated competence, backed by a real transcript.” 

**Closing (end here)**  
“This isn't about replacing human trainers. It's about giving Batam's workforce a fast, honest way to prove they're ready for these new roles — and giving employers, whether in Batam or across the strait in Singapore, a reason to actually trust that signal.” 

**PRODUCT STACK — WHAT AND WHY**

| Layer  | Technology  | Why this choice |
| :---- | :---- | :---- |
| **Backend**  | Python \+ FastAPI  | Fast to build, handles every API call — routes each learner's message to Claude and back |
| **AI Engine**  | Anthropic Claude API  | Powers three things: (1) Socratic teaching of each section, (2) post-conversation evaluation on  speed/explanation/question-sharpness, (3) initial course content drafting (human-reviewed after) |
| **Database**  | SQLite  | Single lightweight file, no separate database server — simple and reliable at this scale |
| **Frontend**  | Plain  HTML/CSS/JavaScript | No build tools, no framework — one file that loads instantly and has nothing to break live during a demo |
| **Hosting**  | Self-managed Linux  server,  systemd-managed  process | Runs permanently, auto-restarts if it ever crashes, independent of my own machine being on |
| **Architecture**  | Fully independent,  isolated application | Not bolted onto any existing product — own database, own server process, built specifically for this problem |

**TOUGH FOLLOW-UP QUESTIONS — PREPARED ANSWERS** 

**Q: How do you know the AI-generated course content is actually accurate?** “AI drafts it, but I personally review and validate every course before it goes live — I have real hands-on experience in this domain, so I'm not blindly trusting AI output. It's AI-assisted authoring with human expert validation, not fully autonomous content.” 

**Q: Isn't it a privacy concern that you're evaluating and scoring users?** 

“No — it's fully transparent. The learner knows from the moment they sign up that their learning conversations are being evaluated, and that this evaluation is what employers will see. There's nothing hidden. That transparency is actually part of the trust mechanism.” 

**Q: How is this different from a technical interview or a coding test like HackerRank?** “Those test isolated problem-solving under pressure, in one sitting. Talent Bridge measures genuine understanding built progressively, over a real learning journey — arguably a more honest signal of whether someone actually knows the material, not just how they perform under exam conditions.” 

**Q: Walk me through the matching algorithm.** 

“It's straightforward and intentional: an employer lists which course credentials a role requires, and the system shows every candidate who has genuinely earned those credentials — meaning they completed every section with confirmed understanding. It's not a black-box ranking algorithm; it's built on real, verified prerequisites, which is exactly what makes it trustworthy.” 

**Q: How would this scale if thousands of people used it?** 

“The architecture doesn't need to change — every conversation is already an independent API call, so it scales horizontally. The real cost driver is AI API usage, which scales with real usage, not fixed infrastructure. That's the honest, given tradeoff of an AI-native product, but it means I only pay for real, active learners.” 

**Q: Why not just use an existing platform or framework instead of building this from scratch?** “Existing platforms like Udemy prove content consumption, not understanding — that's the exact gap this project exists to close, so building on top of them wouldn't solve the problem. On the technical side, I used direct API calls rather than a heavier framework because it gave me precise control over how the teaching and evaluation prompts work, without unnecessary complexity for this stage.” 

**Q: What happens if the AI evaluation is wrong or unfair to a learner?** 

“Right now, evaluation is evidence-based — every score is backed by a specific quote from what the learner actually said, not just a number. That's a deliberate design choice: an employer, or the learner themselves, could later review the actual evidence, not just trust a black-box score. A production version would add a human review/appeal path on top of that same evidence log.” 

**Q: Is this only for Batam, or could it scale beyond this hackathon?** 

“The mechanism doesn't depend on Batam specifically — the courses and skills could be swapped for any field. Batam's data-center boom is the immediate, real problem I designed the first version around, but the underlying idea — proving real understanding instead of content consumption — applies  
anywhere there's a skills-gap-to-hiring problem.”  
**DELIVERY NOTES** 

• Keep the “problem” section short and sharp — the “completion vs. understanding” line is your strongest single sentence, don't bury it 

• If you get a demo slot: **show**, don't describe, a live conversation catching a real misconception — much more convincing than explaining it 

• Say “I reviewed and validated the content” with confidence — this is a genuine strength, not something to downplay 

• If a question surprises you and you don't have a clean answer, it's fine to say: “That's a great question — for this MVP, here's the honest current state...” — panels respect honesty over overselling

