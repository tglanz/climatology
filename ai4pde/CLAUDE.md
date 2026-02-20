# ai4pde - Project Guide

## Purpose

This project contains a presentation (`presentation.md`) surveying AI methods for solving PDEs.
The presentation targets potential Master's Thesis supervisors (a CS researcher and a computational physicist specializing in atmospheric dynamics).

## Presentation Style

- **Format**: Slide-like sections with short headers, bullet points, one key idea per section
- **Depth**: Shallow survey -- illustrate potential research topics, architectures, and applications without deep technical detail
- **Goal**: Show research directions, not teach methods

## Topics Covered

1. Traditional numerical methods (FDM/FEM/spectral) as motivation
2. Physics-Informed Neural Networks (PINNs)
3. Neural Operators (DeepONet, FNO, PINO)
4. Specific application example (to be provided by user)

## Content Rules

- **NEVER add content without asking first** -- the user provides all material and direction
- **NEVER invent or suggest research topics** -- only write what the user specifies
- **ASCII only** -- no emojis, no special Unicode characters
- **Math**: Use LaTeX notation with `$...$` (inline) and `$$...$$` (display blocks)
- **Diagrams**: Use Mermaid.js for architecture diagrams and flowcharts
- **Language**: English throughout
- **Citations**: Include references to papers when the user provides them

## File Structure

```
ai4pde/
  CLAUDE.md           # This file
  presentation.md     # The main presentation document
```

## Workflow

1. User describes what to add or change
2. Claude asks clarifying questions if needed
3. Claude implements the requested changes
4. User reviews and provides feedback
