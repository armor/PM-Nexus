# Excalidraw Diagrams - Nexus UI Platform

This directory contains visual diagrams created with Excalidraw for presentations, documentation, and collaborative design sessions.

## Diagram Index

### 1. [System Architecture](./01-system-architecture.excalidraw)
**Purpose:** Visual representation of the full platform architecture for presentations and documentation

**Format:** Excalidraw native format (JSON-based, editable)

**Content:**
- Client layer (browsers, MCP clients)
- CDN and edge services
- Kubernetes cluster with all services
- Data layer (databases, caches)
- External integrations

**Use Cases:**
- Executive presentations
- Architecture review meetings
- Onboarding documentation
- External stakeholder communication

---

## Working with Excalidraw Files

### Opening Files

1. **Excalidraw.com:** Open https://excalidraw.com and drag the `.excalidraw` file onto the canvas
2. **VS Code:** Install the "Excalidraw" extension by Pomdtr
3. **Obsidian:** Use the Excalidraw plugin
4. **Figma:** Import using Excalidraw plugin

### Exporting

```bash
# Convert to SVG using the conversion script
node scripts/excalidraw-to-svg.mjs .bmad/diagrams/excalidraw/01-system-architecture.excalidraw

# Or use npx directly
npx @excalidraw/cli export 01-system-architecture.excalidraw --format svg
```

### Export Formats

| Format | Use Case |
|--------|----------|
| SVG | Documentation, web embedding |
| PNG | Presentations, static docs |
| PDF | Print materials |
| Excalidraw | Collaborative editing |

---

## Design Guidelines

### Visual Style

| Element | Style |
|---------|-------|
| Boxes | Rounded corners, pastel fills |
| Arrows | Hand-drawn style, labeled |
| Text | Clear, readable, consistent sizing |
| Colors | Category-based (see color scheme) |

### Color Scheme

| Category | Color | Hex |
|----------|-------|-----|
| Frontend | Light Blue | #61DAFB |
| API Services | Light Green | #68D391 |
| Data Layer | Orange | #F6AD55 |
| External | Purple | #B794F4 |
| MCP Services | Pink | #F687B3 |
| Security | Red | #FC8181 |

### Naming Convention

```
{order}-{name}.excalidraw
```

Examples:
- `01-system-architecture.excalidraw`
- `02-data-flow-overview.excalidraw`
- `03-deployment-topology.excalidraw`

---

## Conversion to Other Formats

### Mermaid Equivalent

Each Excalidraw diagram should have a corresponding Mermaid version in the appropriate category folder:

| Excalidraw | Mermaid Equivalent |
|------------|-------------------|
| `excalidraw/01-system-architecture.excalidraw` | `architecture/01-system-architecture.md` |

### When to Use Each Format

| Format | Best For |
|--------|----------|
| Excalidraw | Visual design, presentations, whiteboarding |
| Mermaid | Documentation, version control, automated rendering |
| SVG Export | Static embedding in docs |

---

## Planned Diagrams

| Diagram | Priority | Status |
|---------|----------|--------|
| 02-data-flow-overview | HIGH | Planned |
| 03-deployment-topology | MEDIUM | Planned |
| 04-mcp-integration | HIGH | Planned |
| 05-security-model | HIGH | Planned |

---

## Related Diagrams

| Category | Diagram | Relationship |
|----------|---------|--------------|
| Architecture | [System Architecture (Mermaid)](../architecture/01-system-architecture.md) | Text version of same diagram |
| Data Flows | [All Data Flows](../data-flows/README.md) | Detail flows shown in overview |

---

## Related Documentation

- [Design System](../../planning-artifacts/10-design-system.md) - Visual design guidelines
- [Architecture Document](../../planning-artifacts/nexus-architecture-document.md) - Architecture decisions

---

Last Updated: 2026-01-04
Maintained By: Architecture Team
