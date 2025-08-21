# Component: Excel / HTML Generator

```mermaid
flowchart TB
  Agg[[Aggregated Data]] --> Excel[["Excel/HTML Generator"]]
  Excel -->|writes| Workbook[(Workbook .xlsx)]
  Excel -->|writes| ReportHTML[(HTML Report)]
```
