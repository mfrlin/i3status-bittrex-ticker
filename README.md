# i3status-bittrex-ticker

Displays prices of coins on i3bar (default status bar on [i3 window manager](https://i3wm.org)) if you are using i3status (default).

# Installation

1. Clone this repository (for example in `/opt/i3status-bittrex-ticker`)

2. Configure i3status. [This](https://i3wm.org/i3status/manpage.html#_options) will help you find location of the config file. Mine is at `/etc/i3status.conf`. Make sure you have `output_format = "i3bar"` line in  `general` section.

3. Configure i3 (`~/.config/i3/config`). At the bottom of the file in the `bar` section change `status_command` line to `status_command i3status | /opt/i3status-bittrex-ticker/i3status_wrapper.py`. This will pipe i3status output into our script where we inject coin prices.

4. Copy `example-conf.ini` to `conf.ini`. Edit `conf.ini` to your liking.

# Configuration

In configuration each market pair you want to be displayed is its own section (for example `[USDT-BTC]`).

Each section can have following options (all of them are optional):
- `decimal_points` Number of decimal points you want to see. If not specified all of them will be displayed as returned by Bittrex.
- `limit` If you specify a limit the price will be compared to a limit. If price is higher than limit it will be displayed in green color alongside with the limit and if not the color will be red. If no limit is specified only the price is displayed in white.
- `display_dollars` This will convert prices to dollars. Coins on BTC market (for example BTC-XRP) will be converted by BTC price on USDT-BTC market. Coins on ETH market (ETH-NEO) will be converted by ETH price on USDT-ETH market. Option has no effect on USDT-* markets as they are already displayed in dollars.

