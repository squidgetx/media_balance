library(tidyverse)

df.agg <- read_tsv('nyt-summary-data.tsv')
df.agg %>%
    ggplot(aes(x = year)) +
    geom_bar(aes(y=n_articles), fill='cyan3', stat = "identity") +
    geom_line(aes(y=sources_per*100), size=1.1)  + 
    scale_y_continuous(
        name = "Num Articles",
        breaks=seq(0,1251,250),
        
        sec.axis = sec_axis(~.*0.01, name="Sources per Article" )
    ) + 
    scale_x_continuous(breaks=c(2012, 2016, 2020)) + 
    theme_bw() + 
    theme(
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
    ) + labs(
        x='Year',
        title='Extracted Sources (New York Times Climate Change Articles)'
    )
ggsave('nyt-summary.png', width=6, height=5)


