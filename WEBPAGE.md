---
title: Bermuda COVID-19 Statistics
---
<script src="https://code.highcharts.com/highcharts.js">
</script>
<script src="https://code.highcharts.com/modules/exporting.js">
</script>
<script src="https://code.highcharts.com/modules/export-data.js">
</script>
<script src="https://code.highcharts.com/modules/accessibility.js">
</script>
<script src="https://code.highcharts.com/modules/data.js">
</script>
# Bermuda COVID-19 Statistics

## Key statistics

**LAST_WEEK_CASES_PER_100K** cases per 100,000 people in the week WEEK_FROM - WEEK_TO.

**LAST_WEEK_CASES** cases in the week WEEK_FROM - WEEK_TO.

**DIFF** compared with the previous week.

**CASES_YEAR_TO_DATE** total cases in 2021.

## Why?

The daily press-releases and conferences are great and frustrating all at the same time. They provide useful metrics but not the same numbers as are reported by the likes of the BBC which make comparing the situation in Bermuda to other countries more difficult. This site is an attempt to solve that problem.

## Disclaimer

This data is scraped (poorly) from [gov.bm](https://www.gov.bm) and I have not validated what has been collected. I have only collected data from the start of 2021. You should absolutely not use these numbers for anything important.

### Positivity Rate

<figure class="highcharts-figure">
    <div id="posRateContainer"></div>
</figure>
On May 12, 2020 the World Health Organization (WHO) advised governments that before reopening, rates of positivity in testing (ie, out of all tests conducted, how many came back positive for COVID-19) of should remain at 5% or lower for at least 14 days. The vertical red line on this chart represents 14 days ago from today.

### New positive cases

<figure class="highcharts-figure">
    <div id="newPositiveCasesContainer"></div>
</figure>

### Active cases

<figure class="highcharts-figure">
    <div id="activeCasesContainer"></div>
</figure>
<script>
var fortnightAgo = new Date(Date.now() - 12096e5);
posRateOptions = {
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Bermuda COVID-19 Positivity Rate'
        },
        tooltip: {
            valueDecimals: 2,
            shared: true,
            split: false
        },
        subtitle: {
            text: "Daily and 14 day rolling average of Bermuda's COVID-19 positivity rates."
        },
        data: {
            csvURL: 'https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/positivity_rate.csv',
        },
        xAxis: {
            plotLines: [{
                color: '#FF0000',
                width: 2,
                value: fortnightAgo
            }]
        }
    }
    newPositiveCasesOptions = {
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Bermuda COVID-19 new positive cases'
        },
        tooltip: {
            valueDecimals: 0,
            shared: true,
            split: false
        },
    subtitle: {
        text: "Daily and 7 day rolling average of Bermuda's COVID-19 new positive cases."
    },
    data: {
        csvURL: 'https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/positive_cases.csv',
    }
}
activeCasesOptions = {
    chart: {
        type: 'spline'
    },
    title: {
        text: 'Bermuda COVID-19 Active Cases'
    },
    tooltip: {
        valueDecimals: 0,
        shared: true,
        split: false
    },
    subtitle: {
        text: "Daily and 7 day rolling average of Bermuda's COVID-19 active COVID-19 cases."
    },
    data: {
        csvURL: 'https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/active_cases.csv',
    }
}
Highcharts.chart('posRateContainer', posRateOptions);
Highcharts.chart('activeCasesContainer', activeCasesOptions);
Highcharts.chart('newPositiveCasesContainer', newPositiveCasesOptions);
</script>