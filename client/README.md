On-Air Client
==========

This is the process that runs on human client machines, watching to see if the human has gone "On air."

TODO:

1. Guide for Launch Agent on Mac
2. Architecture wrt Toggles
3. Basic command usage

# Run as PLIST on Mac

`/Library/LaunchAgents/org.gengar.onair.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>org.gengar.onair</string>
	<key>RunAtLoad</key>
	<true/>
	<key>ProgramArguments</key>
	<array>
		<string>/Users/YOURUSER/.local/bin/pipenv</string>
		<string>run</string>
		<string>python</string>
		<string>watcher.py</string>
		<string>--toggle</string>
		<string>toggles.macos.zoom</string>
		<string>--push</string>
		<string>http://YOURSERVER/onair/api/v1/state</string>
	</array>
	<key>WorkingDirectory</key>
	<string>/Users/YOURUSER/git/onair/client</string>
	<key>KeepAlive</key>
	<true/>
	<key>StandardErrorPath</key>
	<string>/tmp/onair.err</string>
	<key>StandardOutPath</key>
	<string>/tmp/onair.out</string>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>
```

    sudo launchctl unload /Library/LaunchAgents/org.gengar.onair.plist
    sudo launchctl load   /Library/LaunchAgents/org.gengar.onair.plist
