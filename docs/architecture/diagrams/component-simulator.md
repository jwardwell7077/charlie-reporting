# Component: SharePoint CSV Simulator

```mermaid
flowchart TB
  Client["Operator / Client"] -->|generate types, rows| Sim[[Simulator]]
  Sim -->|write CSV files| Output[(sharepoint_sim/)]
  Output -->|visible to| Collector[[Collector]]
```
