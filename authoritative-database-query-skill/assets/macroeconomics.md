# Statistics and Macroeconomics

## Use Cases
- Retrieve and download time series for national and regional economic indicators
- Record indicator codes and units, and provide verifiable source links

## Common Methods
- API first: use official interfaces to obtain structured time-series data
- GUI fallback: use when visualization, downloads, or page filtering is needed

## GUI Guidance
- Search the official website by indicator name and country or region
- Use page filters to set the time range and frequency
- Download or copy the latest value, unit, and indicator code

## API and Programmatic Access
- World Bank API: `country/{code}/indicator/{indicator}`
- FRED API: `series/observations` (API key required)
- OECD/IMF SDMX APIs: query by dataset and dimension

## Authoritative Sources and URLs
- World Bank Data: https://data.worldbank.org / API: http://api.worldbank.org
- FRED: https://fred.stlouisfed.org / API: https://api.stlouisfed.org
- OECD Data: https://data.oecd.org / SDMX: https://stats.oecd.org/sdmx-json
- IMF Data: https://www.imf.org/en/Data / SDMX: https://sdmx.imf.org
- UNData: https://data.un.org

## Example Task
- Retrieve Germany's unemployment rate for the past ten years and return the time series, indicator code, and source link
