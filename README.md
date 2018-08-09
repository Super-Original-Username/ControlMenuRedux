# ControlMenuRedux

This is a program for the University of Montana/Montana Space Grant Consortium BOREALIS project. 
It reads in tracking data for an NAL Research Iridium modem, as well as gives methods for sending cutdown commands
and commands for other features to be implemented at a later date

<h2>Required python modules:</h2>
<ul>
<li>PyQt5</li>
<li>mysqlclient</li>
</ul>

Note: You may need to use another gmail address if the program has trouble logging in. There have been issues in the past with 2fA when our accounts get used from too many machines
This program is also designed for python3


<h2>How to use this program:<\h2>
  <ol>
    <li>Take the Iridium IMEI for your modem, found on eclipse.rc.montana.edu, and paste it into the 'Iridium IMEI' box in the GUI.<\li>
    <li>Click the 'Start tracking' button.<\li>
    <li>Click the 'Send idle command' button before turning on your arduino<\li>
    <li>Before sending the cutdown command, make sure that the table to the left of the buttons has populated with location data<\li>
    <li>When ready, click the 'Send cutdown command button<\li>



