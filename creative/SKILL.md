---
name: creative
description: "Visual design studio — create posters, generative art, themed presentations, UI mockups, frontend designs, and brand-styled artifacts. Handles: 'create a poster', 'make generative art', 'apply theme', 'design a UI', 'brand guidelines', 'make a card', 'illustration', 'dark theme', 'light theme', 'style this'. ALWAYS invoke this skill for visual/design requests instead of individual creative skills."
argument-hint: "<what you want to create or design>"
allowed-tools:
  - Read
  - Bash
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
  - Skill
---

<objective>
Visual design dispatcher — route creative requests to the correct sub-skill.

Analyzes $ARGUMENTS and dispatches to canvas-design, algorithmic-art,
theme-factory, frontend-design, or brand-guidelines. Never does the work itself.
</objective>

<process>

<step name="route">
**Match intent to command.**

Evaluate `$ARGUMENTS` against these routing rules. Apply the **first matching** rule:

| If the text describes... | Route to |
|--------------------------|----------|
| Poster, card, illustration, "create an image", "make a visual" | `/canvas-design` |
| Generative art, p5.js, "algorithmic art", "creative coding" | `/algorithmic-art` |
| Theme, styling, "apply theme", "dark theme", "light theme", "color palette" | `/theme-factory` |
| Frontend design, "design a UI", "web interface", "distinctive frontend" | `/frontend-design` |
| Brand guidelines, "brand colors", "Anthropic style", "apply brand" | `/brand-guidelines` |

If ambiguous, ask via AskUserQuestion with top matches.
</step>

<step name="display">
**Show the routing decision.**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CREATIVE ► ROUTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:** {first 80 chars of $ARGUMENTS}
**Routing to:** {chosen command}
**Reason:** {one-line explanation}
```
</step>

<step name="dispatch">
**Invoke the chosen command.**

Use the Skill tool to invoke the selected creative skill, passing `$ARGUMENTS` as args.

After invoking the command, stop. The dispatched command handles everything from here.
</step>

</process>
