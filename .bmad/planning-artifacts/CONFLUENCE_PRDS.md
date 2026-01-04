# Confluence PRD Sources

## Nexus UI Uplift PRDs

The following Confluence pages contain the PRD documentation for this project:

### Main Page
- **URL**: https://armor-defense.atlassian.net/wiki/spaces/PDM/pages/5015044104/Nexus+UI+Uplift
- **Space**: PDM (Product Management)
- **Page ID**: 5015044104

## How to Import PRDs

### Using Atlassian MCP Server

The project is configured with the Atlassian MCP server. To fetch PRD content:

1. Ensure you're authenticated with Atlassian (the MCP server handles SSE auth)
2. Use the MCP tools to fetch page content
3. Save extracted content to `.bmad/planning-artifacts/prd.md`

### Manual Import

If MCP is not available:

1. Navigate to the Confluence page
2. Export as Word or PDF
3. Convert to Markdown
4. Save to `.bmad/planning-artifacts/prd.md`

## PRD Structure

Once imported, PRDs should follow this structure:

```
.bmad/planning-artifacts/
├── prd.md                    # Main PRD document
├── architecture.md           # Technical architecture
├── epics.md                  # Epic breakdown
└── ux-design.md              # UX specifications
```

## Status

- [ ] Main PRD imported
- [ ] Architecture documented
- [ ] Epics created
- [ ] Stories generated
