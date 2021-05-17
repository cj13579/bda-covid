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

The daily press-releases and conferences are great and frustrating all at the same time. They tell you a lot of information but not, what I think, is the really useful and important stuff. This is an attempt to break down the numbers released into some more useful things:

* **Moving averages - **Data is noisy. Calculating simple moving averages gives us a much clearer view about where a data point is trending.
* **New metrics** - The Government have made decisions on positivity rate previously but they have only very recently started releasing this number. I have back dated the calculation to the beginning of th year.

## Disclaimer

This data is scraped (poorly) from [gov.bm](https://www.gov.bm) and I've not validated what's been collected. You should absolutely not use these numbers for anything important.

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
            valueDecimals: 2,
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
        valueDecimals: 2,
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