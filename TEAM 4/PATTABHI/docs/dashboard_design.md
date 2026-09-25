# QuickSight Dashboard Design

## Dataset

Use Athena view `vw_executive_kpis` for trend and regional visuals, supplemented by direct curated tables for model/dealer rankings. Import to SPICE after validating row counts and freshness. Expose `region`, `dealer_id`, `model`, and date fields as controls.

## Layout

Top row: Revenue, Sales, Vehicles, Average Battery, Critical Faults, Warranty Cost, Service Volume KPI cards. Middle: revenue trend, sales trend, warranty trend, and service volume trend. Bottom: revenue by region, faults by region, warranty cost by region, top models, and top dealers.

## Interactions

Filters: region, dealer, model, and date range. Drill hierarchy is BMW > Region > Dealer > Model. Selecting a region cross-filters all visuals. Tooltips include current period, prior period, and variance where available.

## RLS

Create a QuickSight dataset rules table with `UserName` and `region`:

| UserName | region |
|---|---|
| south.manager | South |
| north.manager | North |
| east.manager | East |
| west.manager | West |

Executives use a separate unrestricted group. Test with an account from each group and verify both direct table access and visual results.

## Visual acceptance checks

KPI totals reconcile to Athena; no visual includes duplicate joins; zero-data filters render clearly; date controls use one canonical date; currency and percentages are formatted; last refresh timestamp is visible; dashboard opens in under the agreed SPICE performance target.
