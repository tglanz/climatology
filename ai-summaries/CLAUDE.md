# Paper Summary Instructions

## Purpose

This document provides guidelines for creating comprehensive summaries of academic papers in the field of climatology, machine learning, and numerical systems.

## Output Requirements

### File Format
- Output filename: `<paper-title-slug>.md`
- Plain text markdown format only
- NO special characters, emojis, or Unicode symbols
- Use ASCII characters exclusively
- Mathematical notation: Use LaTeX syntax (e.g., `\alpha`, `\sum_{i=1}^{n}`)

### Required Sections

1. **Title and Metadata**
   - Paper title
   - Authors
   - Publication venue and year
   - Brief summary paragraph

2. **Key Contributions**
   - Main findings and innovations
   - Bullet point format for clarity

3. **Methodology**
   - Problem setup and formulation
   - Approach and techniques used
   - Architecture details (for ML papers)
   - Training strategy (for ML papers)

4. **Results**
   - Quantitative and qualitative findings
   - Comparisons with baselines
   - Key performance metrics

5. **Physical/Theoretical Implications**
   - What the results mean for understanding the underlying physics
   - Connections to existing theory
   - Practical applications

6. **Limitations and Future Work**
   - Known limitations of the approach
   - Suggested directions for future research

7. **Physics Glossary**
   - **Format**: Term name in bold, followed by definition
   - **Content**: All physics/technical terms used in the paper
   - **Structure for each term**:
     - Formal, concise definition
     - Mathematical formulation when applicable
     - Simple example demonstrating the concept
   - Terms should be ordered by relevance to the paper

8. **Knowledge Verification Quiz**
   - 20-25 questions covering main concepts
   - Questions ordered by relevance/importance in paper
   - Each question includes:
     - Clear question statement
     - Reference to relevant paper sections
     - Concise answer (2-4 sentences)
   - Purpose: Help readers verify their understanding

### Diagram Requirements

- Use Mermaid.js for complex diagrams (workflows, architectures, sequences)
- Validate all Mermaid diagrams for correctness
- Alternative: Use simple ASCII text-based diagrams for basic structures
- NO hand-drawn or image-based diagrams

### Style Guidelines

- **Clarity**: Write for technical readers familiar with the domain
- **Conciseness**: Avoid unnecessary verbosity
- **Precision**: Use exact terminology from the paper
- **Structure**: Use hierarchical headings (##, ###) appropriately
- **Emphasis**: Use bold for important terms on first use
- **Lists**: Use bullet points for multiple related items
- **Code blocks**: Use for equations, algorithms, or technical notation

### Mathematical Notation

- Inline math: Use standard notation (e.g., Re = 25,000)
- Complex equations: Present on separate lines
- Variables: Define clearly when first introduced
- Subscripts/superscripts: Use standard text formatting (e.g., u-bar, k^2)

### Physics Glossary Best Practices

Each glossary entry should follow this template:

```
**Term Name**: [One sentence formal definition]. [Mathematical formulation if applicable]. [Physical interpretation]. [Simple example or application].
```

Example:
```
**Reynolds Number (Re)**: Dimensionless number measuring the ratio of inertial forces to viscous forces in a fluid flow. Re = UL/nu where U is characteristic velocity, L is characteristic length, and nu is kinematic viscosity. High Re indicates turbulent flow where inertial forces dominate. Example: Water flowing through a pipe at high speed has high Re and exhibits turbulent, chaotic motion.
```

### Quiz Question Best Practices

Each quiz question should follow this template:

```
**Q#: [Clear, specific question]**
Reference: [Section numbers or figure numbers from paper]
Answer: [Concise 2-4 sentence answer covering key points]
```

Questions should:
- Progress from fundamental to advanced concepts
- Test understanding, not just memorization
- Include questions about methodology, results, and implications
- Reference specific locations in the paper where concepts are discussed

## Process

1. **Read** the entire paper thoroughly
2. **Identify** key contributions, methodology, and results
3. **Extract** all technical terms for glossary
4. **Create** summary following the section structure above
5. **Develop** quiz questions that test understanding
6. **Validate** any diagrams for correctness
7. **Review** for completeness and accuracy

## Quality Checklist

- [ ] All required sections present
- [ ] NO special characters or emojis used
- [ ] Physics glossary contains all relevant terms
- [ ] Each glossary term has definition, formulation, and example
- [ ] Quiz has 20-25 questions with references and answers
- [ ] Mermaid diagrams validated (if used)
- [ ] Mathematical notation is clear and consistent
- [ ] File follows naming convention
- [ ] Content is technically accurate
- [ ] Summary is comprehensive yet concise

## Notes

- These summaries are meant to serve as study aids and reference materials
- Focus on making complex concepts accessible while maintaining technical rigor
- The glossary and quiz are particularly important for learning and retention
- When in doubt about a technical detail, refer back to the original paper
